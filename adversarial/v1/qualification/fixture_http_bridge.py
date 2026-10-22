"""Synthetic OpenAI-compatible HTTP fixture for transport testing ONLY.
No real model, no external network, no assurance or attestation.
"""
import json
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
class FixtureHandler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_POST(self):
  if self.path!='/v1/chat/completions':return self.reply(404,{'error':{'message':'not_found'}})
  try:
   if self.headers.get('Authorization')!='Bearer gauntlet-synthetic-no-privileges':return self.reply(403,{'error':{'message':'not_authorized'}})
   length=int(self.headers.get('Content-Length','0'))
   if not 0<length<=16384:return self.reply(413,{'error':{'message':'request_size'}})
   data=json.loads(self.rfile.read(length))
   if data.get('model')!='gauntlet-fixture-v1' or not isinstance(data.get('messages'),list):return self.reply(403,{'error':{'message':'model_denied'}})
   self.server.observed.append({'model':data['model'],'message_count':len(data['messages']),'fixture':True})
   self.reply(200,{'id':'gauntlet-fixture','object':'chat.completion','created':0,'model':'gauntlet-fixture-v1','choices':[{'index':0,'message':{'role':'assistant','content':'DENY'},'finish_reason':'stop'}],'usage':{'prompt_tokens':0,'completion_tokens':0,'total_tokens':0}})
  except (ValueError,TypeError,UnicodeDecodeError):self.reply(400,{'error':{'message':'invalid_request'}})
 def reply(self,status,data):
  body=json.dumps(data).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
def server():
 s=ThreadingHTTPServer(('127.0.0.1',0),FixtureHandler);s.observed=[];return s