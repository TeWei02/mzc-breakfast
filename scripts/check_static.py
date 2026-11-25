#!/usr/bin/env python3
"""Static-site checks for the Mei Zhi Chen ordering site.

Runs with the Python standard library only, so the CI job needs no pip install.

Checks
------
1. Required files are present.
2. Every local href/src reference resolves to an existing file.
3. HTML files parse, and obviously unclosed tags are reported.
4. No obvious secrets (ECPay keys, Apps Script deployment URLs, admin tokens)
   are committed.

Exit code 1 on failures (missing files, broken local links, unparsable HTML).
Secret hits are reported as warnings and do not fail the build.
"""

from __future__ import annotations

import os
import re
import sys
from html.parser import HTMLParser
from urllib.parse import unquote, urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REQUIRED_FILES = [
    "index.html",
    "admin.html",
    "sauce.html",
    "README.md",
    "README.en.md",
    "LICENSE",
]

HTML_FILES = ["index.html", "admin.html", "sauce.html"]

VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}

SKIP_PREFIXES = (
    "http://", "https://", "//", "mailto:", "tel:", "javascript:",
    "data:", "sms:", "line:", "#",
)

SECRET_PATTERNS = [
    (r"HashKey\s*[:=]\s*['\"][A-Za-z0-9]{12,}['\"]", "可能的綠界 HashKey / possible ECPay HashKey"),
    (r"HashIV\s*[:=]\s*['\"][A-Za-z0-9]{12,}['\"]", "可能的綠界 HashIV / possible ECPay HashIV"),
    (r"script\.google\.com/macros/s/AKfycb[A-Za-z0-9_\-]{10,}", "Apps Script 部署網址 / deployment URL"),
    (r"ADMIN_TOKEN\s*[:=]\s*['\"][^'\"]{6,}['\"]", "管理密碼字面值 / literal admin token"),
]

errors: list[str] = []
warnings: list[str] = []


class RefCollector(HTMLParser):
    """Collect href/src values and check tag balancing."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.refs: list[tuple[str, int]] = []
        self.stack: list[tuple[str, int]] = []
        self.unclosed: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        line = self.getpos()[0]
        for name, value in attrs:
            if name in ("href", "src") and value:
                self.refs.append((value.strip(), line))
        if tag not in VOID_TAGS:
            self.stack.append((tag, line))

    def handle_startendtag(self, tag: str, attrs) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in VOID_TAGS and self.stack and self.stack[-1][0] == tag:
            self.stack.pop()

    def handle_endtag(self, tag: str) -> None:
        if tag in VOID_TAGS:
            return
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                self.unclosed.extend(
                    f"<{t}> (line {ln})" for t, ln in self.stack[index + 1:]
                )
                del self.stack[index:]
                return


def check_required_files() -> None:
    for name in REQUIRED_FILES:
        if not os.path.isfile(os.path.join(ROOT, name)):
            errors.append(f"缺少必要檔案 / missing required file: {name}")


def check_links() -> None:
    broken = 0
    for html in HTML_FILES:
        path = os.path.join(ROOT, html)
        if not os.path.isfile(path):
            continue
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            source = handle.read()
        collector = RefCollector()
        collector.feed(source)
        collector.close()

        for tag, line in collector.unclosed:
            warnings.append(f"{html}:{line} 標籤可能未閉合 / possibly unclosed {tag}")

        for ref, line in collector.refs:
            if ref.lower().startswith(SKIP_PREFIXES):
                continue
            parsed = urlparse(ref)
            if parsed.scheme or parsed.netloc:
                continue
            target = unquote(parsed.path)
            if not target:
                continue
            candidate = os.path.normpath(os.path.join(ROOT, target.lstrip("/")))
            if not os.path.exists(candidate):
                errors.append(
                    f"{html}:{line} 本地連結失效 / broken local link: {ref}"
                )
                broken += 1
    print(f"連結檢查 / link check: {broken} broken")


def check_secrets() -> None:
    tracked: list[str] = []
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in {".git", "node_modules", "temp"}]
        for name in files:
            if name.endswith((".html", ".js", ".json", ".md", ".yml", ".yaml")):
                tracked.append(os.path.join(base, name))

    for path in tracked:
        rel = os.path.relpath(path, ROOT)
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as handle:
                lines = handle.readlines()
        except OSError as exc:  # pragma: no cover - unreadable file
            warnings.append(f"{rel}: 無法讀取 / unreadable ({exc})")
            continue
        for number, line in enumerate(lines, start=1):
            for pattern, label in SECRET_PATTERNS:
                if re.search(pattern, line):
                    warnings.append(f"{rel}:{number} {label}")


def main() -> int:
    check_required_files()
    check_links()
    check_secrets()

    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    report = ["## Static site check", ""]
    report.append(f"- required files: {len(REQUIRED_FILES)} checked")
    report.append(f"- errors: {len(errors)}")
    report.append(f"- warnings: {len(warnings)}")
    if errors:
        report.append("")
        report.append("### Errors")
        report.extend(f"- {item}" for item in errors)
    if warnings:
        report.append("")
        report.append("### Warnings")
        report.extend(f"- {item}" for item in warnings)
    body = "\n".join(report) + "\n"

    print(body)
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as handle:
            handle.write(body)

    if errors:
        print(f"FAILED: {len(errors)} error(s)")
        return 1
    print("OK: static site checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
