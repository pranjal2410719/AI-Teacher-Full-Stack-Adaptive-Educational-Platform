import re
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

def update_file_toc(filepath):
    content = filepath.read_text(encoding='utf-8')
    lines = content.splitlines()
    
    # 1. Build map of header text (normalized) -> canonical slug
    in_code = False
    header_map = {}
    for line in lines:
        if line.strip().startswith('```'):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = re.match(r'^(#{1,6})\s+(.+)$', line)
        if m:
            raw_title = m.group(2).strip()
            slug = gh_slug(raw_title)
            
            # Variations of title to match TOC labels
            # Clean title
            clean_title = re.sub(r'[\U00010000-\U0010ffff\u2600-\u26ff\u2700-\u27bf\u200d\ufe0f]', '', raw_title).strip()
            header_map[clean_title.lower()] = slug
            # Also store without numbering (e.g. "1. System Prerequisites" -> "system prerequisites")
            no_num = re.sub(r'^\d+(\.\d+)*\s*', '', clean_title).strip().lower()
            header_map[no_num] = slug
            header_map[raw_title.lower()] = slug

    # 2. Update TOC lines: - [Label](#old-slug)
    new_lines = []
    toc_pattern = re.compile(r'^(\s*-\s+\[)([^\]]+)(\]\(#)([^\)]+)(\)\s*)$')

    for line in lines:
        m = toc_pattern.match(line)
        if m:
            prefix, label, hash_prefix, old_slug, suffix = m.groups()
            clean_label = re.sub(r'[\U00010000-\U0010ffff\u2600-\u26ff\u2700-\u27bf\u200d\ufe0f]', '', label).strip()
            
            # Find best matching slug
            target_slug = None
            if clean_label.lower() in header_map:
                target_slug = header_map[clean_label.lower()]
            elif label.lower() in header_map:
                target_slug = header_map[label.lower()]
            else:
                # Try direct slugification of the label
                direct_slug = gh_slug(label)
                target_slug = direct_slug
            
            new_line = f"{prefix}{label}{hash_prefix}{target_slug}{suffix}"
            new_lines.append(new_line)
        else:
            # Also check badge links or inline links at the top like (#endpoint-catalog)
            # Replace badge links if needed
            new_lines.append(line)

    filepath.write_text("\n".join(new_lines) + "\n", encoding='utf-8')
    print(f"Updated TOC in {filepath.name}")

for p in ['README.md', 'docs/architecture.md', 'docs/api_specification.md', 'docs/setup_and_deployment.md', 'docs/user_guide.md', 'docs/multilingual_support.md']:
    update_file_toc(ROOT / p)
