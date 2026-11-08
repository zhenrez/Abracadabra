"""Loopback-only SUNNY visuals and explicit offline AgentJev decisions."""
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit, unquote
import argparse, json, mimetypes
from jev_tool import evaluate, http, validate_info, validate_request

ROOT=Path(__file__).resolve().parents[1]
WEB=ROOT/'web/delivery-2026-11-07'

def asset_path(url_path):
    decoded=unquote(urlsplit(url_path).path)
    if '\\' in decoded or ':' in decoded or '\x00' in decoded: raise ValueError('Invalid asset path')
    target=(WEB/decoded.lstrip('/')).resolve()
    if not target.is_relative_to(WEB.resolve()): raise ValueError('Asset outside delivery')
    if target==WEB.resolve():target=target/'index.html'
    if target.suffix.lower() not in ('.html','.js','.css','.json','.svg','.png','.jpg','.wav','.mp3'):
        raise ValueError('Unsupported asset')
    return target

def decision_payload(value):
    if not isinstance(value,dict) or set(value)-{'state','questions'}:
        raise ValueError('Only local state/questions are accepted')
    # JSON numeric exponents can overflow even when no NaN/Infinity token appears.
    json.dumps(value,allow_nan=False)
    validate_request(value)
    return value

def handler_for(port):
    origins={f'http://127.0.0.1:{port}',f'http://localhost:{port}'}
    hosts={f'127.0.0.1:{port}',f'localhost:{port}'}
    class Handler(BaseHTTPRequestHandler):
        def reply(self,status,value):
            raw=json.dumps(value,ensure_ascii=False,allow_nan=False).encode('utf8')
            self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8')
            self.send_header('Content-Length',str(len(raw)));self.send_header('Cache-Control','no-store')
            self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(raw)
        def local_host(self):return self.headers.get('Host') in hosts
        def do_GET(self):
            if not self.local_host():self.reply(403,{'error':'Local host required'});return
            if self.path=='/api/jev/info':
                try:
                    info=http('/api/info',timeout=6);validate_info(info)
                    self.reply(200,{'provider':'local','model':info,'billing':'No hosted API request','liveInferencePerformed':False})
                except Exception as exc:self.reply(503,{'status':'unavailable','category':type(exc).__name__,'liveInferencePerformed':False})
                return
            if self.path=='/health':self.reply(200,{'status':'ready','application':'SUNNY connected delivery','host':'loopback-only'});return
            try:
                target=asset_path(self.path)
                if not target.is_file():self.reply(404,{'error':'Asset not built'});return
                raw=target.read_bytes();kind=mimetypes.guess_type(target.name)[0]or'application/octet-stream'
                self.send_response(200);self.send_header('Content-Type',kind)
                self.send_header('Content-Length',str(len(raw)));self.send_header('X-Content-Type-Options','nosniff')
                self.send_header('Cache-Control','no-cache');self.end_headers();self.wfile.write(raw)
            except (ValueError,OSError):self.reply(403,{'error':'Invalid or unavailable asset'})
        def do_POST(self):
            if not self.local_host() or self.headers.get('Origin') not in origins or self.headers.get('X-SUNNY-Request')!='local-decision':
                self.reply(403,{'error':'Same-origin explicit local decision required'});return
            if self.path!='/api/jev':self.reply(404,{'error':'Unknown endpoint'});return
            try:
                if self.headers.get('Content-Type','').split(';')[0].strip()!='application/json':raise ValueError('JSON required')
                length=int(self.headers.get('Content-Length','0'))
                if not 0<length<=48000:raise ValueError('Request must be1..48000bytes')
                request=decision_payload(json.loads(self.rfile.read(length),parse_constant=lambda _:(_ for _ in()).throw(ValueError('Finite JSON required'))))
                result=evaluate(request,'SUNNY connected workbench: explicit local AgentJev decision')
                self.reply(200,{'provider':'local',**result,'billing':'No hosted API request','completionCertified':False})
            except (ValueError,TypeError,KeyError):self.reply(400,{'status':'invalid','error':'Invalid bounded local decision request','fallbackDecision':None})
            except Exception as exc:self.reply(503,{'status':'unavailable','category':type(exc).__name__,'fallbackDecision':None})
    return Handler

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--port',type=int,default=8767)
    args=parser.parse_args()
    if not 1024<=args.port<=65535:parser.error('Invalid local port')
    server=ThreadingHTTPServer(('127.0.0.1',args.port),handler_for(args.port))
    print(json.dumps({'status':'serving','url':f'http://127.0.0.1:{args.port}','modelEndpoint':'fixed local127.0.0.1:8149'}),flush=True)
    try:server.serve_forever(poll_interval=0.5)
    except KeyboardInterrupt:pass
    finally:server.server_close()
