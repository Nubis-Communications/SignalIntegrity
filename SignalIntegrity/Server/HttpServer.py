"""
HttpServer.py
"""
# Copyright (c) 2026 Nubis Communications, Inc.
# All rights reserved worldwide.
#
# This file is part of SignalIntegrity.
#
# SignalIntegrity is free software: You can redistribute it and/or modify it under the terms
# of the GNU General Public License as published by the Free Software Foundation, either
# version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>
import hmac
import json
import math
import os
import secrets
import threading
import traceback
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

from SignalIntegrity.Server.Api import Api, ApiError

UI_DIR=os.path.join(os.path.dirname(os.path.realpath(__file__)),'ui')
MAX_BODY=1<<20
STATIC_TYPES={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8',
              '.css':'text/css; charset=utf-8','.svg':'image/svg+xml','.png':'image/png','.ico':'image/x-icon'}
CSP=("default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
     "connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")

def _Finite(obj):
    """replaces NaN and infinities, which JSON cannot represent, with None"""
    if isinstance(obj,float):
        return obj if math.isfinite(obj) else None
    if isinstance(obj,dict):
        return {k:_Finite(v) for k,v in obj.items()}
    if isinstance(obj,(list,tuple)):
        return [_Finite(v) for v in obj]
    return obj

class Handler(BaseHTTPRequestHandler):
    server_version='SignalIntegrityServer'
    protocol_version='HTTP/1.1'
    timeout=30
    def log_message(self,format,*args):
        if self.server.verbose:
            BaseHTTPRequestHandler.log_message(self,format,*args)
    def _HostAllowed(self):
        # rejects DNS-rebinding requests that reach 127.0.0.1 under a foreign host name
        host=self.headers.get('Host','')
        port=self.server.server_address[1]
        return host in ('127.0.0.1:%d'%port,'localhost:%d'%port)
    def _Send(self,status,body,contentType='application/json; charset=utf-8'):
        if isinstance(body,str):
            body=body.encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type',contentType)
        self.send_header('Content-Length',str(len(body)))
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Referrer-Policy','no-referrer')
        self.send_header('Content-Security-Policy',CSP)
        # an unread request body would otherwise be parsed as the next request on this connection
        self.send_header('Connection','close')
        self.close_connection=True
        self.end_headers()
        self.wfile.write(body)
    def _Json(self,status,obj):
        try:
            text=json.dumps(obj,allow_nan=False)
        except ValueError:
            text=json.dumps(_Finite(obj),allow_nan=False)
        self._Send(status,text)
    def do_GET(self):
        if not self._HostAllowed():
            return self._Send(403,'forbidden','text/plain')
        path=self.path.split('?',1)[0].split('#',1)[0]
        if path=='/':
            path='/index.html'
        full=os.path.realpath(os.path.join(UI_DIR,path.lstrip('/')))
        ext=os.path.splitext(full)[1].lower()
        if not full.startswith(UI_DIR+os.sep) or ext not in STATIC_TYPES or not os.path.isfile(full):
            return self._Send(404,'not found','text/plain')
        with open(full,'rb') as f:
            self._Send(200,f.read(),STATIC_TYPES[ext])
    def do_POST(self):
        if not self._HostAllowed():
            return self._Json(403,{'error':'forbidden host'})
        origin=self.headers.get('Origin')
        if origin is not None and origin!='http://'+self.headers.get('Host',''):
            return self._Json(403,{'error':'forbidden origin'})
        authorization=self.headers.get('Authorization','')
        if not hmac.compare_digest(authorization.encode(),('Bearer '+self.server.token).encode()):
            return self._Json(401,{'error':'unauthorized'})
        if not self.path.startswith('/api/'):
            return self._Json(404,{'error':'not found'})
        try:
            length=int(self.headers.get('Content-Length','0'))
        except ValueError:
            return self._Json(400,{'error':'bad content length'})
        if length>MAX_BODY:
            return self._Json(413,{'error':'request too large'})
        if 'application/json' not in self.headers.get('Content-Type',''):
            return self._Json(415,{'error':'content type must be application/json'})
        try:
            params=json.loads(self.rfile.read(length) or b'{}')
        except ValueError:
            return self._Json(400,{'error':'invalid JSON'})
        try:
            result=self.server.api.Dispatch(self.path[len('/api/'):],params)
        except ApiError as e:
            return self._Json(e.status,{'error':str(e)})
        except Exception as e:
            if self.server.verbose:
                traceback.print_exc()
            return self._Json(500,{'error':'internal error: '+str(e)})
        self._Json(200,{'result':result})

class SignalIntegrityServer(ThreadingHTTPServer):
    daemon_threads=True
    def __init__(self,port=0,token=None,api=None,verbose=False):
        ThreadingHTTPServer.__init__(self,('127.0.0.1',port),Handler)
        self.token=token or secrets.token_urlsafe(32)
        self.api=Api() if api is None else api
        self.verbose=verbose
    @property
    def port(self):
        return self.server_address[1]
    def Url(self):
        return 'http://127.0.0.1:%d/#token=%s'%(self.port,self.token)
    def StartInThread(self):
        thread=threading.Thread(target=self.serve_forever,daemon=True)
        thread.start()
        return thread
