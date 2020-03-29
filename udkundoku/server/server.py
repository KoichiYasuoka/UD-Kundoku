# coding=utf-8

import os
from pkg_resources import get_distribution
from http.server import BaseHTTPRequestHandler
from http import HTTPStatus
from urllib.parse import unquote
import udkundoku
import unidic2ud

PACKAGE_DIR=os.path.abspath(os.path.dirname(__file__))
VERSION="HTTP UD-Kundoku/"+get_distribution("udkundoku").version
LZH=udkundoku.load()
QKANA=unidic2ud.load("qkana")

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
    elif p.endswith(".txt"):
      if p.startswith("%"):
        s=unquote(p[:-6])
        if self.last_string!=s:
          self.last_string=s
          self.last_UD=LZH(s)
          self.translate=""
        if p.endswith(".0.txt"):
          r=str(self.last_UD)
        elif p.endswith(".1.txt"):
          r=str(udkundoku.reorder(self.last_UD))
        elif p.endswith(".2.txt"):
          r=udkundoku.translate(self.last_UD,raw=True)
          i=r.index("# text = ")
          self.translate=r[i+9:r.index("\n",i)]
        elif p.endswith(".3.txt"):
          r=self.translate
          if not r.endswith("\n"):
            if r=="":
              r=udkundoku.translate(self.last_UD,raw=True)
              i=r.index("# text = ")
              r=r[i+9:r.index("\n",i)]
            r=QKANA(r,raw=True)
          self.translate=r
        else:
          r=""
          self.last_string=None
      else:
        r=""
        self.last_string=None
      t="text/plain;charset=UTF-8"
    elif p.endswith(".ico"):
      self.send_response(HTTPStatus.NOT_FOUND)
      return
    else:
      f=open(os.path.join(PACKAGE_DIR,"index.html"),"r",encoding="utf-8")
      r=f.read()
      f.close()
      t="text/html;charset=UTF-8"
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

