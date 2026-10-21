"""Local-only Unix socket model broker boundary prototype.

This broker deliberately does not forward to any external model provider.
A production provider adapter must be separate, authenticated and allowlisted.
"""
import json,os,socket,threading
from pathlib import Path

MAX_BYTES=16384
class BrokerDenied(Exception):pass

def adjudicate(data):
    if not isinstance(data,dict) or set(data)!={'op','model','prompt'}:raise BrokerDenied('invalid_schema')
    if data['op']!='infer' or data['model']!='gauntlet-fixture-v1':raise BrokerDenied('model_not_allowlisted')
    if not isinstance(data['prompt'],str) or len(data['prompt'])>4096:raise BrokerDenied('prompt_size')
    # Deterministic fixture only. Not a real agent or a model evaluation.
    return {'kind':'fixture_response','text':'DENY','real_model':False}

def serve_once(sock_path,ready):
    with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as server:
        server.bind(str(sock_path));os.chmod(sock_path,0o600);server.listen(1);server.settimeout(15);ready.set()
        conn,_=server.accept()
        with conn:
            conn.settimeout(5);raw=conn.recv(MAX_BYTES+1)
            try:
                if len(raw)>MAX_BYTES:raise BrokerDenied('request_too_large')
                response={'ok':True,'result':adjudicate(json.loads(raw))}
            except (ValueError,TypeError,BrokerDenied) as exc:response={'ok':False,'error':str(exc)}
            conn.sendall(json.dumps(response).encode())

def client(path,request):
    with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as sock:
        sock.settimeout(5);sock.connect(str(path));sock.sendall(json.dumps(request).encode());return json.loads(sock.recv(MAX_BYTES))