import sys
import udkundoku

def main():
  argc=len(sys.argv)
  i=w=1
  optu=optt=optj=False
  while i<argc:
    o=sys.argv[i]
    if o=="-h" or o=="--help" or o=="-v" or o=="--version":
      usage()
    elif o=="-u":
      optu=True
    elif o=="-t" or o=="-t1":
      optt=True
      w=1
    elif o=="-t2":
      optt=True
      w=2
    elif o=="-j":
      optj=True
    else:
      break
    i+=1
  else:
    lzh=udkundoku.load(True)
    while True:
      try:
        s=input()
      except:
        return
      print(output(lzh,optu,optt,optj,w,s),end="")
  lzh=udkundoku.load(True)
  while i<argc:
    f=open(sys.argv[i],"r",encoding="utf-8")
    s=f.read()
    f.close()
    print(output(lzh,optu,optt,optj,w,s),end="")
    i+=1

def output(lzh,optu,optt,optj,width,sentence):
  if optu:
    if optt:
      return udkundoku.translate(lzh(sentence)).to_svg()
    return udkundoku.translate(lzh(sentence),raw=True)
  if optt:
    return udkundoku.translate(lzh(sentence)).to_tree(BoxDrawingWidth=width,Japanese=optj)
  if optj:
    s=""
    for t in udkundoku.translate(lzh(sentence),raw=True).split("\n"):
      if t.startswith("# text = "):
        s+=t[9:]+"\n"
    return s
  return udkundoku.translate(lzh(sentence),raw=True)

def usage():
  from pkg_resources import get_distribution
  print("UD-Kundoku Version "+get_distribution("udkundoku").version,file=sys.stderr)
  print("Usage: udkanbun [-u|-t|-t2|-j] file",file=sys.stderr)
  print("  output format:",file=sys.stderr)
  print("    -u  Universal Dependencies CoNLL-U",file=sys.stderr)
  print("    -t  tree  (-t2  tree with BoxDrawingWidth=2)",file=sys.stderr)
  print("    -j  Japanese string",file=sys.stderr)
  sys.exit()

if __name__=="__main__":
  main()

