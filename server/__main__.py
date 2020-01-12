# coding=utf-8

from .server import run
import sys

if len(sys.argv)==1:
  run()
else:
  run(port=int(sys.argv[1]))

