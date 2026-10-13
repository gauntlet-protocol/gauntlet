"""GAUNTLET-CAPTURE CAP-03: cumulative normative regression detector."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False)

def digest(obj):
    return hashlib.sha256(canonical(obj).encode('utf-8')).hexdigest()

def evaluate(history):
    if not isinstance(history, dict):
        raise ValueError('history must be object')
    baseline = history.get('baseline')
    amendments = history.get('amendments')
    if not isinstance(baseline, dict) or not isinstance(amendments, list):
        raise ValueError('baseline must be object, amendments list')
    required = baseline.get('protected_counterexamples')
    if not isinstance(required, dict) or not required or any(not isinstance(k,str) or not isinstance(v,bool) for k,v in required.items()):
        raise ValueError('protected_counterexamples must map IDs to boolean detected states')
    if not all(required.values()):
        raise ValueError('baseline must detect every protected counterexample')
    state = dict(required)
    seen = set()
    transitions = []
    earliest = {}
    for index, amend in enumerate(amendments, start=1):
        if not isinstance(amend, dict) or not isinstance(amend.get('id'), str) or not amend['id'] or amend['id'] in seen:
            raise ValueError('amendments need unique nonempty string IDs')
        seen.add(amend['id'])
        changes = amend.get('detected')
        if not isinstance(changes, dict) or any(k not in required or not isinstance(v,bool) for k,v in changes.items()):
            raise ValueError('detected must map known protected IDs to booleans')
        before = dict(state)
        state.update(changes)
        lost = sorted(k for k in required if required[k] and not state[k])
        newly_lost = sorted(k for k in lost if before[k])
        restored = sorted(k for k in required if not before[k] and state[k])
        for k in newly_lost:
            earliest.setdefault(k, amend['id'])
        transitions.append({'amendment':amend['id'],'step':index,'newly_lost':newly_lost,'restored':restored,'cumulative_lost':lost,'state_sha256':digest(state)})
    final_lost = sorted(k for k in required if required[k] and not state[k])
    ever_lost = sorted(set(k for entry in transitions for k in entry['cumulative_lost']))
    return {'protocol':'GAUNTLET-CAPTURE-001/CAP-03','schema_version':1,
            'input_sha256':digest(history),'baseline_sha256':digest(required),
            'status':'FAIL' if ever_lost else 'PASS',
            'final_lost':final_lost,'ever_lost':ever_lost,
            'first_loss_by_counterexample':{k:earliest[k] for k in sorted(earliest)},
            'transitions':transitions,
            'scope':'declared protected counterexamples only; does not establish real-world capture'}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('history', type=Path)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    try:
        report=evaluate(json.loads(args.history.read_text(encoding='utf-8')))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        report={'protocol':'GAUNTLET-CAPTURE-001/CAP-03','status':'INSUFFICIENT_EVIDENCE','error':str(exc)}
    data=json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+'\n'
    if args.output:
        args.output.write_text(data,encoding='utf-8')
    else:
        print(data,end='')
    return 0 if report['status']=='PASS' else (2 if report['status']=='FAIL' else 3)

if __name__=='__main__':
    raise SystemExit(main())
