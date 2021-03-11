#! /usr/bin/python -i
# coding=utf-8

import udkanbun
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

from udkundoku.adp import ADP
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

class UDKundokuEntry(udkanbun.UDKanbunEntry):
  def kaeriten(self):
    return None
  def to_tree(self,BoxDrawingWidth=1,kaeriten=False,Japanese=True):
    return udkanbun.UDKanbunEntry.to_tree(self,BoxDrawingWidth,False,Japanese)
  def sentence(self):
    r=""
    for s in self:
      if s.id==1:
        r+="\n"
      if s.form!="_":
        r+=s.form
    return r[1:]+"\n"

def load(MeCab=True,Danku=False):
  return udkanbun.load(MeCab,Danku)

def reorder(kanbun,matrix=False):
  import udkanbun.kaeriten
  if type(kanbun)!=udkanbun.UDKanbunEntry:
    import deplacy
    kanbun=udkanbun.UDKanbunEntry(deplacy.to_conllu(kanbun))
  k=udkanbun.kaeriten.kaeriten(kanbun,True)
# 同時移動
  n=[-1]*len(kanbun)
  for i in range(len(kanbun)-1):
    if kanbun[i+1].id==1:
      continue
    if kanbun[i].lemma=="所" and kanbun[i+1].lemma=="以":
      n[i],n[i+1]=i+1,i
    elif kanbun[i+1].deprel=="flat:vv" and kanbun[i+1].head==kanbun[i]:
      n[i],n[i+1]=i+1,i
    elif kanbun[i+1].deprel=="fixed" and kanbun[i+1].xpos=="p,接尾辞,*,*":
      n[i],n[i+1]=i+1,i
# 語順入れ替え
  t=[0]
  c=[False]*len(kanbun)
  for i in reversed(range(1,len(kanbun))):
    if c[i]:
      if kanbun[i].id==1:
        t.append(0)
      continue
    j=len(t)
    c[i]=True
    t.append(i)
    if n[i]==i-1:
      i-=1
      c[i]=True
      t.append(i)
    if k[i]==[]:
      if kanbun[i].id==1:
        t.append(0)
      continue
    while k[i]!=[]:
      i=k[i][0]
      c[i]=True
      t.insert(j,i)
      if n[i]==i+1:
        c[i+1]=True
        t.insert(j,i+1)
      elif n[i]==i-1:
        i-=1
        c[i]=True
        t.insert(j,i)
# 訓読配列作成
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
    for j,t in enumerate(w):
      t.id=j+1
    d[i]=w
  if matrix:
    return d
  s=""
  for w in d:
    s+="\n".join(str(t) for t in w)+"\n\n"
  return UDKundokuEntry(s)

def translate(kanbun,raw=False):
  d=reorder(kanbun,True)
# の SCONJ,nmod,det
  for s in d:
    for i in reversed(range(len(s))):
      if s[i].form=="之" and s[i].upos=="SCONJ":
        s[i].form="の"
        s[i].id=0
      elif s[i].deprel=="nmod" or s[i].deprel=="det":
        j=s.index(s[i].head)
        if j-i<1:
          continue
        if s[j].upos=="NUM":
          continue
        if j-i==1:
          s.insert(j,UDKundokuToken(0,"の","_","ADP","_","_","case","_","SpaceAfter=No"))
          s[j].head=s[i]
          continue
        x=[k for k in range(i+1,j) if s[k].id==0 or s[k].deprel=="root"]
        if x!=[]:
          if s[i].deprel=="det" and s[i+1].id!=0:
            s.insert(i+1,UDKundokuToken(0,"が","_","ADP","_","_","case","_","SpaceAfter=No"))
            s[i+1].head=s[i]
          continue
        x=[i if k<=i else j if k>=j else s.index(s[k].head) for k in range(len(s))]
        y={i,j}
        while set(x)!=y:
          y=set(x)
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
        y={i,j}
        while set(x)!=y:
          y=set(x)
          x=[k if k==i or k==j else x[k] for k in x]
        j=len([k for k in x if k==i])
        if s[j-1].id!=0:
          if s[j-1].lemma=="者" and s[j-1].deprel=="case":
            s[j-1].form=w
            s[j-1].id=0
          else:
            s.insert(j,UDKundokuToken(0,w,"_","ADP","_","_","case","_","SpaceAfter=No"))
            s[j].head=s[i]
