import re
import os
import sys
from pathlib import Path

ROOT = Path("/home/dev/Desktop/projects/AI-InnovationHackathon")

DOCS_FILES = [
    ROOT / "README.md",
    ROOT / "docs/architecture.md",
    ROOT / "docs/api_specification.md",
    ROOT / "docs/setup_and_deployment.md",
    ROOT / "docs/user_guide.md",
    ROOT / "docs/multilingual_support.md",
    ROOT / "docs/architecture_diagram.svg",
    ROOT / "docs/architecture_diagram.png",
]

def slugify(header_text):
    # Convert header to GitHub Markdown anchor slug
    text = header_text.strip().lower()
    # Remove markdown formatting like bold, code, links
    text = re.sub(r'[*_`]', '', text)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Remove emojis and special characters except hyphens and alphanumeric
    text = re.sub(r'[^\w\s-]', '', text)
    # Replace spaces with hyphens
    text = re.sub(r'\s+', '-', text)
    return text

def extract_headers(content):
    headers = []
    for line in content.splitlines():
        m = re.match(r'^(#{1,6})\s+(.+)$', line)
        if m:
            header_text = m.group(2).strip()
            headers.append(slugify(header_text))
    return headers

def verify_markdown_file(file_path):
    print(f"\n--- Checking {file_path.relative_to(ROOT)} ---")
    if not file_path.exists():
        print(f"ERROR: File {file_path} does not exist!")
        return False

    content = file_path.read_text(encoding='utf-8')
    headers = extract_headers(content)
    # Also add math slug variants if any
    header_set = set(headers)

    # Find all markdown links: [text](link)
    # Ignore image embeds or links that are external URLs (http/https/mailto)
    link_pattern = re.compile(r'!?\[([^\]]*)\]\(([^)]+)\)')
    errors = 0

    for match in link_pattern.finditer(content):
        link_text = match.group(1)
        raw_target = match.group(2).strip()

        # Skip external URLs
        if raw_target.startswith(('http://', 'https://', 'mailto:', 'data:')):
            continue

        # Separate file path and anchor
        if '#' in raw_target:
            target_path_str, anchor = raw_target.split('#', 1)
        else:
            target_path_str, anchor = raw_target, ""

        # Resolve target file path
        if target_path_str:
            target_file = (file_path.parent / target_path_str).resolve()
            if not target_file.exists():
                print(f"  [BROKEN FILE LINK] Text: '{link_text}' -> Path: '{raw_target}' (Resolved: {target_file})")
                errors += 1
                continue
            else:
                # If target file exists and has anchor
                if anchor:
                    target_content = target_file.read_text(encoding='utf-8')
                    target_headers = extract_headers(target_content)
                    clean_anchor = anchor.lower().strip()
                    if clean_anchor not in target_headers:
                        # Spot check if close match
                        print(f"  [BROKEN ANCHOR LINK] Text: '{link_text}' -> Path: '{raw_target}' (Anchor #{clean_anchor} not in {target_file.name})")
                        errors += 1
        else:
            # Internal anchor in the same file
            clean_anchor = anchor.lower().strip()
            if clean_anchor not in header_set:
                print(f"  [BROKEN INTERNAL ANCHOR] Text: '{link_text}' -> #{clean_anchor}")
                errors += 1

    if errors == 0:
        print(f"  ✓ All links and anchors verified successfully!")
        return True
    else:
        print(f"  ✗ Found {errors} broken links/anchors.")
        return False

def main():
    all_ok = True
    for doc in DOCS_FILES:
        if not doc.exists():
            print(f"ERROR: Missing expected file {doc}")
            all_ok = False
        elif doc.suffix == '.md':
            ok = verify_markdown_file(doc)
            if not ok:
                all_ok = False

    print("\n==========================================")
    if all_ok:
        print("🎉 ALL DOCUMENTATION LINKS VERIFIED 100% CLEAN!")
        sys.exit(0)
    else:
        print("❌ DOCUMENTATION LINK VERIFICATION FAILED!")
        sys.exit(1)

if __name__ == '__main__':
    main()
