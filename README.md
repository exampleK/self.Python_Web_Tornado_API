# self.Python_Web_Tornado_API

'''
在公司写的一些api练手用，菜鸟，代码有点那啥，不喜勿喷
'''
-------------------------------环境---------------------------------
#系统：
(.venv) # lsb_release -a
No LSB modules are available.
Distributor ID: Ubuntu
Description:    Ubuntu 16.04.5 LTS
Release:        16.04
Codename:       xenial

#python版本：
Python 3.5.2 (default, Nov 23 2017, 16:37:01) 
[GCC 5.4.0 20160609] on linux


#pip安装包：
(.venv) # pip list
asn1crypto (0.24.0)
astroid (2.1.0)
certifi (2018.11.29)
cffi (1.12.1)
chardet (3.0.4)
Click (7.0)
cryptography (2.5)
dogpile.cache (0.6.7)
flake8 (3.6.0)
idna (2.7)
isort (4.3.4)
lazy-object-proxy (1.3.1)
mccabe (0.6.1)
pip (8.1.1)
pkg-resources (0.0.0)
pycodestyle (2.4.0)
pycparser (2.19)
pycrypto (2.6.1)
pyflakes (2.0.0)
pylint (2.1.1)
PyMySQL (0.9.2)
python-consul (1.1.0)
PyYAML (3.13)
redis (2.10.6)
requests (2.19.1)
rq (0.13.0)
setuptools (40.8.0)
six (1.12.0)
SQLAlchemy (1.2.11)
tornado (5.1.1)
typed-ast (1.3.1)
urllib3 (1.23)
wrapt (1.11.1)
xlrd (1.2.0)


数据库：mysql



-------------------------------内容---------------------------------

用到的数据库python库：
SQLAlchemy


主要是一些增删改查（删：改变状态，软删除）

身份证检查

execl表格的检查，导入并写入mysql