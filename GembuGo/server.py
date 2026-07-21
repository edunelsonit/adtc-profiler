#!/usr/bin/env python3
"""Local web server and llama.cpp adapter for GembuGo."""
import base64, html, io, json, os, re, shutil, subprocess, tempfile, zipfile
from collections import Counter
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
ROOT=os.path.dirname(os.path.abspath(__file__)); MODEL_PATH=os.getenv('MODEL_PATH',''); LLAMA_CLI=os.getenv('LLAMA_CLI','llama-cli')
PORT=int(os.getenv('PORT','8000'))
SYSTEM='You are GembuGo Tutor, a concise, encouraging offline educational assistant. Use plain language and practical examples.'
MAX_DOCUMENT_BYTES=20*1024*1024

def summarise(text):
 sentences=re.split(r'(?<=[.!?])\s+',re.sub(r'\s+',' ',text).strip())
 words=re.findall(r"[A-Za-z][A-Za-z'-]{2,}",text.lower())
 common={word for word,count in Counter(words).items() if count>1}
 ranked=sorted(enumerate(sentences),key=lambda item:sum(word.lower().strip(".,;:!?()[]") in common for word in item[1].split()),reverse=True)
 chosen=sorted(ranked[:min(3,len(ranked))])
 return ' '.join(sentence for _,sentence in chosen)[:1400] or text[:1400]

def extract_document(name, raw):
 suffix=os.path.splitext(name.lower())[1]
 if suffix in {'.txt','.md','.csv'}:
  return raw.decode('utf-8',errors='replace')
 if suffix=='.docx':
  with zipfile.ZipFile(io.BytesIO(raw)) as doc:
   xml=doc.read('word/document.xml').decode('utf-8',errors='replace')
  return html.unescape(re.sub(r'<[^>]+>',' ',xml))
 if suffix=='.pdf':
  if not shutil.which('pdftotext'): raise ValueError('PDF reading needs the local pdftotext utility. Upload a text or DOCX file, or install poppler-utils.')
  with tempfile.NamedTemporaryFile(suffix='.pdf') as source:
   source.write(raw);source.flush()
   result=subprocess.run(['pdftotext',source.name,'-'],capture_output=True,text=True,timeout=30,check=False)
  if result.returncode: raise ValueError('Unable to extract text from this PDF. It may be scanned or protected.')
  return result.stdout
 raise ValueError('Supported file types are TXT, Markdown, CSV, PDF, and DOCX.')
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw): super().__init__(*a,directory=ROOT,**kw)
 def respond(self,data,status=200):
  raw=json.dumps(data).encode();self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
 def do_GET(self):
  if self.path=='/api/status':
   ready=bool(MODEL_PATH and os.path.isfile(MODEL_PATH));self.respond({'available':ready,'engine':'llama.cpp','model':os.path.basename(MODEL_PATH) if ready else None})
  else: super().do_GET()
 def do_POST(self):
  if self.path not in {'/api/chat','/api/document'}: self.send_error(404);return
  try:
   length=int(self.headers.get('Content-Length','0'))
   limit=MAX_DOCUMENT_BYTES*2 if self.path=='/api/document' else 8000
   if length > limit: self.respond({'error':'The request is too large.'},413);return
   body=json.loads(self.rfile.read(length)); message=body.get('message','').strip()
   if self.path=='/api/document':
    name=os.path.basename(body.get('name','document'))
    raw=base64.b64decode(body.get('content',''),validate=True)
    if len(raw)>MAX_DOCUMENT_BYTES: self.respond({'error':'Documents must be 5 MB or smaller.'},413);return
    text=extract_document(name,raw).strip()
    if not text: self.respond({'error':'No readable text was found in this document.'},422);return
    self.respond({'name':name,'summary':summarise(text),'text':text[:30000],'truncated':len(text)>30000,'local':True});return
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
