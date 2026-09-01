import re
import os
import sys
from pathlib import Path

ROOT = Path("/home/dev/Desktop/projects/AI-InnovationHackathon")

def gh_slug(header_text):
    text = header_text.strip()
    text = re.sub(r'^#+\s*', '', text)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'[\U00010000-\U0010ffff\u2600-\u26ff\u2700-\u27bf\u200d\ufe0f]', '', text)
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')

def get_markdown_headers(filepath):
    content = filepath.read_text(encoding='utf-8')
    headers = []
    in_code_block = False
    for line in content.splitlines():
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        m = re.match(r'^(#{1,6})\s+(.+)$', line)
        if m:
            raw_text = m.group(2).strip()
            slug = gh_slug(raw_text)
            headers.append((raw_text, slug))
    return headers

def verify_all_links():
    docs = [
        ROOT / "README.md",
        ROOT / "docs/architecture.md",
        ROOT / "docs/api_specification.md",
        ROOT / "docs/setup_and_deployment.md",
        ROOT / "docs/user_guide.md",
        ROOT / "docs/multilingual_support.md",
    ]
    
    # Map each file to its set of header slugs
    header_map = {}
    for doc in docs:
        if doc.exists():
            h_list = get_markdown_headers(doc)
            header_map[doc.name] = set(s for _, s in h_list)
            # print for debugging
            # print(f"File {doc.name} has {len(header_map[doc.name])} headers")

    link_pattern = re.compile(r'!?\[([^\]]*)\]\(([^)]+)\)')
    total_errors = 0

    for doc in docs:
        if not doc.exists():
            print(f"Missing doc: {doc}")
            total_errors += 1
            continue
        
        content = doc.read_text(encoding='utf-8')
        in_code_block = False
        lines = content.splitlines()
        
        print(f"\n--- Verifying {doc.relative_to(ROOT)} ---")
        doc_errors = 0

        for line_num, line in enumerate(lines, 1):
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue

            for match in link_pattern.finditer(line):
                link_text = match.group(1)
                raw_target = match.group(2).strip()

                if raw_target.startswith(('http://', 'https://', 'mailto:', 'data:')):
                    continue

                if '#' in raw_target:
                    target_file_str, anchor = raw_target.split('#', 1)
                else:
                    target_file_str, anchor = raw_target, ""

                if target_file_str:
                    target_file = (doc.parent / target_file_str).resolve()
                    if not target_file.exists():
                        print(f"  Line {line_num}: [BROKEN FILE LINK] '{link_text}' -> '{raw_target}' (Resolved: {target_file})")
                        doc_errors += 1
                        continue
                    if anchor and target_file.suffix == '.md':
                        clean_anchor = anchor.lower().strip()
                        target_slugs = header_map.get(target_file.name, set())
                        if clean_anchor not in target_slugs:
                            print(f"  Line {line_num}: [BROKEN CROSS-FILE ANCHOR] '{link_text}' -> '{raw_target}' (Anchor #{clean_anchor} not in {target_file.name})")
                            doc_errors += 1
                else:
                    if anchor:
                        clean_anchor = anchor.lower().strip()
                        doc_slugs = header_map.get(doc.name, set())
                        if clean_anchor not in doc_slugs:
                            print(f"  Line {line_num}: [BROKEN INTERNAL ANCHOR] '{link_text}' -> #{clean_anchor}")
                            doc_errors += 1

        if doc_errors == 0:
            print(f"  ✓ All links & anchors in {doc.name} verified clean!")
        else:
            print(f"  ✗ {doc_errors} broken links in {doc.name}")
            total_errors += doc_errors

    print("\n==========================================")
    if total_errors == 0:
        print("🎉 ALL 6 MARKDOWN DOCUMENTS HAVE 100% VALID LINKS & ANCHORS!")
        return True
    else:
        print(f"❌ TOTAL BROKEN LINKS: {total_errors}")
        return False

if __name__ == '__main__':
    verify_all_links()
