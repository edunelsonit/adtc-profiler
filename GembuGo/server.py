#!/usr/bin/env python3
"""Local web server and llama.cpp adapter for GembuGo."""
import json, os, subprocess
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
ROOT=os.path.dirname(os.path.abspath(__file__)); MODEL_PATH=os.getenv('MODEL_PATH',''); LLAMA_CLI=os.getenv('LLAMA_CLI','llama-cli')
PORT=int(os.getenv('PORT','8000'))
SYSTEM='You are GembuGo Tutor, a concise, encouraging offline educational assistant. Use plain language and practical examples.'
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw): super().__init__(*a,directory=ROOT,**kw)
 def respond(self,data,status=200):
  raw=json.dumps(data).encode();self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
 def do_GET(self):
  if self.path=='/api/status':
   ready=bool(MODEL_PATH and os.path.isfile(MODEL_PATH));self.respond({'available':ready,'engine':'llama.cpp','model':os.path.basename(MODEL_PATH) if ready else None})
  else: super().do_GET()
 def do_POST(self):
  if self.path!='/api/chat': self.send_error(404);return
  try:
   length=int(self.headers.get('Content-Length','0'))
   if length > 8000: self.respond({'error':'Please keep your question under 8,000 characters.'},413);return
   body=json.loads(self.rfile.read(length)); message=body.get('message','').strip()
   if not message: self.respond({'error':'A message is required.'},400);return
   if len(message)>4000: self.respond({'error':'Please keep your question under 4,000 characters.'},413);return
   if not (MODEL_PATH and os.path.isfile(MODEL_PATH)): self.respond({'error':'No local GGUF model is configured. Set MODEL_PATH and restart the server.'},503);return
   prompt=f'<|system|>\n{SYSTEM}\n<|user|>\n{message}\n<|assistant|>\n'
   run=subprocess.run([LLAMA_CLI,'-m',MODEL_PATH,'-p',prompt,'-n','256','--temp','0.3','--no-display-prompt'],capture_output=True,text=True,timeout=120,check=False)
   if run.returncode: raise RuntimeError(run.stderr[-500:] or 'llama.cpp exited unexpectedly')
   self.respond({'answer':run.stdout.strip(),'local':True})
  except subprocess.TimeoutExpired: self.respond({'error':'The local model took too long to respond.'},504)
  except Exception as e: self.respond({'error':str(e)},500)
if __name__=='__main__':
 print(f'GembuGo local server: http://127.0.0.1:{PORT}');ThreadingHTTPServer(('127.0.0.1',PORT),Handler).serve_forever()
