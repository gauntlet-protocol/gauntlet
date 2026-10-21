"""Fail-closed structural and linkage checks; never a proof verifier."""
import json
import sys
from pathlib import Path

KINDS = ('CLAIM', 'CONTRACT', 'EXECUTION', 'EVIDENCE', 'VERIFICATION', 'ATTESTATION')
SUBJECT = ('product_id', 'product_version', 'environment_id')


def validate(doc):
    if not isinstance(doc, dict) or set(doc) != {'format', 'subject', 'records'} or doc['format'] != 'gauntlet-claim-chain-v0.1':
        raise ValueError('invalid envelope')
    subject = doc['subject']
    if not isinstance(subject, dict) or set(subject) != set(SUBJECT) or any(not isinstance(subject[k], str) or not subject[k].strip() for k in SUBJECT):
        raise ValueError('invalid subject')
    if not isinstance(doc['records'], list):
        raise ValueError('invalid records')
    ids = {}
    for record in doc['records']:
        if not isinstance(record, dict) or set(record) != {'id', 'kind', 'subject', 'scope', 'version', 'source_ref', 'upstream_id'}:
            raise ValueError('invalid record fields')
        if any(not isinstance(record[k], str) or not record[k].strip() for k in ('id', 'kind', 'scope', 'version', 'source_ref')):
            raise ValueError('invalid record values')
        if record['kind'] not in KINDS or record['id'] in ids or record['subject'] != subject:
            raise ValueError('duplicate id, invalid kind or subject mismatch')
        if record['kind'] == 'CLAIM':
            if record['upstream_id'] is not None:
                raise ValueError('claim must have no upstream')
        elif not isinstance(record['upstream_id'], str) or not record['upstream_id']:
            raise ValueError('missing upstream')
        ids[record['id']] = record
    for record in doc['records']:
        if record['kind'] != 'CLAIM':
            upstream = ids.get(record['upstream_id'])
            if upstream is None or KINDS.index(upstream['kind']) != KINDS.index(record['kind']) - 1:
                raise ValueError('missing or wrong-stage upstream')
            if upstream['scope'] != record['scope']:
                raise ValueError('scope mismatch')
    return 'STRUCTURALLY_VALID_UNVERIFIED'


def reject_duplicates(pairs):
    out = {}
    for k, v in pairs:
        if k in out:
            raise ValueError('duplicate JSON key')
        out[k] = v
    return out


if __name__ == '__main__':
    try:
        print(validate(json.loads(Path(sys.argv[1]).read_text(), object_pairs_hook=reject_duplicates)))
    except (ValueError, KeyError, IndexError, OSError, TypeError) as exc:
        print('INVALID:', exc, file=sys.stderr)
        sys.exit(1)
