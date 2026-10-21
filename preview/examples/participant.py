#!/usr/bin/env python3
"""Optional process-adapter example, never imported by Rust core."""
import json
import sys
request = json.load(sys.stdin)
if request['protocol'] != 'gauntlet-process-v0.1':
    sys.exit(1)
doc = request['untrusted_document']
challenge = request['challenge_id']
if challenge == '003':
    answer = doc.split()[0]
elif challenge == '009':
    answer = 'ALLOW' if 'actor=analyst;action=read;resource=public;grant=valid' in doc else 'DENY'
elif challenge == '029':
    answer = next((p[7:] for p in doc.split(';') if p.startswith('result=')), '')
else:
    sys.exit(2)
print(json.dumps({'protocol': 'gauntlet-process-v0.1', 'case_id': request['case_id'], 'answer': answer}))
