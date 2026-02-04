import argparse
import argparse
import os
import re
import shutil
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")
    return value or "untitled"


def sanitize_asset_filename(name: str) -> str:
    base = os.path.basename(name)
    base = base.replace("\\", "/")
    base = os.path.basename(base)

    # Common Obsidian paste naming: "Pasted image 20250101123000.png"
    m = re.match(r"^Pasted image\s+(\d{8,14})(\.[A-Za-z0-9]+)$", base)
    if m:
        return f"{m.group(1)}{m.group(2).lower()}"

    stem, ext = os.path.splitext(base)
    ext = ext.lower()
    stem = slugify(stem)
    return f"{stem}{ext}"


def strip_frontmatter(md: str) -> str:
    if not md.startswith("---"):
        return md
    parts = md.split("---", 2)
    if len(parts) < 3:
        return md
    return parts[2].lstrip("\r\n")


def remove_dataview_blocks(md: str) -> str:
    # Remove fenced blocks like ```dataviewjs ... ```
    return re.sub(r"```dataviewjs\s*.*?```\s*", "", md, flags=re.DOTALL | re.IGNORECASE)


def split_fenced_blocks(md: str):
    # Returns list of (is_code, text)
    out = []
    fence_re = re.compile(r"(^```.*?$)", flags=re.MULTILINE)
    pos = 0
    in_code = False

    for m in fence_re.finditer(md):
        start = m.start(1)
        line = m.group(1)
        out.append((in_code, md[pos:start]))
        out.append((True, line + "\n"))
        pos = m.end(1) + 1
        in_code = not in_code

    out.append((in_code, md[pos:]))
    return out


def extract_inline_tags(md: str):
    # Extract tags that look like #tag but ignore code fences.
    tags = set()
    parts = split_fenced_blocks(md)
    cleaned = []

    tag_re = re.compile(r"(?<!\S)#([a-zA-Z0-9_/-]+)")

    for is_code, text in parts:
        if is_code:
            cleaned.append(text)
            continue
        found = tag_re.findall(text)
        for t in found:
            tags.add(t)
        cleaned.append(tag_re.sub("", text))

    return "".join(cleaned), sorted(tags)


def title_from_filename(path: Path) -> str:
    stem = path.stem
    # Keep some common acronyms readable
    stem = stem.replace("AZUREADSSO", "AzureAD SSO")
    stem = stem.replace("_", " ")
    return stem


def extract_leading_h1(md: str):
    """If markdown starts with a level-1 heading, return (new_md, heading_text)."""
    lines = md.splitlines(True)
    i = 0
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    if i < len(lines) and lines[i].startswith("# "):
        heading = lines[i][2:].strip()
        # Drop heading line and at most one following blank line
        j = i + 1
        if j < len(lines) and lines[j].strip() == "":
            j += 1
        new_md = "".join(lines[:i] + lines[j:])
        return new_md, heading
    return md, ""


@dataclass
class MigrationItem:
    src: Path
    dest_bundle_dir: Path
    title: str
    tags: list[str]


def build_asset_index(search_roots: list[Path]):
    exts = {".png", ".jpg", ".jpeg", ".gif", ".svg"}
    index: dict[str, list[Path]] = {}
    for root in search_roots:
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if p.is_file() and p.suffix.lower() in exts:
                index.setdefault(p.name, []).append(p)
    return index


def find_asset(asset_name: str, note_dir: Path, hardening_root: Path, asset_index: dict[str, list[Path]]):
    candidates = []

    # First: relative common folders
    for rel in [
        note_dir / "assets" / asset_name,
        note_dir / "images" / asset_name,
        hardening_root / "assets" / asset_name,
        hardening_root / "images" / asset_name,
    ]:
        if rel.exists():
            candidates.append(rel)

    # Fallback to index by filename
    for p in asset_index.get(asset_name, []):
        candidates.append(p)

    if not candidates:
        return None

    # Prefer the closest path (shortest relative distance to note dir)
    def score(p: Path):
        try:
            rel = p.relative_to(note_dir)
            return (0, len(rel.parts))
        except Exception:
            pass
        try:
            rel = p.relative_to(hardening_root)
            return (1, len(rel.parts))
        except Exception:
            pass
        return (2, len(p.parts))

    return sorted(candidates, key=score)[0]


def replace_obsidian_embeds(md: str, note_path: Path, dest_bundle_dir: Path, hardening_root: Path, asset_index):
    note_dir = note_path.parent

    def repl(match):
        raw = match.group(1).strip()
        # Handle sizes like ![[img.png|300]]
        if "|" in raw:
            raw = raw.split("|", 1)[0].strip()

        src = find_asset(raw, note_dir=note_dir, hardening_root=hardening_root, asset_index=asset_index)
        if not src:
            return match.group(0)

        safe_name = sanitize_asset_filename(src.name)
        dest = dest_bundle_dir / safe_name
        dest_bundle_dir.mkdir(parents=True, exist_ok=True)
        if not dest.exists():
            shutil.copy2(src, dest)
        return f"![{safe_name}]({safe_name})"

    return re.sub(r"!\[\[(.*?)\]\]", repl, md)


