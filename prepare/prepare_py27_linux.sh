#!/bin/bash
#
# @file: prepare_py27_linux.sh
#
#   prepare for python2.7 on linux
#
# @create: 2021-01-06 15:19:12
# @update: 2021-02-04 18:01:12
#
#######################################################################
# NOTE: readlink -f not support by MaxOS-X
_file=$(readlink -f $0)
_cdir=$(dirname $_file)
_name=$(basename $_file)

_ver=1.0.0

_help="prepare environment for python2.7 on linux."


. $_cdir/common.sh


# Set characters encodeing
#   LANG=en_US.UTF-8;export LANG
LANG=zh_CN.UTF-8;export LANG

# https://blog.csdn.net/drbinzhao/article/details/8281645
# Treat unset variables as an error
set -o nounset

# Treat any error as exit
set -o errexit

chk_root

osid=`linux_os_id`

#######################################################################
#### python2.7.x required

pyver=`python $_cdir/pyver.py`

if [ $pyver != "2.7" ]; then
    echoerror "not python2.7: python$pyver"
    exit -1
fi

#### fix bug: pyconfig.h not found
# 必须正确配置 yum 源!
if [ $osid == "centos" ] || [ $osid == "rhel" ]; then
    sudo yum install -y python-devel
elif [ $osid == "ubuntu" ]; then
	sudo apt install -y python-dev
else
	echoerror "unsupported os: $osid"
    exit -1
fi


pkgtmpdir=$(mktemp -d /tmp/tmp.XXXXXXXXXX) || exit 1

#### http://pyyaml.org/download/libyaml/yaml-0.2.5.tar.gz
echoinfo "installing yaml-0.2.5"
tar -zxf $_cdir/yaml-0.2.5.tar.gz -C $pkgtmpdir
cd $pkgtmpdir/yaml-0.2.5/ && ./configure && make && sudo make install


#### http://pyyaml.org/download/pyyaml/PyYAML-5.3.1.tar.gz
echoinfo "installing PyYAML-5.3.1"
tar -zxf $_cdir/PyYAML-5.3.1.tar.gz -C $pkgtmpdir
cd $pkgtmpdir/PyYAML-5.3.1/ && python setup.py build && sudo python setup.py install


#### import setuptools
echoinfo "installing setuptools-40.0.0"
tar -zxf $_cdir/setuptools-40.0.0.tar.gz -C $pkgtmpdir
cd $pkgtmpdir/setuptools-40.0.0/ && python setup.py build && sudo python setup.py install


#### from markupsafe import Markup,escape
echoinfo "installing MarkupSafe-1.1.1"
tar -zxf $_cdir/MarkupSafe-1.1.1.tar.gz -C $pkgtmpdir
cd $pkgtmpdir/MarkupSafe-1.1.1/ && python setup.py build && sudo python setup.py install


#### import jinja2
echoinfo "installing Jinja2-2.11.2.tar.gz"
tar -zxf $_cdir/Jinja2-2.11.2.tar.gz -C $pkgtmpdir
cd $pkgtmpdir/Jinja2-2.11.2/ && python setup.py build && sudo python setup.py install


#### import six.moves.urllib as urllib
echoinfo "installing six-1.15.0"
tar -zxf $_cdir/six-1.15.0.tar.gz -C $pkgtmpdir
cd $pkgtmpdir/six-1.15.0/ && python setup.py build && sudo python setup.py install


#### from pathlib2 import Path
echoinfo "installing scandir-1.10.0, pathlib2-2.3.5"
tar -zxf $_cdir/scandir-1.10.0.tar.gz -C $pkgtmpdir
cd $pkgtmpdir/scandir-1.10.0/ && python setup.py build && sudo python setup.py install

tar -zxf $_cdir/pathlib2-2.3.5.tar.gz -C $pkgtmpdir
cd $pkgtmpdir/pathlib2-2.3.5/ && python setup.py build && sudo python setup.py install


#### pyparsing, packaging
echoinfo "installing pyparsing-2.4.7, packaging-20.9"
tar -zxf $_cdir/pyparsing-2.4.7.tar.gz -C $pkgtmpdir
cd $pkgtmpdir/pyparsing-2.4.7/ && python setup.py build && sudo python setup.py install

tar -zxf $_cdir/packaging-20.9.tar.gz -C $pkgtmpdir
cd $pkgtmpdir/packaging-20.9/ && python setup.py build && sudo python setup.py install


#### do cleanup
echoinfo "remove tmp dir: $pkgtmpdir"
cd $_cdir
rm -rf "$pkgtmpdir"


#### report result
result=`python $_cdir/verify.py`

res=${result:0:7}

if [ "$res" != "SUCCESS" ]; then
    echoerror "$result"
    exit -1
fi

echoinfo "$result"

exit 0
