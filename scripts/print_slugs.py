import re
from pathlib import Path

def gh_slug(text):
    text = text.strip()
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

ROOT = Path('/home/dev/Desktop/projects/AI-InnovationHackathon')
for p in ['README.md', 'docs/architecture.md', 'docs/api_specification.md', 'docs/setup_and_deployment.md', 'docs/user_guide.md', 'docs/multilingual_support.md']:
    f = ROOT / p
    print(f'=== {p} ===')
    lines = f.read_text(encoding='utf-8').splitlines()
    for l in lines:
        if l.startswith('#'):
            print(f'  {l}  -->  #{gh_slug(l)}')
