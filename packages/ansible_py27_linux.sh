#!/bin/bash
#
# @file: ansible_py27_linux.sh
#
#   install ansible for python2.7 on linux (el6,el7)
#
# @create: 2021-02-04 18:01:12
# @update: 2021-02-25 19:21:12
#
#######################################################################
# NOTE: readlink -f not support by MaxOS-X
_file=$(readlink -f $0)
_cdir=$(dirname $_file)
_name=$(basename $_file)

_ver=1.0.0

_help="install ansible for python2.7 on linux."


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

pkgtmpdir=$(mktemp -d /tmp/tmp.XXXXXXXXXX) || exit 1

echowarn "installing packages before ansible installation"
echowarn "[0] yum install -y libffi libffi-devel"

# TODO: 升级 OpenSSL

echowarn "[1: ecdsa-0.16.1.tar.gz] https://pypi.org/project/ecdsa/"
echowarn "[2: pycrypto-2.6.1.tar.gz] https://pypi.org/project/pycrypto/"
echowarn "[3: pycparser-2.20.tar.gz] https://pypi.org/project/pycparser/"
echowarn "[4: cffi-1.14.5.tar.gz] https://pypi.org/project/cffi/"
echowarn "[5: simplejson-3.17.2.tar.gz] https://pypi.org/project/simplejson/"
echowarn "[6: ipaddress-1.0.23.tar.gz] https://pypi.org/project/ipaddress/"
echowarn "[7: enum34-1.1.10.tar.gz] https://pypi.org/project/enum34/"
echowarn "[8: cryptography-2.9.2.tar.gz] https://pypi.org/project/cryptography/"
echowarn "[9: wheel-0.30.0.tar.gz] https://pypi.org/project/wheel/"
echowarn "[10: PyNaCl-1.4.0.tar.gz] https://pypi.org/project/PyNaCl"
echowarn "[11: bcrypt-3.1.7.tar.gz] https://pypi.org/project/bcrypt/"
echowarn "[12: paramiko-2.7.2.tar.gz] https://pypi.org/project/paramiko/"

echowarn "[ansible-base-2.10.5.tar.gz]"
echowarn "[ansible-2.10.6-fix.tar.gz]"

echowarn "如果安装完毕请注释掉下面的行, 然后再次执行安装!"
exit 1

#### ansible-base-2.10.5.tar.gz
echoinfo "installing ansible-base-2.10.5"
tar -zxf $_cdir/ansible-base-2.10.5.tar.gz -C $pkgtmpdir
cd $pkgtmpdir/ansible-base-2.10.5/ && python setup.py build && python setup.py install


#### ansible-2.10.6-fix.tar.gz
echoinfo "installing ansible-2.10.6"
tar -zxf $_cdir/ansible-2.10.6-fix.tar.gz -C $pkgtmpdir
cd $pkgtmpdir/ansible-2.10.6-fix/ && python setup.py build && python setup.py install


#### do cleanup
echoinfo "remove tmp dir: $pkgtmpdir"
cd $_cdir
rm -rf "$pkgtmpdir"


#### create default inventory
inventory_file="/etc/ansible/hosts"

if [ -f "$inventory_file" ]; then
	echoinfo "default inventory exists: ""$inventory_file"
else
	echoinfo "create default inventory: ""$inventory_file"
	mkdir -p $(dirname $inventory_file)
	echo "# default inventory for ansible" > "$inventory_file"
	echo "[self]" >> "$inventory_file"
	echo "`hostname`  ansible_ssh_host=127.0.0.1  ansible_ssh_port=22" >> "$inventory_file"
fi

# test ansible
ansible self -m ping

exit 0
