[![Current PyPI packages](https://badge.fury.io/py/udkundoku.svg)](https://pypi.org/project/udkundoku/)

# UD-Kundoku

Classical Chinese to Modern Japanese Translator, working on [Universal Dependencies](https://universaldependencies.org/format.html).

## Basic usage

```py
>>> import udkundoku
>>> lzh=udkundoku.load()
>>> s=lzh("欲治其國者先齊其家")
>>> t=udkundoku.translate(s)
>>> print(t)
```
`udkundoku.load()` is an alias for `udkanbun.load()` of [UD-Kanbun](https://github.com/KoichiYasuoka/UD-Kanbun/). `udkundoku.translate()` is a transcriptive converter from Classical Chinese (under Universal Dependencies of UD-Kanbun) into Modern Japanese (under Universal Dependencies of [UniDic2UD](https://github.com/KoichiYasuoka/UniDic2UD/)).

## Installation for Linux

Binary wheel is available for Linux, and is installed by default when you use `pip`:
```sh
pip install udkundoku
```
[旧仮名口語UniDic](https://unidic.ninjal.ac.jp/download_all#unidic_qkana) is automatically downloaded for UniDic2UD.

## Installation for Cygwin64

For installing in [Cygwin64](https://www.cygwin.com/install.html), make sure to get `gcc-g++` `git` `python37-pip` `python37-devel` `swig` packages, and then:
```sh
pip3.7 install git+https://github.com/KoichiYasuoka/mecab-cygwin64
pip3.7 install udkundoku
```
Use `python3.7` command in Cygwin64 instead of `python`. For installing in old Cygwin (32-bit), try to use [mecab-cygwin32](https://github.com/KoichiYasuoka/mecab-cygwin32) instead of [mecab-cygwin64](https://github.com/KoichiYasuoka/mecab-cygwin64).

## Installation for Jupyter Notebook (Google Colaboratory)

```py
!pip install udkundoku
```

## Author

Koichi Yasuoka (安岡孝一)