# せ と が xcomp
  for s in d:
    for i in reversed(range(len(s))):
      if s[i].deprel=="xcomp":
        j=s.index(s[i].head)
        if j<i:
          continue
        k=s[j].xpos
        if k=="v,動詞,行為,使役":
          w="せ"
        elif k=="v,動詞,行為,伝達":
          w="と"
        else:
          w="が"
        if j-i==1:
          s.insert(j,UDKundokuToken(0,w,"_","SCONJ","_","_","case","_","SpaceAfter=No"))
          s[j].head=s[i]
          continue
        x=[i if k<=i else j if k>=j else s.index(s[k].head) for k in range(len(s))]
        y={i,j}
        while set(x)!=y:
          y=set(x)
          x=[k if k==i or k==j else x[k] for k in x]
        j=len([k for k in x if k==i])
        if s[j-1].id!=0:
          s.insert(j,UDKundokuToken(0,w,"_","SCONJ","_","_","case","_","SpaceAfter=No"))
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
          if s[j].lemma=="有" or s[j].lemma=="無":
            continue
          w="に"
        elif k=="v,動詞,行為,伝達":
          w="と" if x=="ccomp" else "を"
          if x=="obj":
            v=s[i].xpos
            if v.startswith("n,代名詞,人称,") or v.startswith("n,名詞,人,"):
              w="に"
            v=[t.deprel for t in s if t.head==s[j]]
            if "iobj" in v:
              w="と"
            elif "aux" in v:
              v=[t.lemma for t in s if t.head==s[j] and t.deprel=="aux"]
              if "可" in v:
                w="と"
        elif k=="v,動詞,行為,移動":
          w="に"
        elif k=="v,動詞,行為,使役":
          w="をして"
        elif k=="v,動詞,行為,分類":
          w="の"
          if x=="ccomp":
            w="が"
          elif x=="obj" and s[i].upos=="VERB":
            w="が"
        else:
          w="に" if x=="iobj" else "を"
        if j-i==1:
          s.insert(j,UDKundokuToken(0,w,"_","ADP","_","_","case","_","SpaceAfter=No"))
          s[j].head=s[i]
          continue
        x=[i if k<=i else j if k>=j else s.index(s[k].head) for k in range(len(s))]
        y={i,j}
        while set(x)!=y:
          y=set(x)
          x=[k if k==i or k==j else x[k] for k in x]
        j=len([k for k in x if k==i])
        if s[j-1].id!=0:
          s.insert(j,UDKundokuToken(0,w,"_","ADP","_","_","case","_","SpaceAfter=No"))
          s[j].head=s[i]
# ADPチェック
  for s in d:
    for h in reversed(range(len(s))):
      if s[h].xpos=="v,前置詞,基盤,*":
        i=s.index(s[h].head)
        if i>h:
          j=s.index(s[i].head)
          w="より" if s[j].xpos=="v,動詞,描写,量" else "に"
          if j-i<1:
            pass
          elif j-i!=1:
            x=[i if k<=i else j if k>=j else s.index(s[k].head) for k in range(len(s))]
            y={i,j}
            while set(x)!=y:
              y=set(x)
              x=[k if k==i or k==j else x[k] for k in x]
            j=len([k for k in x if k==i])
          if s[j-1].id==0:
            s[h].form="_"
            continue
          t=s.pop(h)
          t.id,t.form=0,w
          s.insert(j-1,t)
    for t in s:
      if t.upos!="ADP":
        continue
      i=(t.lemma if t.lemma!="_" else t.form)+","+t.xpos
      if i in ADP:
        x=ADP[i].split(":")
        t.id,t.form,t.upos=0,x[0],x[1]
