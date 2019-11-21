#! /usr/bin/python -i
# coding=utf-8

import udkanbun

class UDKundokuEntry(udkanbun.UDPipeEntry):
  def to_tree(self,BoxDrawingWidth=1):
    if not hasattr(self,"_tokens"):
      return None
    f=[[] for i in range(len(self))]
    h=[0]
    for i in range(1,len(self)):
      if self[i].deprel=="root":
        h.append(0)
        continue
      j=i+self[i].head.id-self[i].id
      f[j].append(i)
      h.append(j) 
    d=[1 if f[i]==[] and abs(h[i]-i)==1 else -1 if h[i]==0 else 0 for i in range(len(self))]
    while 0 in d:
      for i,e in enumerate(d):
        if e!=0:
          continue
        g=[d[j] for j in f[i]]
        if 0 in g:
          continue
        k=h[i]
        if 0 in [d[j] for j in range(min(i,k)+1,max(i,k))]:
          continue
        for j in range(min(i,k)+1,max(i,k)):
          if j in f[i]:
            continue
          g.append(d[j]-1 if j in f[k] else d[j])
        g.append(0)
        d[i]=max(g)+1
    m=max(d)
    p=[[0]*(m*2) for i in range(len(self))]
    for i in range(1,len(self)):
      k=h[i]
      if k==0:
        continue
      j=d[i]*2-1
      p[min(i,k)][j]|=9
      p[max(i,k)][j]|=5
      for l in range(j):
        p[k][l]|=3
      for l in range(min(i,k)+1,max(i,k)):
        p[l][j]|=12
    u=[" ","\u2574","\u2576","\u2500","\u2575","\u2518","\u2514","\u2534","\u2577","\u2510","\u250C","\u252C","\u2502","\u2524","\u251C","\u253C","<"]
    v=[t.form for t in self]
    l=[]
    for w in v:
      l.append(len(w)+len([c for c in w if ord(c)>127]))
    m=max(l)
    s=""
    for i in range(1,len(self)):
      if h[i]>0:
        j=d[i]*2-2
        while j>=0:
          if p[i][j]>0:
            break
          p[i][j]|=3
          j-=1
        p[i][j+1]=16
      t="".join(u[j] for j in p[i])
      if BoxDrawingWidth>1:
        t=t.replace(" "," "*BoxDrawingWidth).replace("<"," "*(BoxDrawingWidth-1)+"<")
      s+=" "*(m-l[i])+v[i]+" "+t+" "+self[i].deprel+"\n"
    return s

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

def translate(kanbun):
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
# の
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
        x=[k for k in range(i+1,j) if s[k].form=="の" or s[k].deprel=="root"]
        if x!=[]:
          continue
        x=[i if k<=i else j if k>=j else s.index(s[k].head) for k in range(len(s))]
        while set(x)!={i,j}:
          x=[k if k==i or k==j else x[k] for k in x]
        j=len([k for k in x if k==i])
        s.insert(j,UDKundokuToken(0,"の","_","ADP","_","_","case","_","SpaceAfter=No"))
        s[j].head=s[i]
# Universal Dependencies化
  kundoku=""
  for s in d:
    for i in range(len(s)):
      s[i].id=i+1
    kundoku+="# text = "+"".join(t.form for t in s if t.form!="_")+"\n"+"\n".join(str(t) for t in s)+"\n\n"
  return UDKundokuEntry(kundoku)

