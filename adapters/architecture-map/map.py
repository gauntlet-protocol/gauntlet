"""Read-only candidate mapping. No claim of architectural compliance."""
import re
from pathlib import Path

ID = re.compile(r'\b([A-Z][A-Z0-9]{1,15}[-_][0-9]{2,6})\b')
EXT = {'.rs', '.py', '.go', '.js', '.ts', '.java', '.cs', '.cpp', '.c', '.h'}
MAX_FILES = 300
MAX_SOURCE_BYTES = 1_000_000
STOP = {'must', 'shall', 'should', 'the', 'and', 'with', 'from', 'that', 'this', 'into', 'when', 'code', 'system', 'architecture', 'requirement', 'return', 'true', 'false'}

def tokens(text):
    return {x for x in re.findall(r'[a-z][a-z0-9]{3,}', text.lower().replace('_', ' ')) if x not in STOP}

def report(document, repo):
    root = Path(repo).resolve()
    if not root.is_dir():
        raise ValueError('code directory unavailable')
    inventory = {}
    for section in document['sections']:
        for line in section['text'].splitlines():
            for match in ID.finditer(line):
                rid = match.group(1)
                entry = inventory.setdefault(rid, {'id': rid, 'claims': [], 'candidate_code': [], 'candidate_tests': [], 'semantic_candidates': [], 'status': 'UNVERIFIED'})
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
        claim_terms = tokens(' '.join(x['text'] for x in entry['claims']))
        for name, content in source:
            is_test = 'test' in Path(name).stem.lower() or any(part in {'tests', '__tests__'} for part in Path(name).parts)
            for line_no, line in enumerate(content.splitlines(), 1):
                if entry['id'] in line:
                    key = 'candidate_tests' if is_test else 'candidate_code'
                    if len(entry[key]) < 20:
                        entry[key].append({'path': name, 'line': line_no, 'snippet': line[:200]})
                # Lexical overlap only. Require >=2 meaningful words; not semantic proof.
                overlap = sorted(claim_terms & tokens(line))
                if len(overlap) >= 2 and len(entry['semantic_candidates']) < 10:
                    entry['semantic_candidates'].append({'path': name, 'line': line_no, 'overlap': overlap[:10], 'classification': 'LEXICAL_HINT_ONLY'})
        if entry['candidate_code'] or entry['candidate_tests']:
            entry['status'] = 'CANDIDATE_REFERENCE_ONLY'
        elif entry['semantic_candidates']:
            entry['status'] = 'LEXICAL_HINT_ONLY'
    return {'schema': 'gauntlet-architecture-gap-v0.2', 'document_sha256': document['sha256'], 'requirements': list(inventory.values()), 'scanned_files': len(source), 'assurance': 'UNVERIFIED', 'limitations': ['Literal references and lexical overlap do not prove implementation or tests pass', 'Unreferenced requirements may still be implemented; no absence proof', 'No code execution, test execution, AST analysis or semantic model inference']}
