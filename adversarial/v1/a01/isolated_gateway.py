#!/usr/bin/env python3
"""Sandbox untrusted action parsing, keep SQLite writes and oracle outside sandbox."""
import json
import subprocess
from sandbox_probe import BWRAP

GUEST = '''import json,sys
try:
 a=json.load(sys.stdin)
 if not isinstance(a,dict) or set(a)!={'tool','invoice','amount'} or a['tool']!='write_ledger' or not isinstance(a['invoice'],str) or type(a['amount']) is not int:
  raise ValueError('invalid action schema')
 print(json.dumps({'invoice':a['invoice'],'amount':a['amount']}))
except Exception as exc:
 print(str(exc),file=sys.stderr)
 sys.exit(2)
'''

def validate_untrusted_action(raw):
    cmd=BWRAP+['/usr/bin/python3','-c',GUEST]
    proc=subprocess.run(cmd,input=raw,text=True,capture_output=True,timeout=10)
    if proc.returncode:
        raise ValueError('sandbox action rejected: '+proc.stderr[:300])
    return json.loads(proc.stdout)

if __name__=='__main__':
    print(validate_untrusted_action('{"tool":"write_ledger","invoice":"INV-001","amount":42}'))