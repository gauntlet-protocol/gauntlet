#!/usr/bin/env python3
"""Optional, read-only GAUNTLET MCP stdio adapter. No core dependency."""
import json
import sys
import os
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# The MCP client cannot pick arbitrary filesystem paths. Operator controls the root.
INPUT_ROOT = Path(os.environ.get('GAUNTLET_ARCHITECTURE_ROOT', str(ROOT / 'starter'))).resolve()
CODE_ROOT = Path(os.environ.get('GAUNTLET_CODE_ROOT', str(ROOT / 'starter'))).resolve()
MAX_RESULT_CHARS = 100_000

def ingest_allowed_file(name):
    if not isinstance(name, str) or not name or len(name) > 255 or '/' in name or '\\' in name or name in ('.', '..'):
        raise ValueError('filename must be a single basename in configured input directory')
    if not INPUT_ROOT.is_dir():
        raise ValueError('configured architecture input directory missing')
    path = INPUT_ROOT / name
    if path.is_symlink() or not path.is_file() or path.resolve().parent != INPUT_ROOT:
        raise ValueError('input must be a regular file directly inside configured input directory')
    spec = importlib.util.spec_from_file_location('gauntlet_ingest', ROOT / 'adapters/architecture-ingest/ingest.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.parse(path)
    size = sum(len(x['text']) for x in result['sections'])
    if size > MAX_RESULT_CHARS:
        raise ValueError('extracted document too large for MCP response; use ingestion CLI')
    return result

TOOLS = [
    {"name": "gauntlet_list_challenges", "description": "List public challenge IDs and lifecycle states", "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}},
    {"name": "gauntlet_get_challenge", "description": "Get a public challenge manifest by ID", "inputSchema": {"type": "object", "properties": {"id": {"type": "string", "pattern": "^[0-9]{3}$"}}, "required": ["id"], "additionalProperties": False}},
    {"name": "gauntlet_get_started", "description": "Get local MCP setup, runner commands and architecture-to-code starter without executing code", "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}},
    {"name": "gauntlet_get_starter", "description": "Read a minimal participant adapter scaffold and architecture mapping worksheet", "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}},
    {"name": "gauntlet_parse_architecture", "description": "Read a document by basename from the operator-configured local input directory; returns untrusted extracted text and provenance", "inputSchema": {"type": "object", "properties": {"filename": {"type": "string", "maxLength": 255}}, "required": ["filename"], "additionalProperties": False}},
    {"name": "gauntlet_map_architecture", "description": "Inventory explicit requirement IDs and find candidate references in operator-approved code root; never asserts compliance", "inputSchema": {"type": "object", "properties": {"filename": {"type": "string", "maxLength": 255}}, "required": ["filename"], "additionalProperties": False}},
    {"name": "gauntlet_get_guides", "description": "Find contribution, proof and evaluator guides", "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}},
]

def handle(req):
    method = req.get('method')
    if method == 'initialize':
        return {'protocolVersion': '2025-06-18', 'capabilities': {'tools': {'listChanged': False}}, 'serverInfo': {'name': 'gauntlet-readonly', 'version': '0.1.0'}}
    if method == 'ping':
        return {}
    if method == 'tools/list':
        return {'tools': TOOLS}
    if method == 'tools/call':
        params = req.get('params', {})
        name = params.get('name')
        args = params.get('arguments', {})
        if name == 'gauntlet_list_challenges' and args == {}:
            data = [{'id': p.parent.name, 'manifest': json.loads(p.read_text())} for p in sorted((ROOT/'season1/challenges').glob('*/manifest.json'))]
        elif name == 'gauntlet_get_challenge' and isinstance(args, dict) and set(args) == {'id'} and isinstance(args['id'], str) and len(args['id']) == 3 and args['id'].isascii() and args['id'].isdigit():
            p = ROOT/'season1/challenges'/args['id']/'manifest.json'
            if not p.is_file():
                return {'content': [{'type': 'text', 'text': 'Unknown public challenge ID'}], 'isError': True}
            data = json.loads(p.read_text())
        elif name == 'gauntlet_get_started' and args == {}:
            data = {'mcp_command': 'python3 adapters/mcp/server.py', 'adapter_docs': 'adapters/mcp/README.md', 'starter': 'starter/architecture-to-code/README.md', 'run_command': 'cargo run -p gauntlet-runner -- run-external 003 /tmp/result.json python3 /path/to/participant.py', 'verify_command': 'cargo run -p gauntlet-runner -- verify-local /tmp/result.json', 'assurance': 'LOCAL', 'release_status': 'PRIVATE / NOT RELEASED'}
        elif name == 'gauntlet_get_starter' and args == {}:
            data = {'guide': (ROOT/'starter/architecture-to-code/README.md').read_text(), 'participant_python': (ROOT/'starter/architecture-to-code/participant.py').read_text(), 'status': 'SCAFFOLDED / NOT RUNNABLE UNTIL IMPLEMENTED'}
        elif name == 'gauntlet_parse_architecture' and isinstance(args, dict) and set(args) == {'filename'}:
            try:
                data = ingest_allowed_file(args['filename'])
            except (ValueError, OSError, ImportError, UnicodeError) as exc:
                return {'content': [{'type': 'text', 'text': 'Architecture ingestion rejected: ' + str(exc)}], 'isError': True}
        elif name == 'gauntlet_map_architecture' and isinstance(args, dict) and set(args) == {'filename'}:
            try:
                document = ingest_allowed_file(args['filename'])
                spec = importlib.util.spec_from_file_location('gauntlet_map', ROOT / 'adapters/architecture-map/map.py')
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                data = module.report(document, CODE_ROOT)
            except (ValueError, OSError, ImportError, UnicodeError) as exc:
                return {'content': [{'type': 'text', 'text': 'Architecture mapping rejected: ' + str(exc)}], 'isError': True}
        elif name == 'gauntlet_get_guides' and args == {}:
            data = {'contributing': 'season1/governance/CONTRIBUTING.md', 'evaluators': 'preview/EVALUATORS.md', 'proof': 'preview/PROOF_PROTOCOL.md', 'trust': 'preview/ADR-0002-federated-trust.md', 'status': 'PRIVATE / NOT RELEASED'}
        else:
            return {'content': [{'type': 'text', 'text': 'Unsupported tool or invalid arguments'}], 'isError': True}
        return {'content': [{'type': 'text', 'text': json.dumps(data, sort_keys=True)}]}
    raise ValueError('Method not found')

def serve():
    for line in sys.stdin:
        try:
            req = json.loads(line)
            if not isinstance(req, dict) or req.get('jsonrpc') != '2.0':
                continue
            if req.get('method', '').startswith('notifications/'):
                continue
            result = handle(req)
            if 'id' in req:
                response = {'jsonrpc': '2.0', 'id': req['id'], 'result': result}
            else:
                continue
        except (ValueError, TypeError, KeyError, OSError) as exc:
            if not isinstance(locals().get('req'), dict) or 'id' not in req:
                continue
            response = {'jsonrpc': '2.0', 'id': req['id'], 'error': {'code': -32601, 'message': str(exc)}}
        print(json.dumps(response, separators=(',', ':')), flush=True)

if __name__ == '__main__':
    serve()
