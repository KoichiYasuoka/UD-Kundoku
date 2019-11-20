#! /usr/bin/python -i
# coding=utf-8

def translate(kanbun):
  import udkanbun.kaeriten
  k=udkanbun.kaeriten.kaeriten(kanbun,True)
  t=[]
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
  s=""
  for i in reversed(range(len(t))):
    if t[i]==0:
      s+="\n"
    else:
      s+=str(kanbun[t[i]])+"\n"
  return s

