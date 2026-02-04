import re
from pathlib import Path


def _parse_frontmatter_title(text: str) -> str:
    if not text.startswith("---"):
        return ""
    parts = text.split("---", 2)
    if len(parts) < 3:
        return ""
    fm = parts[1]
    m = re.search(r"^title:\s*(.+?)\s*$", fm, flags=re.MULTILINE)
    if not m:
        return ""
    raw = m.group(1).strip()
    if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
        raw = raw[1:-1]
    return raw.strip()


def _split_frontmatter(text: str):
    if not text.startswith("---"):
        return "", text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return "", text
    front = "---" + parts[1] + "---\n"
    body = parts[2]
    return front, body


def _norm_title(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"[^a-z0-9 &()_-]+", "", s)
    return s


def _strip_inline_md(s: str) -> str:
    # Convert common inline markdown to plain text for comparison.
    # Links: [text](url) -> text
    s = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", s)
    # Images: ![alt](url) -> alt
    s = re.sub(r"!\[([^\]]*)\]\([^\)]+\)", r"\1", s)
    # Code: `code` -> code
    s = re.sub(r"`([^`]+)`", r"\1", s)
    # Emphasis: **x**, *x*, __x__, _x_ -> x
    s = re.sub(r"\*\*([^*]+)\*\*", r"\1", s)
    s = re.sub(r"\*([^*]+)\*", r"\1", s)
    s = re.sub(r"__([^_]+)__", r"\1", s)
    s = re.sub(r"_([^_]+)_", r"\1", s)
    return s


def remove_leading_h1_if_title(path: Path) -> bool:
    text = path.read_text(encoding="utf-8", errors="replace")
    title = _parse_frontmatter_title(text)
    if not title:
        return False

    front, body = _split_frontmatter(text)
    lines = body.splitlines(True)

    i = 0
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    if i >= len(lines):
        return False
    if not lines[i].startswith("# "):
        return False

    h1 = lines[i][2:].strip()
    h1_plain = _strip_inline_md(h1)
    if _norm_title(h1_plain) != _norm_title(title):
        return False

    j = i + 1
    if j < len(lines) and lines[j].strip() == "":
        j += 1
    new_body = "".join(lines[:i] + lines[j:])
    path.write_text(front + new_body.lstrip("\r\n"), encoding="utf-8")
    return True


def main():
    root = Path(__file__).resolve().parents[1]
    content_root = root / "content" / "docs"
    changed = []

    # Only check regular content pages (index.md bundles). Avoid list pages and taxonomy.
    for md in sorted(content_root.rglob("index.md")):
        # Skip section index pages; they often intentionally include headings.
        if md.name == "_index.md":
            continue
        if remove_leading_h1_if_title(md):
            changed.append(md)

    print(f"Updated {len(changed)} file(s)")
    for p in changed:
        print(p.relative_to(root).as_posix())


if __name__ == "__main__":
    main()
