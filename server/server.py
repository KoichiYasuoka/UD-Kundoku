# coding=utf-8

import os
from pkg_resources import get_distribution
from http.server import BaseHTTPRequestHandler
from http import HTTPStatus
from urllib.parse import unquote
import udkundoku

PACKAGE_DIR=os.path.abspath(os.path.dirname(__file__))
VERSION="HTTP UD-Kundoku/"+get_distribution("udkundoku").version
LZH=udkundoku.load()

class UDKundokuRequestHandler(BaseHTTPRequestHandler):
  server_version=VERSION
  last_string=None
  def do_GET(self):
    p=self.path
    p=p[p.rfind("/")+1:]
    if p.endswith(".js"):
      f=open(os.path.join(PACKAGE_DIR,p),"r",encoding="utf-8")
      r=f.read()
      f.close()
      t="application/javascript"
    elif p.startswith("0."):
      s=unquote(p[2:])
      if self.last_string!=s:
        self.last_UD=LZH(s)
      r=str(self.last_UD)
      t="text/plain;charset=UTF-8";
    elif p.startswith("1."):
      s=unquote(p[2:])
      if self.last_string!=s:
        self.last_UD=LZH(s)
      r=str(udkundoku.rearrange(self.last_UD))
      t="text/plain;charset=UTF-8";
    elif p.startswith("2."):
      s=unquote(p[2:])
      if self.last_string!=s:
        self.last_UD=LZH(s)
      r=udkundoku.translate(self.last_UD,raw=True)
      t="text/plain;charset=UTF-8";
    else:
      f=open(os.path.join(PACKAGE_DIR,"index.html"),"r",encoding="utf-8")
      r=f.read()
      f.close()
      t="text/html;charset=UTF-8";
    b=r.encode("utf-8")
    self.send_response(HTTPStatus.OK)
    self.send_header("Content-Type",t)
    self.send_header("Content-Length",str(len(b)))
    self.end_headers()
    self.wfile.write(b)

def run(port=5000):
  import sys
  from http.server import HTTPServer
  httpd=HTTPServer(("",port),UDKundokuRequestHandler)
  print("http://127.0.0.1:"+str(port)+"   "+VERSION,file=sys.stderr)
  try:
    httpd.serve_forever()
  except:
    quit()

