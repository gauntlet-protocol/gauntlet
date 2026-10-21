#!/usr/bin/env python3
"""Minimal adapter scaffold: deliberately NOT a passing agent implementation."""
import json
import sys

def answer(request):
    # Replace with real agent/system invocation. Do not hardcode GAUNTLET answers.
    raise NotImplementedError('Connect your actual implementation before running challenges')

def main():
    request = json.load(sys.stdin)
    if request.get('protocol') != 'gauntlet-process-v0.1':
        raise ValueError('unsupported protocol')
    result = answer(request)
    if not isinstance(result, str):
        raise TypeError('answer must be a string')
    print(json.dumps({'protocol': 'gauntlet-process-v0.1', 'case_id': request['case_id'], 'answer': result}))

if __name__ == '__main__':
    main()
