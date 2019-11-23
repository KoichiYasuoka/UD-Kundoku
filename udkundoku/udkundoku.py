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

from udkundoku.adv import ADV
from udkundoku.aux import AUX
from udkundoku.part import PART
from udkundoku.verb import VERB

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
        if j<i:
          continue
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
        if j<i:
          continue
        k=s[j].xpos
        if k=="v,動詞,存在,存在":
          continue
        elif k=="v,動詞,行為,交流" or k=="v,動詞,行為,伝達":
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
# ADVチェック
  for s in d:
    for i in reversed(range(len(s))):
      t=s[i]
      if t.upos=="ADV" and t.form=="未":
        j=s.index(t.head)
        s[i]=UDKundokuToken(0,"ず","_","AUX","_","_","aux","_","SpaceAfter=No")
        s[i].head=t.head
        t.form="未だ"
        s.insert(j,t)
    for t in s:
      if t.upos!="ADV":
        continue
      i=(t.lemma if t.lemma!="_" else t.form)+","+t.xpos
      if i in ADV:
        x=ADV[i].split(":")
        t.form,t.upos=x[0],x[1]
# PART CCONJ チェック
  for s in d:
    for t in s:
      if t.upos!="PART" and t.upos!="CCONJ":
        continue
      i=(t.lemma if t.lemma!="_" else t.form)+","+t.xpos
      if i in PART:
        x=PART[i].split(":")
        t.form,t.upos=x[0],x[1]
# AUX VERB 活用チェック
  for s in d:
    for i in reversed(range(len(s))):
      if s[i].deprel=="flat:vv":
        s.insert(i+1,UDKundokuToken(0,"す","_","AUX","_","_","aux","_","SpaceAfter=No"))
        s[i+1].head=s[i].head
    for i in range(len(s)):
      if s[i].upos!="AUX"and s[i].upos!="VERB":
        continue
      j=s[i].deprel
      if j=="amod" or j=="flat:vv":
        continue
      x=[t for t in s if t.head==s[i] and t.deprel=="flat:vv"]
      if x==[]:
        s[i].form=katsuyo(s,i)
# よ vocative
  for s in d:
    for i in reversed(range(len(s))):
      if s[i].deprel=="vocative":
        s.insert(i+1,UDKundokuToken(0,"よ","_","ADP","_","_","case","_","SpaceAfter=No"))
        s[i+1].head=s[i]
        j=s.index(s[i].head)
        if s[j].upos=="VERB" and s[j].lemma=="請":
          s[j].form="請ふ"
          x=[k for k,t in enumerate(s) if t.head==s[j] and (t.deprel=="ccomp" or t.deprel=="obj")]
          if x==[]:
            continue
          j=x[-1]
        if s[j].upos=="VERB":
          f=s[j].id
          if len(s)-j>1:
            f=s[j+1].id
          if f>0:
            k=katsuyo_verb(s[j].lemma,s[j].lemma,s[j].xpos).split(":")
            s[j].form=k[5]
# UD化
  kundoku=""
  for s in d:
    for i in range(len(s)):
      s[i].id=i+1
    kundoku+="# text = "+"".join(t.form for t in s if t.form!="_")+"\n"+"\n".join(str(t) for t in s)+"\n\n"
  if raw:
    return kundoku
  return unidic2ud.UniDic2UDEntry(kundoku)

