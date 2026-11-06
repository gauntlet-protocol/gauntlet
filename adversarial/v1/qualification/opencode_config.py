"""Credential-free OpenCode config for a sandboxed HTTP bridge.
The HTTP bridge must be separately implemented and verified before inference.
"""
import json

def config(base_url='http://127.0.0.1:8787/v1'):
    if base_url!='http://127.0.0.1:8787/v1':raise ValueError('nonlocal_endpoint_denied')
    return {'$schema':'https://opencode.ai/config.json','plugin':[],'permission':{'*':'deny'},'provider':{'gauntlet':{'npm':'@ai-sdk/openai-compatible','name':'GAUNTLET fixture bridge','options':{'baseURL':base_url,'apiKey':'gauntlet-synthetic-no-privileges'},'models':{'gauntlet-fixture-v1':{'name':'GAUNTLET fixture (not real inference)'}}}},'model':'gauntlet/gauntlet-fixture-v1'}
if __name__=='__main__':print(json.dumps(config(),indent=2))