# に obl
  for s in d:
    for i in reversed(range(len(s))):
      if s[i].deprel.startswith("obl"):
        if s[i].lemma=="自" and s[i].upos=="PRON":
          continue
        j=s.index(s[i].head)
        if j<i:
          if s[i].lemma=="焉":
            s[i].form="_"
          continue
        if j-i==1:
          s.insert(j,UDKundokuToken(0,"に","_","ADP","_","_","case","_","SpaceAfter=No"))
          s[j].head=s[i]
          continue
        x=[k for k in range(i+1,j) if s[k].deprel=="case" and s[k].head==s[i]]
        if x!=[]:
          continue
        x=[i if k<=i else j if k>=j else s.index(s[k].head) for k in range(len(s))]
        y={i,j}
        while set(x)!=y:
          y=set(x)
          x=[k if k==i or k==j else x[k] for k in x]
        j=len([k for k in x if k==i])
        s.insert(j,UDKundokuToken(0,"に","_","ADP","_","_","case","_","SpaceAfter=No"))
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
      elif t.upos=="ADV" and t.form=="則":
        j=s.index(t.head)
        t.form="則ち"
        if j<=i:
          continue
        x=[k for k in range(0,i) if s[k].head==t.head and s[k].deprel=="advcl"]
        if x==[]:
          continue
        s.insert(i,UDKundokuToken(0,"ば","_","ADP","_","_","case","_","SpaceAfter=No"))
        s[i].head=t
    for k,t in enumerate(s):
      if t.upos!="ADV" and t.deprel!="advmod":
        continue
      i=(t.lemma if t.lemma!="_" else t.form)+","+t.xpos
      if i in ADV:
        x=ADV[i].split(":")
        t.form,t.upos=x[0],x[1]
      elif t.upos=="ADV" and t.lemma!="_":
        x=QKANA.mecab(t.lemma).split(",")
        if x[0]==t.lemma+"\t"+"副詞" or x[0]==t.lemma+"\t"+"接続詞":
          k=x[7]
          if k==t.lemma or not k.startswith(t.lemma):
            k="".join(chr(c if c<12449 or c>12534 else c-96) for c in [ord(c) for c in x[6]])
          ADV[i]=k+":ADV"
          t.form=k
        else:
          t.form+="に"
# PART CCONJ PRON チェック
  for s in d:
    for k,t in enumerate(s):
      if t.upos!="PART" and t.upos!="CCONJ" and t.upos!="PRON":
        continue
      i=(t.lemma if t.lemma!="_" else t.form)+","+t.xpos
      if i in PART:
        x=PART[i].split(":")
        t.form,t.upos=x[0],x[1]
      elif t.upos=="PART":
        if t.xpos=="p,助詞,句末,*":
          if len(s)-k==1:
            t.form="か"
          elif s[k+1].upos=="PART":
            t.form="_"
          else:
            t.form="か"
        elif t.xpos=="p,助詞,句頭,*":
          t.form="それ"
# AUX VERB 活用チェック
  for s in d:
    for i in reversed(range(len(s))):
      if s[i].deprel=="flat:vv":
        if len(s)-i==1:
          s.append(UDKundokuToken(0,"す","_","AUX","_","_","aux","_","SpaceAfter=No"))
          s[i+1].head=s[i].head
        elif s[i+1].id!=0:
          s.insert(i+1,UDKundokuToken(0,"す","_","AUX","_","_","aux","_","SpaceAfter=No"))
          s[i+1].head=s[i].head
    for i in range(len(s)):
      if s[i].upos!="AUX"and s[i].upos!="VERB":
        continue
      j=s[i].deprel
      if j=="flat:vv":
        continue
      if j=="amod":
        if i<s.index(s[i].head):
          continue
      x=[t for t in s if t.head==s[i] and (t.deprel=="flat:vv" or (t.lemma!="乎" and t.xpos=="p,接尾辞,*,*"))]
      if x==[]:
        s[i].form="況んや" if s[i].lemma=="況" and s[i].xpos=="v,動詞,行為,動作" else katsuyo(s,i)