def replace_standard_images(md: str, note_path: Path, dest_bundle_dir: Path, hardening_root: Path, asset_index):
    note_dir = note_path.parent

    def repl(match):
        alt = match.group(1)
        path = (match.group(2) or "").strip()
        if not path:
            return match.group(0)

        # Skip non-file sources (can't be copied into bundle).
        if path.startswith("data:") or re.match(r"^(?:https?:)?//", path, flags=re.IGNORECASE):
            return match.group(0)

        # Drop query/fragment from local paths like img.png?raw=1
        clean_path = path.split("?", 1)[0].split("#", 1)[0]
        name = os.path.basename(clean_path)
        src = None

        # If the link is relative, try relative to note
        try:
            rel = (note_dir / clean_path).resolve()
            if rel.exists():
                src = Path(rel)
        except OSError:
            # e.g. filename too long (data URIs) or invalid path
            return match.group(0)

        if not src:
            src = find_asset(name, note_dir=note_dir, hardening_root=hardening_root, asset_index=asset_index)

        if not src:
            return match.group(0)

        safe_name = sanitize_asset_filename(src.name)
        dest = dest_bundle_dir / safe_name
        dest_bundle_dir.mkdir(parents=True, exist_ok=True)
        if not dest.exists():
            shutil.copy2(src, dest)
        return f"![{alt}]({safe_name})"

    return re.sub(r"!\[(.*?)\]\((.*?)\)", repl, md)


def compute_destination(content_root: Path, rel_src: Path):
    # Topic-first mapping (not a 1:1 mirror). Uses source folder hints and filename keywords.
    src_str = str(rel_src).replace("\\", "/")
    src_lower = src_str.lower()
    name = rel_src.stem
    slug = slugify(name)

    # Explicit skips/merges (already authored pages)
    if src_str.endswith("hardening/tiering.md"):
        return content_root / "tiered-administration"
    if src_str.endswith("hardening/Kerberos_Security/Kerberos Armoring.md"):
        return content_root / "kerberos-armoring"
    if src_str.endswith("hardening/Kerberos_Security/Kerberos_RC4_Audit_CVE-2026-20833.md"):
        return content_root / "kerberos_rc4_audit_cve-2026-20833"

    # Entra/hybrid note that already exists in Entra section
    if name.lower().startswith("azureadsso"):
        # keep existing Entra ID location
        return Path("content/docs/entra-id/azureadsso-reset")

    if "/baseline/" in src_lower:
        return content_root / "baseline-and-audit" / slug
    if "/protocols/ldaps/" in src_lower:
        return content_root / "protocol-hardening" / "ldap-ldaps" / slug
    if "/protocols/" in src_lower:
        return content_root / "protocol-hardening" / slug
    if "/dns/" in src_lower:
        return content_root / "protocol-hardening" / "dns" / slug
    if "/laps/" in src_lower:
        return content_root / "directory-hygiene" / "laps" / slug
    if "/certificate/" in src_lower:
        return content_root / "certificate-services" / slug
    if "/kerberos_security/" in src_lower:
        return content_root / "protocol-hardening" / "kerberos" / slug

    # Filename-based fallback
    lower = name.lower()
    if "spool" in lower or "netcease" in lower or "domain controller" in lower:
        return content_root / "domain-controllers" / slug
    if "krbtgt" in lower or "replication" in lower:
        return content_root / "operations-and-recovery" / slug
    if "dcsync" in lower or "cve" in lower or "vulnerable" in lower or "mitigation" in lower:
        return content_root / "vulnerabilities-and-mitigations" / slug
    if "tier" in lower or "paw" in lower or "jump" in lower or "privileged" in lower:
        return content_root / "privileged-access" / slug
    if "service account" in lower or "lsa" in lower or "recycle" in lower or "quota" in lower:
        return content_root / "directory-hygiene" / slug
    if "exchange" in lower:
        return content_root / "applications-and-services" / slug

    return content_root / "directory-hygiene" / "misc" / slug


