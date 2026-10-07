# -*- coding: utf-8 -*-
"""Local, source-backed web research for ALI.

The web layer is an internal tool used by the normal chat pipeline. It does not
open a browser window and it never asks a separate UI surface to answer the user.
The result is returned to the same conversation as evidence with source URLs.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from html import unescape
from urllib.parse import quote, urlparse, parse_qs, unquote
from urllib.request import Request, urlopen
import ipaddress
import re
import socket
import ssl
from typing import Any


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    source: str
    rank: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


UA = "ALI-Studio/4.6 (+local-agent; source-backed-research)"
_EXPLICIT_WEB_RE = re.compile(
    r"(?:ابحث\s+(?:لي\s+)?(?:على|في|عبر)\s*ال(?:إنترنت|انترنت|انترنيت|ويب)|"
    r"ابحث\s+(?:عن|في|عبر)\s+(?:الويب|الإنترنت|انترنت)|"
    r"بحث\s+ويب|web\s+search|search\s+the\s+web|browse\s+the\s+web|"
    r"look\s+it\s+up|online\s+research|internet\s+research)",
    re.I,
)
_CURRENT_RE = re.compile(
    r"(?:اليوم|حالي(?:اً|ا)?|الآن|اخر|آخر|أحدث|حديث(?:ة|ا)?|مؤخر(?:اً|ا)?|حالياً|"
    r"today|now|current|latest|recent|newest|live|this\s+(?:week|month|year)|"
    r"2026|20\d{2})",
    re.I,
)
_WEB_NEGATIVE_RE = re.compile(r"(?:ابحث\s+في\s+(?:الملفات|المشروع|المجلد)|search\s+(?:files|the\s+project))", re.I)


def should_search_web(query: str, *, auto_current: bool = True) -> tuple[bool, str]:
    """Return whether the normal chat pipeline should invoke web research."""
    q = str(query or "").strip()
    if not q or _WEB_NEGATIVE_RE.search(q):
        return False, ""
    if _EXPLICIT_WEB_RE.search(q):
        return True, "explicit_web_request"
    if auto_current and _CURRENT_RE.search(q):
        return True, "freshness_required"
    return False, ""


def clean_query(query: str) -> str:
    q = str(query or "").strip()
    q = _EXPLICIT_WEB_RE.sub(" ", q)
    q = re.sub(r"\s+", " ", q).strip(" .،,؟?\t\n")
    return q or str(query or "").strip()


def _dns_addresses(host: str) -> set[str]:
    out: set[str] = set()
    try:
        for item in socket.getaddrinfo(host, None):
            sockaddr = item[4]
            if sockaddr:
                out.add(str(sockaddr[0]))
    except Exception:
        pass
    return out


def _safe_public_url(url: str) -> None:
    p = urlparse(str(url))
    if p.scheme not in {"http", "https"} or not p.hostname:
        raise ValueError("Only public http(s) URLs are allowed")
    host = p.hostname.lower().rstrip(".")
    if host in {"localhost", "localhost.localdomain"} or host.endswith(".local"):
        raise ValueError("Localhost URL blocked")
    try:
        ip = ipaddress.ip_address(host)
        addresses = {str(ip)}
    except ValueError:
        addresses = _dns_addresses(host)
    for raw in addresses:
        try:
            ip = ipaddress.ip_address(raw)
        except ValueError:
            continue
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
            or ip.is_unspecified
        ):
            raise ValueError("Private/local network URL blocked")


def _fetch(url: str, timeout: int = 15) -> tuple[str, dict[str, str]]:
    _safe_public_url(url)
    req = Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept-Language": "ar,en;q=0.8",
            "Accept": "text/html,application/xhtml+xml,text/plain;q=0.8,*/*;q=0.1",
        },
    )
    ctx = ssl.create_default_context()
    with urlopen(req, timeout=timeout, context=ctx) as response:
        raw = response.read(4_000_000)
        headers = {
            "content_type": str(response.headers.get("Content-Type", "")),
            "charset": str(response.headers.get_content_charset() or "utf-8"),
        }
        return raw.decode(headers["charset"], "replace"), headers


def _strip_html(value: str) -> str:
    text = unescape(re.sub(r"<[^>]+>", " ", str(value or "")))
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _search_duckduckgo(query: str, limit: int) -> list[SearchResult]:
    html, _ = _fetch("https://html.duckduckgo.com/html/?q=" + quote(query), timeout=15)
    blocks = re.findall(
        r'<div[^>]+class="result"[^>]*>(.*?)</div>\s*</div>',
        html,
        flags=re.S | re.I,
    )
    if not blocks:
        blocks = re.findall(r'<a[^>]+class="result__a"[^>]*>.*?</a>', html, flags=re.S | re.I)
    out: list[SearchResult] = []
    seen: set[str] = set()
    for block in blocks:
        m = re.search(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>', block, re.S | re.I)
        if not m:
            m = re.search(r'<a[^>]+href="([^"]+)"[^>]+class="result__a"[^>]*>(.*?)</a>', block, re.S | re.I)
        if not m:
            continue
        url = unescape(m.group(1))
        try:
            params = parse_qs(urlparse(url).query)
            url = unquote(params.get("uddg", [url])[0])
        except Exception:
            pass
        if not url.startswith(("http://", "https://")) or url in seen:
            continue
        title = _strip_html(m.group(2))
        sm = re.search(r'class="result__snippet"[^>]*>(.*?)</(?:a|span|div)>', block, re.S | re.I)
        snippet = _strip_html(sm.group(1)) if sm else ""
        seen.add(url)
        out.append(SearchResult(title or url, url, snippet, "duckduckgo", len(out) + 1))
        if len(out) >= limit:
            break
    return out


def _search_bing(query: str, limit: int) -> list[SearchResult]:
    html, _ = _fetch("https://www.bing.com/search?q=" + quote(query), timeout=15)
    out: list[SearchResult] = []
    for block in re.findall(r'<li[^>]+class="b_algo"[^>]*>(.*?)</li>', html, re.S | re.I):
        m = re.search(r'<h2[^>]*>\s*<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', block, re.S | re.I)
        if not m:
            continue
        url = unescape(m.group(1))
        if not url.startswith(("http://", "https://")):
            continue
        title = _strip_html(m.group(2))
        sm = re.search(r'<p[^>]*>(.*?)</p>', block, re.S | re.I)
        snippet = _strip_html(sm.group(1)) if sm else ""
        out.append(SearchResult(title or url, url, snippet, "bing", len(out) + 1))
        if len(out) >= limit:
            break
    return out


def search(query: str, limit: int = 8) -> list[SearchResult]:
    q = clean_query(query)
    if not q:
        return []
    limit = max(1, min(int(limit or 8), 10))
    errors: list[str] = []
    try:
        results = _search_duckduckgo(q, limit)
        if results:
            return results
    except Exception as exc:
        errors.append(f"duckduckgo: {exc}")
    try:
        results = _search_bing(q, limit)
        if results:
            return results
    except Exception as exc:
        errors.append(f"bing: {exc}")
    return [SearchResult("تعذر البحث عبر الإنترنت", "", " | ".join(errors) or "لا توجد نتائج", "search")]


def _extract_title(html: str, fallback: str) -> str:
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I)
    return _strip_html(m.group(1)) if m else fallback


def _html_to_text(html: str) -> str:
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "noscript", "svg", "canvas", "template"]):
            tag.decompose()
        text = soup.get_text("\n")
    except Exception:
        text = re.sub(r"<script.*?</script>|<style.*?</style>|<noscript.*?</noscript>", "", html, flags=re.S | re.I)
        text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def fetch_text(url: str, timeout: int = 20) -> dict[str, Any]:
    html, headers = _fetch(url, timeout)
    content_type = headers.get("content_type", "").lower()
    if content_type and not any(x in content_type for x in ("text/html", "application/xhtml+xml", "text/plain")):
        return {"url": url, "title": url, "text": "", "error": f"unsupported_content_type:{content_type}"}
    return {
        "url": url,
        "title": _extract_title(html, url),
        "text": _html_to_text(html)[:1_000_000],
    }


def research(query: str, limit: int = 5) -> dict[str, Any]:
    q = clean_query(query)
    results = search(q, limit)
    documents: list[dict[str, Any]] = []
    for result in results:
        if not result.url.startswith(("http://", "https://")):
            continue
        try:
            doc = fetch_text(result.url)
            if result.snippet and not doc.get("text"):
                doc["text"] = result.snippet
            doc["snippet"] = result.snippet
            doc["rank"] = result.rank
            doc["source"] = result.source
            documents.append(doc)
        except Exception as exc:
            documents.append({
                "url": result.url,
                "title": result.title,
                "text": result.snippet,
                "snippet": result.snippet,
                "rank": result.rank,
                "source": result.source,
                "error": str(exc),
            })
    return {
        "query": q,
        "results": [r.to_dict() for r in results],
        "documents": documents,
        "result_count": len(results),
        "fetched_count": sum(1 for d in documents if d.get("text")),
    }


def evidence_text(web: dict[str, Any], *, max_chars: int = 3000, max_sources: int = 3) -> str:
    """Compact evidence for a small local context window."""
    blocks: list[str] = []
    used = 0
    for i, doc in enumerate((web or {}).get("documents", [])[:max_sources], 1):
        text = re.sub(r"\s+", " ", str(doc.get("text") or doc.get("snippet") or "").strip())
        if not text:
            continue
        take = min(len(text), 700, max(0, max_chars - used))
        if take <= 0:
            break
        title = str(doc.get("title") or doc.get("url") or f"Web {i}")
        blocks.append(f"[W{i}] {title}\n{text[:take]}\nURL: {doc.get('url','')}")
        used += take
    return "\n\n".join(blocks)


def source_footer(web: dict[str, Any], *, language: str = "ar", max_sources: int = 5) -> str:
    docs = [d for d in (web or {}).get("documents", []) if d.get("url")][:max_sources]
    if not docs:
        return ""
    heading = "المصادر" if language.lower().startswith("ar") else "Sources"
    lines = [f"\n\n{heading}:"]
    for i, d in enumerate(docs, 1):
        title = str(d.get("title") or d.get("url") or "Source").strip()
        url = str(d.get("url") or "").strip()
        lines.append(f"[{i}] {title} — {url}")
    return "\n".join(lines)


def web_fallback(web: dict[str, Any], *, language: str = "ar") -> str:
    docs = [d for d in (web or {}).get("documents", []) if d.get("text")]
    if not docs:
        return "تعذر الحصول على مصادر من الإنترنت في الوقت الحالي." if language.lower().startswith("ar") else "No usable web sources were retrieved."
    intro = "اعتمدتُ على نتائج الإنترنت التالية، وهذه خلاصة أولية لما وجدته:" if language.lower().startswith("ar") else "I found the following web evidence; here is a concise extract:"
    parts = [intro]
    for i, d in enumerate(docs[:3], 1):
        text = re.sub(r"\s+", " ", str(d.get("text") or "").strip())
        if text:
            parts.append(f"\n[{i}] {d.get('title') or d.get('url')}\n{text[:650]}")
    return "\n".join(parts)
