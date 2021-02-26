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

echowarn "installing libffi before ansible installation"
echowarn "[0] yum install -y libffi libffi-devel"

echowarn "请手动升级 OpenSSL 完毕后, 注释掉下面的行, 然后再次执行安装!"
exit 1

echoinfo "(centos6.5 with python2.7) install dependencies for ansible..."
pyinstall_pkg "ecdsa-0.16.1" "$_cdir" "$pkgtmpdir"
pyinstall_pkg "pycrypto-2.6.1" "$_cdir" "$pkgtmpdir"
pyinstall_pkg "pycparser-2.20" "$_cdir" "$pkgtmpdir"
pyinstall_pkg "cffi-1.14.5" "$_cdir" "$pkgtmpdir"
pyinstall_pkg "simplejson-3.17.2" "$_cdir" "$pkgtmpdir"
pyinstall_pkg "ipaddress-1.0.23" "$_cdir" "$pkgtmpdir"
pyinstall_pkg "enum34-1.1.10" "$_cdir" "$pkgtmpdir"
pyinstall_pkg "cryptography-2.9.2" "$_cdir" "$pkgtmpdir"
pyinstall_pkg "wheel-0.30.0" "$_cdir" "$pkgtmpdir"
pyinstall_pkg "PyNaCl-1.4.0" "$_cdir" "$pkgtmpdir"
pyinstall_pkg "bcrypt-3.1.7" "$_cdir" "$pkgtmpdir"
pyinstall_pkg "paramiko-2.7.2-fix" "$_cdir" "$pkgtmpdir"
echoinfo "dependencies for ansible installed success."

echoinfo "install ansible..."
pyinstall_pkg "ansible-base-2.10.5" "$_cdir" "$pkgtmpdir"
pyinstall_pkg "ansible-2.10.6-fix" "$_cdir" "$pkgtmpdir"
echoinfo "ansible installed success."

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

echowarn "(centos6.5 with python2.7) fix ssh error"
echo "[ssh_connection]" > /etc/ansible/ansible.cfg
echo "ssh_args=" >> /etc/ansible/ansible.cfg

echowarn "(centos6.5 with python2.7) fix paramiko:"
echo "paramiko-2.7.2-fix/transport.py:120"

# test ansible
ansible self -m ping

# 对 centos6.5+python2.7

exit 0