def build_note_map(items: list[MigrationItem], project_root: Path):
    # Map Obsidian display name (filename stem) -> docs-relative page path.
    # Example value: "docs/active-directory/protocol-hardening/dns/dnssec"
    docs_root = project_root / "content" / "docs"

    mapping: dict[str, str] = {}
    for it in items:
        try:
            docs_rel = it.dest_bundle_dir.relative_to(docs_root).as_posix()
        except Exception:
            # If destination is outside docs_root, fall back to absolute-ish POSIX path.
            docs_rel = it.dest_bundle_dir.as_posix().lstrip("/")

        if not docs_rel.startswith("docs/"):
            docs_rel = "docs/" + docs_rel.lstrip("/")

        key = it.src.stem
        mapping.setdefault(key, docs_rel)
        mapping.setdefault(key.lower(), docs_rel)

    return mapping


def replace_wikilinks(md: str, note_map: dict[str, str]):
    def repl(match):
        raw = match.group(1).strip()
        if "|" in raw:
            target, alias = raw.split("|", 1)
            target = target.strip()
            alias = alias.strip()
        else:
            target = raw
            alias = raw

        # Strip headings in wikilinks if present [[Note#Heading]]
        if "#" in target:
            target = target.split("#", 1)[0].strip()

        dest = note_map.get(target) or note_map.get(target.lower())
        if not dest:
            return f"{alias} (TODO: link: {target})"

        return f"[{alias}]({{{{< relref \"{dest}\" >}}}})"

    return re.sub(r"\[\[(.*?)\]\]", repl, md)


def render_frontmatter(title: str, tags: list[str]):
    date_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S")
    tags_line = ""
    if tags:
        tags_line = "tags: [" + ", ".join([f'"{t}"' for t in sorted(set(tags))]) + "]\n"

    return (
        "---\n"
        f'title: "{title}"\n'
        f"date: {date_str}\n"
        "draft: false\n"
        "authors: [\"ahmed\"]\n"
        + tags_line
        + "---\n\n"
    )


def migrate_one(item: MigrationItem, hardening_root: Path, asset_index, note_map: dict[str, str], overwrite: bool):
    dest_index = item.dest_bundle_dir / "index.md"
    if dest_index.exists() and not overwrite:
        return "skipped (exists)", dest_index

    raw = item.src.read_text(encoding="utf-8", errors="replace")
    md = strip_frontmatter(raw)
    md = remove_dataview_blocks(md)
    md, inline_tags = extract_inline_tags(md)
    md = replace_obsidian_embeds(md, note_path=item.src, dest_bundle_dir=item.dest_bundle_dir, hardening_root=hardening_root, asset_index=asset_index)
    md = replace_standard_images(md, note_path=item.src, dest_bundle_dir=item.dest_bundle_dir, hardening_root=hardening_root, asset_index=asset_index)
    md = replace_wikilinks(md, note_map)

    md, h1_title = extract_leading_h1(md)

    tags = list(item.tags)
    tags.extend(inline_tags)

    title = h1_title or item.title
    final = render_frontmatter(title, tags) + md.strip() + "\n"
    item.dest_bundle_dir.mkdir(parents=True, exist_ok=True)
    dest_index.write_text(final, encoding="utf-8")
    return "migrated", dest_index


def main():
    parser = argparse.ArgumentParser(description="Migrate Obsidian hardening notes to Hugo content.")
    parser.add_argument(
        "--hardening-root",
        default="/Users/abayoumy/GLOBAL BRANDS - Gbrands-Security Team - AD-Workflow/hardening",
    )
    parser.add_argument("--project-root", default="/Users/abayoumy/Projects/AD-Workflow")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    hardening_root = Path(args.hardening_root)
    project_root = Path(args.project_root)

    ad_content_root = project_root / "content" / "docs" / "active-directory"

    md_files = sorted(hardening_root.rglob("*.md"))

    # Build global asset index across hardening (and its parent vault) to resolve embeds.
    asset_index = build_asset_index([hardening_root, hardening_root.parent])

    items: list[MigrationItem] = []
    for src in md_files:
        rel = src.relative_to(hardening_root)
        dest_dir = compute_destination(ad_content_root, Path("hardening") / rel)
        # Allow non-AD destination (e.g., Entra page path)
        if str(dest_dir).startswith("content/"):
            dest_dir = project_root / dest_dir

        items.append(
            MigrationItem(
                src=src,
                dest_bundle_dir=dest_dir,
                title=title_from_filename(src),
                tags=[],
            )
        )

    note_map = build_note_map(items, project_root=project_root)

    if args.dry_run:
        for it in items:
            print(f"{it.src} -> {it.dest_bundle_dir / 'index.md'}")
        return

    migrated = 0
    skipped = 0
    for it in items:
        status, dest = migrate_one(
            it,
            hardening_root=hardening_root,
            asset_index=asset_index,
            note_map=note_map,
            overwrite=args.overwrite,
        )
        if status.startswith("migrated"):
            migrated += 1
        else:
            skipped += 1
        print(f"{status}: {it.src.name} -> {dest}")

    print(f"Done. migrated={migrated} skipped={skipped}")


if __name__ == "__main__":
    main()
