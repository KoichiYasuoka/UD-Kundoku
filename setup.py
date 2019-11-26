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
        subprocess.check_call(["udcabocha","--download=qkana"])
    except:
      from pip._internal.models.link import Link
      from pip._internal.download import unpack_url
      unpack_url(Link(QKANA_URL),"build/lib/udkundoku/qkana")
    install.run(self)

setuptools.setup(
  name="udkundoku",
  version="0.5.8",
  description="Classical Chinese to Modern Japanese Translator",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url=URL,
  author="Koichi Yasuoka",
  author_email="yasuoka@kanji.zinbun.kyoto-u.ac.jp",
  license="MIT",
  keywords="udkanbun nlp",
  packages=setuptools.find_packages(),
  install_requires=["udkanbun>=1.4.2","unidic2ud>=1.5.0"],
  python_requires=">=3.6",
  cmdclass={"install":qkanaInstall},
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
