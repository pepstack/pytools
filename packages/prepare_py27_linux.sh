#!/bin/bash
#
# @file: prepare_py27_linux.sh
#
#   prepare for python2.7 on linux (el6,el7)
#
# @create: 2021-01-06 15:19:12
# @update: 2021-02-25 19:21:12
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
    yum install -y python-devel
elif [ $osid == "ubuntu" ]; then
	apt install -y python-dev
else
	echoerror "unsupported os: $osid"
    exit -1
fi


pkgtmpdir=$(mktemp -d /tmp/tmp.XXXXXXXXXX) || exit 1

#### http://pyyaml.org/download/libyaml/yaml-0.2.5.tar.gz
echoinfo "installing yaml-0.2.5"
tar -zxf $_cdir/yaml-0.2.5.tar.gz -C $pkgtmpdir
cd $pkgtmpdir/yaml-0.2.5/ && ./configure && make && make install

pyinstall_pkg "PyYAML-5.3.1" "$_cdir" "$pkgtmpdir"
pyinstall_pkg "setuptools-40.0.0" "$_cdir" "$pkgtmpdir"
pyinstall_pkg "MarkupSafe-1.1.1" "$_cdir" "$pkgtmpdir"
pyinstall_pkg "Jinja2-2.11.2" "$_cdir" "$pkgtmpdir"
pyinstall_pkg "six-1.15.0" "$_cdir" "$pkgtmpdir"
pyinstall_pkg "scandir-1.10.0" "$_cdir" "$pkgtmpdir"
pyinstall_pkg "pathlib2-2.3.5" "$_cdir" "$pkgtmpdir"
pyinstall_pkg "pyparsing-2.4.7" "$_cdir" "$pkgtmpdir"
pyinstall_pkg "packaging-20.9" "$_cdir" "$pkgtmpdir"

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
