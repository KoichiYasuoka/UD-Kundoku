#! /usr/bin/python -i
# coding=utf-8

import setuptools
from setuptools.command.install import install

with open("README.md","r",encoding="UTF-8") as r:
  long_description=r.read()
URL="https://github.com/KoichiYasuoka/UD-Kundoku"
QKANA_URL="https://unidic.ninjal.ac.jp/unidic_archive/qkana/1603/UniDic-qkana_1603.zip"

class qkanaInstall(install):
  def run(self):
    try:
      import unidic2ud
      if unidic2ud.dictlist().find("qkana\n")<0:
        import subprocess
        subprocess.check_call(["unidic2ud","--download=qkana"])
    except:
      import os,ssl,urllib.request,zipfile,glob
      ssl._create_default_https_context=ssl._create_unverified_context
      f,h=urllib.request.urlretrieve(QKANA_URL)
      with zipfile.ZipFile(f) as z:
        z.extractall("build")
      os.renames(glob.glob("build/UniDic-qkana*")[0],"build/lib/udkundoku/qkana")
    install.run(self)

setuptools.setup(
  name="udkundoku",
  version="2.0.0",
  description="Classical Chinese to Modern Japanese Translator",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url=URL,
  author="Koichi Yasuoka",
  author_email="yasuoka@kanji.zinbun.kyoto-u.ac.jp",
  license="MIT",
  keywords="udkanbun nlp",
  packages=setuptools.find_packages(),
  install_requires=["udkanbun>=3.0.2","unidic2ud>=2.8.0"],
  python_requires=">=3.6",
  cmdclass={"install":qkanaInstall},
  package_data={
    "udkundoku":["./server/*.html","./server/*.js"],
  },
  entry_points={
    "console_scripts":["udkundoku=udkundoku.cli:main"],
  },
  classifiers=[
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Operating System :: OS Independent",
    "Topic :: Text Processing :: Linguistic",
    "Natural Language :: Japanese",
  ],
  project_urls={
    "ud-ja-kanbun":"https://corpus.kanji.zinbun.kyoto-u.ac.jp/gitlab/Kanbun/ud-ja-kanbun",
    "Source":URL,
    "Tracker":URL+"/issues",
  }
)
