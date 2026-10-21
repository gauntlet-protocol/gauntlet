#!/usr/bin/env python3
"""Optional, read-only GAUNTLET MCP stdio adapter. No core dependency."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = [
    {"name": "gauntlet_list_challenges", "description": "List public challenge IDs and lifecycle states", "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}},
    {"name": "gauntlet_get_challenge", "description": "Get a public challenge manifest by ID", "inputSchema": {"type": "object", "properties": {"id": {"type": "string", "pattern": "^[0-9]{3}$"}}, "required": ["id"], "additionalProperties": False}},
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
