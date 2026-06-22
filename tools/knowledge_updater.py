# -*- coding: utf-8 -*-
"""knowledge_updater.py — production-grade self-improving knowledge pipeline."""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import logging
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable, List, Optional, Sequence, Set

DEFAULT_BRAIN = Path(__file__).resolve().parent.parent / "SECOND-KNOWLEDGE-BRAIN.md"
DEFAULT_CONFIG = Path(__file__).resolve().parent / "knowledge_updater.json"

ARXIV_CATEGORIES = ["cond-mat.mtrl-sci", "physics.app-ph"]
SEARCH_QUERIES = [
    "additive manufacturing process parameter optimization",
    "FDM layer adhesion anisotropy",
    "support structure generation overhang",
    "design for additive manufacturing DfAM",
]
DOMAINS = ["astm.org", "iso.org", "all3dp.com"]
KEYWORDS = sorted({w.lower() for q in SEARCH_QUERIES for w in q.split()})

MAX_RETRIES = 3
BACKOFF_SECONDS = 2.0
REQUEST_TIMEOUT = 30
MAX_AGE_DAYS = 730

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("knowledge_updater")


@dataclass(frozen=True)
class Entry:
    """A single knowledge entry destined for the brain."""
    title: str
    authors: str
    date: str
    url: str
    abstract: str
    source: str = "arXiv"
    score: float = 0.0
    venue: str = "-"
    doi: str = "-"

    def hash(self):
        key = self.doi if self.doi and self.doi != "-" else self.url
        if not key or key == "-":
            key = f"{self.title}::{self.authors}"
        return hashlib.sha1(key.encode("utf-8", "ignore")).hexdigest()[:12]

    def year(self):
        return self.date[:4] if self.date and len(self.date) >= 4 else "-"


