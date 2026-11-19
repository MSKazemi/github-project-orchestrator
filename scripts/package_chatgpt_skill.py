#!/usr/bin/env python3
"""Package the ChatGPT skill source as a portable ZIP without network dependencies."""
import argparse
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'skills'/'chatgpt'/'github-project-orchestrator'

def package(output: Path):
    entry=SRC/'SKILL.md'
    if not entry.is_file() or not entry.read_text().startswith('---\nname: github-project-orchestrator\n'):
        raise ValueError('ChatGPT SKILL.md frontmatter missing or incorrect')
    for name in ['agents/openai.yaml','scripts/github_project_sync.py','assets/project-plan.example.json']:
        if not (SRC/name).is_file():
            raise ValueError('Missing skill file: '+name)
    output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(SRC.rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts:
                z.write(p, arcname=str(Path(SRC.name)/p.relative_to(SRC)))
    print('Packaged',output)

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--output',type=Path,default=ROOT/'skill.zip')
    package(ap.parse_args().output)