KATSUYO_TABLE={
  "ぶ,五段-バ行":"xば:xび:xぶ:xぶ:xべ:xべ",
  "ぶ,文語上二段-バ行":"xび:xび:xぶ:xびる:xびれ:xびよ",
  "ぶ,文語下二段-バ行":"xべ:xべ:xぶ:xべる:xべれ:xべよ",
  "ぐ,五段-ガ行":"xが:xぎ:xぐ:xぐ:xげ:xげ",
  "ぐ,文語上二段-ガ行":"xぎ:xぎ:xぐ:xぎる:xぎれ:xぎよ",
  "ぐ,文語下二段-ガ行":"xげ:xげ:xぐ:xげる:xげれ:xげよ",
  "づ,五段-ダ行":"xだ:xぢ:xづ:xづ:xで:xで",
  "づ,文語上二段-ダ行":"xぢ:xぢ:xづ:xぢる:xぢれ:xぢよ",
  "づ,文語下二段-ダ行":"xで:xで:xづ:xでる:xでれ:xでよ",
  "ふ,五段-ワア行":"xは:xひ:xふ:xふ:xへ:xへ",
  "ふ,文語四段-ハ行":"xは:xひ:xふ:xふ:xへ:xへ",
  "ふ,文語上二段-ハ行":"xひ:xひ:xふ:xひる:xひれ:xひよ",
  "ふ,文語下二段-ハ行":"xへ:xへ:xふ:xへる:xへれ:xへよ",
  "む,五段-マ行":"xま:xみ:xむ:xむ:xめ:xめ",
  "む,文語上二段-マ行":"xみ:xみ:xむ:xみる:xみれ:xみよ",
  "む,文語下二段-マ行":"xめ:xめ:xむ:xめる:xめれ:xめよ",
  "つ,五段-タ行":"xた:xち:xつ:xつ:xて:xて",
  "つ,文語上二段-タ行":"xち:xち:xつ:xちる:xちれ:xちよ",
  "つ,文語下二段-タ行":"xて:xて:xつ:xてる:xてれ:xてよ",
  "ず,文語サ行変格":"xぜ:xじ:xず:xずる:xじれ:xぜよ",
  "き,文語形容詞-ク":"xから:xく:xし:xき:xけれ:xくせよ",
  "き,文語形容詞-シク":"xしから:xしく:xし:xしき:xしけれ:xしくせよ",
  "く,五段-カ行":"xか:xき:xく:xく:xけ:xけ",
  "く,文語上二段-カ行":"xき:xき:xく:xきる:xきれ:xきよ",
  "く,文語下二段-カ行":"xけ:xけ:xく:xける:xけれ:xけよ",
  "る,五段-ラ行":"xら:xり:xる:xる:xれ:xれ",
}

def katsuyo_verb(form,lemma,xpos):
  t=lemma+","+xpos
  if t in VERB:
    return VERB[t].replace("x",form)
  for g in "ぶぐづふむつずきくる":
    s=QKANA.mecab(lemma+g).split(",")
    if s[0].startswith(lemma+g+"\t"):
      t=g+","+s[4]
      if t in KATSUYO_TABLE:
        return KATSUYO_TABLE[t].replace("x",form)
  if s[4].startswith("上一段-"):
    return "x:x:xる:xる:xれ:xよ".replace("x",form)
  if s[4].startswith("下一段-"):
    return "x:x:xる:xる:xれ:xよ".replace("x",form)
  if xpos.startswith("v,動詞,描写,"):
    return "xなら:xなり:xなり:xなる:xなれ:xなれ".replace("x",form)
  return "xせ:xし:xす:xする:xすれ:xせよ".replace("x",form)

KATSUYO_NEXT={
  "ず,AUX":"0,",
  "なし,AUX":"3,こと",
  "得,AUX":"3,を",
  "欲,AUX":"0,んと",
  "無,VERB":"3,こと",
}

def katsuyo(sentence,ix):
  t=sentence[ix]
  m=t.form if t.lemma=="_" else t.lemma
  if t.upos=="AUX":
    if t.lemma=="能":
      i=sentence.index(t.head)
      if i>ix:
        return "能く"
    k=AUX[m+","+t.xpos].split(":")
  elif t.upos=="VERB":
    k=katsuyo_verb(t.form,m,t.xpos).split(":")
  else:
    return t.form
  while len(sentence)-ix>1:
    ix+=1
    u=sentence[ix]
    if u.form!="_":
      break
  else:
    return k[2]
  m=u.form+","+u.upos
  if m in KATSUYO_NEXT:
    x=KATSUYO_NEXT[m].split(",")
    return k[int(x[0])]+x[1]
  if u.upos=="ADP" or u.upos=="AUX" or u.upos=="PART":
    return k[3]
  return k[1]+"て"

