"""Conservative architecture requirement inventory and source-code candidate mapping."""
import hashlib
import re
from pathlib import Path

ID = re.compile(r'\b([A-Z][A-Z0-9]{1,15}[-_][0-9]{2,6})\b')
EXT = {'.rs', '.py', '.go', '.js', '.ts', '.java', '.cs', '.cpp', '.c', '.h'}
MAX_FILES = 300
MAX_SOURCE_BYTES = 1_000_000

def report(document, repo):
    root = Path(repo).resolve()
    if not root.is_dir():
        raise ValueError('code directory unavailable')
    inventory = {}
    for section in document['sections']:
        for line in section['text'].splitlines():
            for match in ID.finditer(line):
                rid = match.group(1)
                entry = inventory.setdefault(rid, {'id': rid, 'claims': [], 'candidate_code': [], 'status': 'UNVERIFIED'})
                if len(entry['claims']) < 10:
                    entry['claims'].append({'location': section['location'], 'text': line[:500]})
    source = []
    for p in sorted(root.rglob('*')):
        if any(part in {'.git', 'target', 'node_modules', '.venv', '__pycache__'} for part in p.relative_to(root).parts):
            continue
        if p.is_symlink() or not p.is_file() or p.suffix not in EXT:
            continue
        if len(source) >= MAX_FILES:
            raise ValueError('repository scan exceeds file limit')
        if p.stat().st_size > MAX_SOURCE_BYTES:
            continue
        try:
            content = p.read_text(encoding='utf-8')
        except UnicodeError:
            continue
        source.append((p.relative_to(root).as_posix(), content))
    for entry in inventory.values():
        for name, content in source:
            for line_no, line in enumerate(content.splitlines(), 1):
                if entry['id'] in line and len(entry['candidate_code']) < 20:
                    entry['candidate_code'].append({'path': name, 'line': line_no, 'snippet': line[:200]})
        if entry['candidate_code']:
            entry['status'] = 'CANDIDATE_REFERENCE_ONLY'
    return {'schema': 'gauntlet-architecture-gap-v0.1', 'document_sha256': document['sha256'], 'requirements': list(inventory.values()), 'scanned_files': len(source), 'assurance': 'UNVERIFIED', 'limitations': ['Exact requirement-ID references are candidates only, not implementation evidence', 'Unreferenced requirements may still be implemented; no absence proof', 'No test execution, static analysis, or semantic architecture verification']}
