#! /usr/bin/python -i
# coding=utf-8

import setuptools
from setuptools.command.install import install

with open("README.md","r",encoding="UTF-8") as r:
  long_description=r.read()
URL="https://github.com/KoichiYasuoka/UD-Kundoku"

class qkanaPostInstall(install):
  def run(self):
    import atexit
    def qkana_install():
      import unidic2ud
      if unidic2ud.dictlist().find("qkana\n")<0:
        import subprocess
        subprocess.run(["udcabocha","--download=qkana"])
    atexit.register(qkana_install)
    install.run(self)

setuptools.setup(
  name="udkundoku",
  version="0.2.0",
  description="Classical Chinese to Modern Japanese Translator",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url=URL,
  author="Koichi Yasuoka",
  author_email="yasuoka@kanji.zinbun.kyoto-u.ac.jp",
  license="MIT",
  keywords="udkanbun nlp",
  packages=setuptools.find_packages(),
  build_requires=["unidic2ud>=1.4.8"],
  install_requires=["udkanbun>=1.3.4","unidic2ud>=1.4.8"],
  python_requires=">=3.6",
  cmdclass={"install":qkanaPostInstall},
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
