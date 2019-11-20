[![Current PyPI packages](https://badge.fury.io/py/udkundoku.svg)](https://pypi.org/project/udkundoku/)

# UD-Kundoku

Classical Chinese to Modern Japanese Translator, working on [Universal Dependencies](https://universaldependencies.org/format.html).

## Basic usage

```py
>>> import udkanbun
>>> lzh=udkanbun.load()
>>> s=lzh("未有義而後其君者也")
>>> import udkundoku
>>> t=udkundoku.translate(s)
>>> print(t)
```

## Installation for Linux

Binary wheel is available for Linux, and is installed by default when you use `pip`:
```sh
pip install udkundoku
```

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