# よ vocative
  for s in d:
    for i in reversed(range(len(s))):
      if s[i].deprel=="vocative":
        f=False
        if len(s)-i==1:
          f=True
        elif s[i+1].upos!="ADP" and s[i+1].upos!="PART":
          f=True
        if f:
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
# 所以(ゆゑん) 如何(いかん) 所謂(いはゆる) 名詞+ず 名詞+ば
  for s in d:
    for i in range(len(s)):
      if s[i].lemma=="所" and s[i].upos=="PART":
        u=s[i].head
        if u.lemma=="以":
          s[i].form="ゆゑん"
          u.form="_"
          if len(s)-i>1:
            s[i].form="ゆゑんの" if s[i+1].lemma=="者" else "ゆゑん"
    for i in range(len(s)-1):
      k=s[i].lemma
      if k=="如" or k=="奈" or k=="若":
        if s[i+1].lemma=="何":
          s[i].form,s[i+1].form="いか","ん"
      elif k=="謂":
        if s[i+1].form=="所":
          s[i].form,s[i+1].form="いは","ゆる"
    for i in range(len(s)):
      if s[i].form in ["ざら","ずし","ず","ざる","ざれ"] and s[i].upos=="AUX":
        x=s[i-1].upos
        if x!="VERB" and x!="AUX":
          s[i].form="なら"+s[i].form
      elif s[i].lemma=="非" and s[i].upos=="AUX":
        x=s[i-1].upos
        if x!="VERB" and x!="AUX":
          s[i].form="に"+s[i].form
      elif s[i].form=="ば" and s[i].id==0:
        x=s[i-1].upos
        if x!="VERB" and x!="AUX":
          s[i].form="ならば"
# UD化
  for s in d:
    for i in reversed(range(len(s))):
      j=s.index(s[i].head)
      if abs(i-j)<2:
        continue
      z=[-1 if t.head==t else s.index(t.head) for t in s]
      x,y=min(i,j),max(i,j)
      for k,w in enumerate(z):
        if k==x or k==y:
          continue
        elif k>x and k<y:
          if w==-1 or w<x or w>y:
            break
        elif w>x and w<y:
            break
      else:
        continue
      s[i].head=s[i-1] if i>0 else s[1]
  kundoku=""
  for s in d:
    if s==[]:
      continue
    for i in range(len(s)):
      s[i].id=i+1
    kundoku+="# text = "+"".join(t.form for t in s if t.form!="_")+"\n"+"\n".join(str(t) for t in s)+"\n\n"
  if raw:
    return kundoku
  return UDKundokuEntry(kundoku)

KATSUYO_TABLE={
  "ぶ,五段-バ行":"xば:xび:xぶ:xぶ:xべ:xべ",
  "ぶ,文語上二段-バ行":"xび:xび:xぶ:xびる:xびれ:xびよ",
  "ぶ,文語下二段-バ行":"xべ:xべ:xぶ:xべる:xべれ:xべよ",
  "づ,五段-ダ行":"xだ:xぢ:xづ:xづ:xで:xで",
  "づ,文語上二段-ダ行":"xぢ:xぢ:xづ:xぢる:xぢれ:xぢよ",
  "づ,文語下二段-ダ行":"xで:xで:xづ:xでる:xでれ:xでよ",
  "す,五段-サ行":"xさ:xし:xす:xす:xせ:xせ",
  "ず,文語サ行変格":"xぜ:xじ:xず:xずる:xじれ:xぜよ",
  "む,五段-マ行":"xま:xみ:xむ:xむ:xめ:xめ",
  "む,文語上二段-マ行":"xみ:xみ:xむ:xみる:xみれ:xみよ",
  "む,文語下二段-マ行":"xめ:xめ:xむ:xめる:xめれ:xめよ",
  "ふ,五段-ワア行":"xは:xひ:xふ:xふ:xへ:xへ",
  "ふ,文語四段-ハ行":"xは:xひ:xふ:xふ:xへ:xへ",
  "ふ,文語上二段-ハ行":"xひ:xひ:xふ:xひる:xひれ:xひよ",
  "ふ,文語下二段-ハ行":"xへ:xへ:xふ:xへる:xへれ:xへよ",
  "つ,五段-タ行":"xた:xち:xつ:xつ:xて:xて",
  "つ,文語上二段-タ行":"xち:xち:xつ:xちる:xちれ:xちよ",
  "つ,文語下二段-タ行":"xて:xて:xつ:xてる:xてれ:xてよ",
  "ぐ,五段-ガ行":"xが:xぎ:xぐ:xぐ:xげ:xげ",
  "ぐ,文語上二段-ガ行":"xぎ:xぎ:xぐ:xぎる:xぎれ:xぎよ",
  "ぐ,文語下二段-ガ行":"xげ:xげ:xぐ:xげる:xげれ:xげよ",
  "き,文語形容詞-ク":"xから:xく:xし:xき:xけれ:xくせよ",
  "き,文語形容詞-シク":"xしから:xしく:xし:xしき:xしけれ:xしくせよ",
  "く,五段-カ行":"xか:xき:xく:xく:xけ:xけ",
  "く,文語上二段-カ行":"xき:xき:xく:xきる:xきれ:xきよ",
  "く,文語下二段-カ行":"xけ:xけ:xく:xける:xけれ:xけよ",
  "る,五段-ラ行":"xら:xり:xる:xる:xれ:xれ",
}