@dataclass
class Config:
    """Runtime configuration."""
    brain: Path = DEFAULT_BRAIN
    arxiv_categories: List[str] = field(default_factory=lambda: ARXIV_CATEGORIES.copy())
    search_queries: List[str] = field(default_factory=lambda: SEARCH_QUERIES.copy())
    domains: List[str] = field(default_factory=lambda: DOMAINS.copy())
    keywords: List[str] = field(default_factory=lambda: KEYWORDS.copy())
    max_results: int = 15
    max_age_days: int = MAX_AGE_DAYS
    dry_run: bool = False
    since: Optional[datetime.date] = None

    @classmethod
    def from_file(cls, path: Path):
        if not path.exists():
            return cls()
        try:
            import yaml
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except Exception:
            data = json.loads(path.read_text(encoding="utf-8"))
        cfg = cls()
        cfg.brain = Path(data.get("brain", str(cfg.brain)))
        cfg.arxiv_categories = data.get("arxiv_categories", cfg.arxiv_categories)
        cfg.search_queries = data.get("search_queries", cfg.search_queries)
        cfg.domains = data.get("domains", cfg.domains)
        cfg.keywords = sorted({w.lower() for q in cfg.search_queries for w in q.split()})
        cfg.max_results = int(data.get("max_results", cfg.max_results))
        cfg.max_age_days = int(data.get("max_age_days", cfg.max_age_days))
        if data.get("since"):
            cfg.since = datetime.date.fromisoformat(data["since"])
        return cfg

    def save_default(self, path: Path = DEFAULT_CONFIG):
        payload = {
            "brain": str(self.brain),
            "arxiv_categories": self.arxiv_categories,
            "search_queries": self.search_queries,
            "domains": self.domains,
            "max_results": self.max_results,
            "max_age_days": self.max_age_days,
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _fetch_url(url: str, retries: int = MAX_RETRIES, timeout: int = REQUEST_TIMEOUT) -> str:
    """Fetch a URL with exponential backoff and a sensible User-Agent."""
    headers = {
        "User-Agent": (
            "3d-printing-process-optimizer-knowledge-updater/1.0 "
            "(research crawler; contact: project maintainer)"
        )
    }
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8", "ignore")
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                wait = BACKOFF_SECONDS * (2 ** attempt)
                logger.warning("Rate-limited / unavailable (%s). Backing off %.1fs", e.code, wait)
                time.sleep(wait)
                last_err = e
                continue
            raise
        except Exception as e:
            wait = BACKOFF_SECONDS * (2 ** attempt)
            logger.warning("Fetch attempt %d failed: %s. Retrying in %.1fs", attempt + 1, e, wait)
            last_err = e
            time.sleep(wait)
    raise RuntimeError(f"Failed to fetch {url} after {retries} attempts: {last_err}")


def _clean_atom_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def parse_arxiv_atom(xml: str) -> List[Entry]:
    """Parse ArXiv Atom response into a list of Entry objects."""
    entries: List[Entry] = []
    for block in re.findall(r"<entry>(.*?)</entry>", xml, re.S):
        def get(tag: str) -> str:
            m = re.search(r"<%s[^>]*>(.*?)</%s>" % (tag, tag), block, re.S)
            return _clean_atom_text(m.group(1)) if m else ""

        title = get("title")
        if not title or title.lower().startswith("comment"):
            continue
        summary = get("summary")
        published = get("published")[:10]
        link_match = re.search(r'<id>(.*?)</id>', block, re.S)
        link = link_match.group(1).strip() if link_match else ""
        authors = ", ".join(re.findall(r"<name>(.*?)</name>", block))
        doi_match = re.search(r"<arxiv:doi[^>]*>(.*?)</arxiv:doi>", block, re.S)
        doi = _clean_atom_text(doi_match.group(1)) if doi_match else "-"
        entries.append(
            Entry(
                title=title,
                authors=authors,
                date=published,
                url=link,
                abstract=summary,
                source="arXiv",
                venue="arXiv",
                doi=doi,
            )
        )
    return entries


def fetch_arxiv(category: str, max_results: int, since: Optional[datetime.date] = None, timeout: int = REQUEST_TIMEOUT, retries: int = MAX_RETRIES) -> List[Entry]:
    """Query the ArXiv Atom API for a single category."""
    base = "http://export.arxiv.org/api/query"
    params = {
        "search_query": f"cat:{category}",
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": max_results,
    }
    url = f"{base}?{urllib.parse.urlencode(params)}"
    try:
        xml = _fetch_url(url, retries=retries, timeout=timeout)
    except Exception as e:
        logger.warning("ArXiv fetch failed for %s: %s", category, e)
        return []
    entries = parse_arxiv_atom(xml)
    if since:
        entries = [e for e in entries if _not_older_than(e.date, since)]
    return entries


def _not_older_than(date_str: str, cutoff: datetime.date) -> bool:
    try:
        d = datetime.date.fromisoformat(date_str[:10])
        return d >= cutoff
    except Exception:
        return True


def relevance(entry: Entry, keywords: Sequence[str], max_age_days: int) -> float:
    """Score = keyword match count + recency weight."""
    text = f"{entry.title} {entry.abstract}".lower()
    kw_matches = sum(1 for k in set(keywords) if k in text)
    try:
        d = datetime.date.fromisoformat(entry.date[:10])
        age_days = (datetime.date.today() - d).days
        recency = max(0.0, 1.0 - age_days / max_age_days)
    except Exception:
        recency = 0.0
    return kw_matches + 2.0 * recency


class SearchProvider:
    """Pluggable web-search provider. Implement real search by subclassing."""
    def search(self, query: str, since: Optional[datetime.date] = None) -> List[Entry]:
        raise NotImplementedError


class DomainCrawlProvider(SearchProvider):
    """Fetch authoritative domain landing pages via direct HTTP + optional crawl4ai."""
    def __init__(self, domains: Sequence[str], use_crawl4ai: bool = True):
        self.domains = list(domains)
        self.use_crawl4ai = use_crawl4ai

    def search(self, query: str, since: Optional[datetime.date] = None) -> List[Entry]:
        entries: List[Entry] = []
        crawler = None
        if self.use_crawl4ai:
            try:
                from crawl4ai import WebCrawler  # type: ignore[import-untyped]
                crawler = WebCrawler()
                crawler.warmup()
            except Exception as e:
                logger.info("crawl4ai unavailable (%s); falling back to direct HTTP fetch.", e)
                crawler = None
        today = str(datetime.date.today())
        for domain in self.domains:
            url = f"https://{domain}"
            try:
                if crawler:
                    res = crawler.run(url=url)
                    text = (res.markdown or "")[:600]
                else:
                    text = _fetch_url(url)[:600]
                title = self._extract_title(text) or f"Domain scan: {domain}"
                entries.append(
                    Entry(
                        title=title,
                        authors="",
                        date=today,
                        url=url,
                        abstract=text,
                        source="domain_crawl",
                        venue=domain,
                    )
                )
            except Exception as e:
                logger.warning("Domain crawl failed for %s: %s", domain, e)
        return entries

    @staticmethod
    def _extract_title(html_or_md: str) -> Optional[str]:
        m = re.search(r"<title[^>]*>(.*?)</title>", html_or_md, re.S | re.I)
        if m:
            return _clean_atom_text(m.group(1))
        lines = [ln.strip() for ln in html_or_md.splitlines() if ln.strip()]
        return lines[0][:80] if lines else None


class PlaceholderSearchProvider(SearchProvider):
    """Placeholder for a real search API. Returns empty; replace with Serper/SerpAPI/etc."""
    def search(self, query: str, since: Optional[datetime.date] = None) -> List[Entry]:
        logger.info("Placeholder web-search provider active for query: %r", query)
        return []


def build_search_provider(cfg: Config, use_crawl4ai: bool = True) -> SearchProvider:
    """Return a provider that combines domain crawl and any configured real search."""
    return DomainCrawlProvider(cfg.domains, use_crawl4ai=use_crawl4ai)


def existing_hashes(brain_path: Path) -> Set[str]:
    if not brain_path.exists():
        return set()
    text = brain_path.read_text(encoding="utf-8", errors="ignore")
    return set(re.findall(r"<!--h:([0-9a-f]{12})-->", text))


def append_entries(
    entries: Iterable[Entry],
    brain_path: Path,
    cfg: Config,
    score_fn: Optional[Callable[[Entry], float]] = None,
) -> int:
    """Append new entries to the brain. Returns count of appended entries."""
    score_fn = score_fn or (lambda e: relevance(e, cfg.keywords, cfg.max_age_days))
    existing = existing_hashes(brain_path)
    ranked = sorted(entries, key=score_fn, reverse=True)
    new_rows: List[str] = []
    log_lines: List[str] = []
    today = datetime.date.today().isoformat()
    for e in ranked:
        h = e.hash()
        if h in existing:
            continue
        existing.add(h)
        row = (
            f"| {e.title[:90].replace('|', '/')} | "
            f"{e.authors[:40] or '-'} | {e.year()} | {e.venue} | "
            f"{e.url or e.doi} | score={score_fn(e):.2f} <!--h:{h}--> |"
        )
        new_rows.append(row)
        log_lines.append(f"- {today} — added: {e.title[:90]}")
    if not new_rows:
        logger.info("No new entries to append.")
        return 0
    if cfg.dry_run:
        logger.info("DRY-RUN: would append %d entries", len(new_rows))
        for row in new_rows:
            logger.info("  %s", row)
        return len(new_rows)
    brain_path.parent.mkdir(parents=True, exist_ok=True)
    with brain_path.open("a", encoding="utf-8") as f:
        f.write(f"\n<!-- auto-appended {today} -->\n")
        f.write("\n".join(new_rows) + "\n")
        f.write("\n".join(log_lines) + "\n")
    logger.info("Appended %d new entries to %s", len(new_rows), brain_path)
    return len(new_rows)


def run_pipeline(cfg: Config, timeout: int = REQUEST_TIMEOUT, retries: int = MAX_RETRIES) -> int:
    """Execute the full update pipeline. Returns number of new entries."""
    logger.info("Starting knowledge update: brain=%s dry_run=%s", cfg.brain, cfg.dry_run)
    entries: List[Entry] = []
    for cat in cfg.arxiv_categories:
        logger.info("Fetching arXiv category %s", cat)
        entries.extend(fetch_arxiv(cat, cfg.max_results, cfg.since, timeout=timeout, retries=retries))
    provider = build_search_provider(cfg)
    for query in cfg.search_queries:
        logger.info("Running web search / domain crawl for %r", query)
        try:
            entries.extend(provider.search(query, cfg.since))
        except Exception as e:
            logger.warning("Search provider failed for %r: %s", query, e)
    if not entries:
        logger.info("No entries fetched (offline or empty result). Brain left unchanged.")
        return 0
    return append_entries(entries, cfg.brain, cfg)


def parse_args(argv: Optional[Sequence[str]] = None):
    parser = argparse.ArgumentParser(
        description="Update the SECOND-KNOWLEDGE-BRAIN.md with fresh AM research and domain sources.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing.")
    parser.add_argument("--since", type=str, metavar="YYYY-MM-DD", help="Ignore entries older than date.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="Path to JSON/YAML config.")
    parser.add_argument("--brain", type=Path, default=DEFAULT_BRAIN, help="Path to brain markdown file.")
    parser.add_argument("--max-results", type=int, default=15, help="Max arXiv results per category.")
    parser.add_argument("--timeout", type=int, default=REQUEST_TIMEOUT, help="HTTP request timeout in seconds.")
    parser.add_argument("--max-retries", type=int, default=MAX_RETRIES, help="Max retries per HTTP request.")
    parser.add_argument("--init-config", action="store_true", help="Write a default config file and exit.")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging.")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    if args.init_config:
        Config(brain=args.brain).save_default(args.config)
        logger.info("Default config written to %s", args.config)
        return 0
    cfg = Config.from_file(args.config) if args.config.exists() else Config()
    cfg.brain = args.brain
    cfg.max_results = args.max_results
    cfg.dry_run = args.dry_run
    if args.since:
        cfg.since = datetime.date.fromisoformat(args.since)
    try:
        count = run_pipeline(cfg, timeout=args.timeout, retries=args.max_retries)
        logger.info("Knowledge update complete. New entries: %d", count)
        return 0
    except Exception as e:
        logger.exception("Knowledge update failed: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())

