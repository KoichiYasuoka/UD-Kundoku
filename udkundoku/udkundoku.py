#! /usr/bin/python -i
# coding=utf-8

import unidic2ud
if unidic2ud.dictlist().find("qkana\n")<0:
  import os
  p=os.path.join(os.path.abspath(os.path.dirname(__file__)),"qkana")
  if os.path.isdir(p):
    import shutil
    shutil.move(p,unidic2ud.DOWNLOAD_DIR)
  else:
    unidic2ud.download("qkana","unidic")
QKANA=unidic2ud.UniDic2UD("qkana",None)

class UDKundokuToken(object):
  def __init__(self,id,form,lemma,upos,xpos,feats,deprel,deps,misc):
    self.id=id
    self.form=form
    self.lemma=lemma
    self.upos=upos
    self.xpos=xpos
    self.feats=feats
    self.deprel=deprel
    self.deps=deps
    self.misc=misc
  def __repr__(self):
    r="\t".join([str(self.id),self.form,self.lemma,self.upos,self.xpos,self.feats,str(0 if self.head is self else self.head.id),self.deprel,self.deps,self.misc])
    return r if type(r) is str else r.encode("utf-8")

def load(MeCab=True):
  import udkanbun
  return udkanbun.load(MeCab)

def translate(kanbun,raw=False):
  import udkanbun.kaeriten
  k=udkanbun.kaeriten.kaeriten(kanbun,True)
  t=[0]
  c=[False]*len(kanbun)
  for i in reversed(range(1,len(kanbun))):
    if c[i]:
      if kanbun[i].id==1:
        t.append(0)
      continue
    c[i]=True
    t.append(i)
    if k[i]==[]:
      if kanbun[i].id==1:
        t.append(0)
      continue
    j=len(t)-1
    while k[i]!=[]:
      i=k[i][0]
      c[i]=True
      t.insert(j,i)
  d,s=[],[]
  for i in reversed(range(len(t)-1)):
    if t[i]==0:
      d.append(s)
      s=[]
    else:
      s.append(kanbun[t[i]])
  for i,s in enumerate(d):
    w=[]
    for t in s:
      w.append(UDKundokuToken(t.id,t.form,t.lemma,t.upos,t.xpos,t.feats,t.deprel,t.deps,t.misc))
    for j,t in enumerate(s):
      w[j].head=w[s.index(t.head)]
    d[i]=w
# の SCONJ,nmod,det
  for s in d:
    for i in reversed(range(len(s))):
      if s[i].form=="之" and s[i].upos=="SCONJ":
        s[i].form="の"
        s[i].id=0
      elif s[i].deprel=="nmod" or s[i].deprel=="det":
        j=s.index(s[i].head)
        if j-i==1:
          s.insert(j,UDKundokuToken(0,"の","_","ADP","_","_","case","_","SpaceAfter=No"))
          s[j].head=s[i]
          continue
        x=[k for k in range(i+1,j) if s[k].id==0 or s[k].deprel=="root"]
        if x!=[]:
          continue
        x=[i if k<=i else j if k>=j else s.index(s[k].head) for k in range(len(s))]
        while set(x)!={i,j}:
          x=[k if k==i or k==j else x[k] for k in x]
        j=len([k for k in x if k==i])
        s.insert(j,UDKundokuToken(0,"の","_","ADP","_","_","case","_","SpaceAfter=No"))
        s[j].head=s[i]
# は,が PART,nsubj,csubj
  for s in d:
    for i in reversed(range(len(s))):
      if s[i].deprel.startswith("nsubj") or s[i].deprel.startswith("csubj"):
        j=s.index(s[i].head)
        k=s[j].deprel
        w="が" if k=="ccomp" or k=="advcl" or k.startswith("csubj") else "は"
        if j-i==1:
          s.insert(j,UDKundokuToken(0,w,"_","ADP","_","_","case","_","SpaceAfter=No"))
          s[j].head=s[i]
          continue
        x=[i if k<=i else j if k>=j else s.index(s[k].head) for k in range(len(s))]
        while set(x)!={i,j}:
          x=[k if k==i or k==j else x[k] for k in x]
        j=len([k for k in x if k==i])
        if s[j-1].id!=0:
          if s[j-1].lemma=="者" and s[j-1].deprel=="case":
            s[j-1].form=w
            s[j-1].id=0
          else:
            s.insert(j,UDKundokuToken(0,w,"_","ADP","_","_","case","_","SpaceAfter=No"))
            s[j].head=s[i]
# せ の xcomp
  for s in d:
    for i in reversed(range(len(s))):
      if s[i].deprel=="xcomp":
        j=s.index(s[i].head)
        if j<i:
          continue
        k=s[j].xpos
        if k=="v,動詞,行為,使役":
          w="せ"
        else:
          w="が"
        if j-i==1:
          s.insert(j,UDKundokuToken(0,w,"_","ADP","_","_","case","_","SpaceAfter=No"))
          s[j].head=s[i]
          continue
        x=[i if k<=i else j if k>=j else s.index(s[k].head) for k in range(len(s))]
        while set(x)!={i,j}:
          x=[k if k==i or k==j else x[k] for k in x]
        j=len([k for k in x if k==i])
        if s[j-1].id!=0:
          s.insert(j,UDKundokuToken(0,w,"_","ADP","_","_","case","_","SpaceAfter=No"))
          s[j].head=s[i]
# を に と obj ccomp iobj
  for s in d:
    for i in reversed(range(len(s))):
      x=s[i].deprel
      if x=="obj" or x=="ccomp" or x=="iobj":
        j=s.index(s[i].head)
        k=s[j].xpos
        if k=="v,動詞,行為,交流" or k=="v,動詞,行為,伝達":
          w="を" if x=="iobj" else "と"
        elif k=="v,動詞,行為,移動":
          w="に"
        elif k=="v,動詞,行為,使役":
          w="をして"
        elif k=="v,動詞,行為,分類":
          w="の"
        else:
          w="に" if x=="iobj" else "を"
        if j-i==1:
          s.insert(j,UDKundokuToken(0,w,"_","ADP","_","_","case","_","SpaceAfter=No"))
          s[j].head=s[i]
          continue
        x=[i if k<=i else j if k>=j else s.index(s[k].head) for k in range(len(s))]
        while set(x)!={i,j}:
          x=[k if k==i or k==j else x[k] for k in x]
        j=len([k for k in x if k==i])
        if s[j-1].id!=0:
          s.insert(j,UDKundokuToken(0,w,"_","ADP","_","_","case","_","SpaceAfter=No"))
          s[j].head=s[i]
# UD化
  kundoku=""
  for s in d:
    for i in range(len(s)):
      s[i].id=i+1
    kundoku+="# text = "+"".join(t.form for t in s if t.form!="_")+"\n"+"\n".join(str(t) for t in s)+"\n\n"
  if raw:
    return kundoku
  return unidic2ud.UniDic2UDEntry(kundoku)