def katsuyo_verb(form,lemma,xpos):
  v=lemma+","+xpos
  if v in VERB:
    return VERB[v].replace("x",form)
  s=QKANA.mecab(lemma).split(",")
  if s[0]==lemma+"\t動詞":
    t=s[12][1:]+","+s[4]
    if t in KATSUYO_TABLE:
      VERB[v]=KATSUYO_TABLE[t]
      return VERB[v].replace("x",form)
  for g in "ぶづすずむふつぐきくる":
    s=QKANA.mecab(lemma+g).split(",")
    if s[0].startswith(lemma+g+"\t"):
      t=g+","+s[4]
      if t in KATSUYO_TABLE:
        VERB[v]=KATSUYO_TABLE[t]
        return VERB[v].replace("x",form)
  if s[4].startswith("上一段-"):
    VERB[v]="x:x:xる:xる:xれ:xよ"
  elif s[4].startswith("下一段-"):
    VERB[v]="x:x:xる:xる:xれ:xよ"
  elif xpos.startswith("v,動詞,描写,"):
    VERB[v]="xなら:xなり:xなり:xなる:xなれ:xなれ"
  else:
    VERB[v]="xせ:xし:xす:xする:xすれ:xせよ"
  return VERB[v].replace("x",form)

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
    if u.form!="_" and u.upos!="PUNCT":
      break
  else:
    return k[2]
  if u.xpos=="v,動詞,存在,存在" and u.lemma=="爲":
    return k[1]
  m=u.form+","+u.upos
  if m in KATSUYO_NEXT:
    x=KATSUYO_NEXT[m].split(",")
    return k[int(x[0])]+x[1]
  if u.upos=="ADP" or u.upos=="AUX" or u.upos=="PART":
    return k[3]
  if t.deprel=="acl" and (u.upos=="NOUN" or u.upos=="PROPN"):
    return k[3]
  if k[1].endswith("く"):
    return k[1]
  return k[1]+"て"

KATSUYO_NEXT={
  "ず,AUX":"0,",
  "せ,SCONJ":"1,",
  "と,ADP":"2,",
  "と,SCONJ":"5,",
  "なし,AUX":"3,こと",
  "ば,ADP":"4,",
  "や,PART":"2,",
  "んとす,AUX":"0,",
  "得,AUX":"3,を",
  "易,VERB":"1,",
  "有,VERB":"3,",
  "欲,AUX":"0,んと",
  "無,VERB":"3,こと",
  "被,AUX":"0,",
  "見,AUX":"0,",
  "雖も,ADV":"2,と",
  "難,VERB":"1,",
  "非ず,AUX":"3,に",
  "難,VERB":"1,",
}
