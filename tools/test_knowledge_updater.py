# -*- coding: utf-8 -*-
"""Unit tests for knowledge_updater.py.

Run with: python -m pytest tools/test_knowledge_updater.py -v
"""
from __future__ import annotations

import datetime
import json
import sys
import tempfile
from pathlib import Path

# Ensure the module under test is importable when tests are run from repo root.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import knowledge_updater as ku


def test_entry_hash_uses_doi():
    e1 = ku.Entry(title="T1", authors="A1", date="2024-01-01", url="http://x", abstract="abs", doi="10.1234/x")
    e2 = ku.Entry(title="T1", authors="A1", date="2024-01-01", url="http://y", abstract="abs", doi="10.1234/x")
    assert e1.hash() == e2.hash()


def test_entry_hash_differs_by_url_when_no_doi():
    e1 = ku.Entry(title="T1", authors="A1", date="2024-01-01", url="http://x", abstract="abs")
    e2 = ku.Entry(title="T1", authors="A1", date="2024-01-01", url="http://y", abstract="abs")
    assert e1.hash() != e2.hash()


def test_relevance_counts_keywords_and_recency():
    entry = ku.Entry(
        title="FDM layer adhesion and anisotropy in additive manufacturing",
        authors="Smith",
        date=str(datetime.date.today()),
        url="http://x",
        abstract="Study of FDM process parameter optimization.",
    )
    score = ku.relevance(entry, ku.KEYWORDS, ku.MAX_AGE_DAYS)
    assert score >= 4.0


def test_relevance_old_entry_gets_lower_score():
    entry = ku.Entry(
        title="FDM layer adhesion",
        authors="Smith",
        date="2000-01-01",
        url="http://x",
        abstract="Old study.",
    )
    score = ku.relevance(entry, ku.KEYWORDS, ku.MAX_AGE_DAYS)
    assert score <= 3.0


def test_parse_arxiv_atom_extracts_entries():
    atom = """
    <?xml version="1.0"?>
    <feed xmlns="http://www.w3.org/2005/Atom">
      <entry>
        <title>AM Parameter Optimization</title>
        <author><name>J. Doe</name></author>
        <published>2024-06-15T00:00:00Z</published>
        <id>http://arxiv.org/abs/2406.12345</id>
        <summary>We optimize FDM parameters using Taguchi.</summary>
      </entry>
    </feed>
    """
    entries = ku.parse_arxiv_atom(atom)
    assert len(entries) == 1
    assert entries[0].title == "AM Parameter Optimization"
    assert entries[0].authors == "J. Doe"
    assert entries[0].date == "2024-06-15"
    assert entries[0].url == "http://arxiv.org/abs/2406.12345"


def test_existing_hashes_finds_hashes():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("| title | authors | year | venue | url | score=1.0 <!--h:abc123def45a--> |\n")
        f.write("| t2 | a2 | 2023 | v2 | u2 | score=0.5 <!--h:abc123def45b--> |\n")
        tmp = f.name
    try:
        hashes = ku.existing_hashes(Path(tmp))
        assert "abc123def45a" in hashes
        assert "abc123def45b" in hashes
    finally:
        Path(tmp).unlink()


def test_append_entries_deduplicates_and_appends():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# Brain\n\n| title | authors | year | venue | url | score=1.0 <!--h:abc123def45a--> |\n")
        tmp = f.name
    try:
        e1 = ku.Entry(title="New paper", authors="Alice", date="2024-01-01", url="http://new", abstract="abs")
        e2 = ku.Entry(title="Old paper", authors="Bob", date="2023-01-01", url="http://old", abstract="abs")
        cfg = ku.Config(brain=Path(tmp), dry_run=False, keywords=ku.KEYWORDS)
        count = ku.append_entries([e1, e2], Path(tmp), cfg)
        assert count == 2
        text = Path(tmp).read_text(encoding="utf-8")
        assert "New paper" in text
        assert "Old paper" in text
        # Second append should add nothing
        count2 = ku.append_entries([e1], Path(tmp), cfg)
        assert count2 == 0
    finally:
        Path(tmp).unlink()


def test_append_entries_dry_run_does_not_write():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# Brain\n")
        tmp = f.name
    try:
        e1 = ku.Entry(title="Dry paper", authors="X", date="2024-01-01", url="http://dry", abstract="abs")
        cfg = ku.Config(brain=Path(tmp), dry_run=True, keywords=ku.KEYWORDS)
        count = ku.append_entries([e1], Path(tmp), cfg)
        assert count == 1
        text = Path(tmp).read_text(encoding="utf-8")
        assert "Dry paper" not in text
    finally:
        Path(tmp).unlink()


def test_config_from_json():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"max_results": 5, "max_age_days": 365}, f)
        tmp = f.name
    try:
        cfg = ku.Config.from_file(Path(tmp))
        assert cfg.max_results == 5
        assert cfg.max_age_days == 365
    finally:
        Path(tmp).unlink()


def test_not_older_than():
    assert ku._not_older_than("2024-01-01", datetime.date(2024, 1, 1))
    assert not ku._not_older_than("2023-12-31", datetime.date(2024, 1, 1))


def test_domain_crawl_provider_graceful_without_crawl4ai():
    provider = ku.DomainCrawlProvider(domains=["example.invalid"], use_crawl4ai=False)
    original_fetch = ku._fetch_url
    def fast_fail(url, retries=1, timeout=1):
        raise RuntimeError("simulated network failure")
    ku._fetch_url = fast_fail
    try:
        entries = provider.search("test")
        assert isinstance(entries, list)
        assert len(entries) == 0
    finally:
        ku._fetch_url = original_fetch
