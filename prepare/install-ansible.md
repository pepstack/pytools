# install-ansible

仅在 master 节点按次序安装以下python包. 要求 centos7.x with python2.7.x !

1) 执行 preinstall_py27_linux.sh, 安装基础包

2) 安装 pyparsing-2.4.7 (python setup.py build && python setup.py install, 下同)

3) 安装 packaging-20.9

4) 安装 ansible-base-2.10.5

5) 安装 ansible-2.10.6-fix

注意, 原 ansible-2.10.6 包如下2个文件有 bug (python2.7 不支持 f-string 语法), 这里提供修复之后的版本:

    ansible_collections/netbox/netbox/docs/conf.py
    ansible_collections/netbox/netbox/tests/test_data.py

搜索更改的地方：#py27bug




