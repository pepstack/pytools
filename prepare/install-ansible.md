# install-ansible

## 介绍

ansible是基于 python （2.7， 3.x）的一套完整的自动化执行任务模块，是一款简单的运维自动化工具，
只需要使用ssh协议连接就可以来进行系统管理，自动化执行命令，部署等任务。ansible不需要单独安装
客户端，也不需要启动任何服务。ansible playbook 采用yaml配置，对于自动化任务执行过一目了然。

ansible组成结构:

    ansible - 是ansible的命令工具，核心执行工具；一次性或临时执行的操作都是通过该命令执行。

    playbook - 任务剧本（又称任务集），编排定义 ansible 任务集的配置文件，由 ansible 顺序依
               次执行，yaml格式。

    inventory - ansible 管理主机的清单，默认是 /etc/ansible/hosts 文件。

    modules - ansible 执行命令的功能模块，还可以自定义模块。

    plugins - 模块功能的补充，常有连接类型插件，循环插件，变量插件，过滤插件，插件功能用的较少。

    API - 提供给第三方程序调用的应用程序编程接口。


## 安装

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

## 测试

配置管理节点到子节点的免密登录（复制管理节点的公钥证书到每个被管理的节点）。

```
ssh-copy-id ~/.ssh/id_rsa.pub root@192.168.51.111
ssh-copy-id ~/.ssh/id_rsa.pub root@192.168.51.112
ssh-copy-id ~/.ssh/id_rsa.pub root@192.168.51.113
```

编写默认的主机的清单文件（/etc/ansible/hosts），内容如下：

```
[yarntest]
yarntest1 ansible_ssh_host=192.168.51.111 ansible_ssh_port=22
yarntest2 ansible_ssh_host=192.168.51.112 ansible_ssh_port=22
yarntest3 ansible_ssh_host=192.168.51.113 ansible_ssh_port=22
```

在管理节点执行ping命令：

ansible yarntest -m ping

得到成功的返回结果：

yarntest1 | SUCCESS => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python"
    },
    "changed": false,
    "ping": "pong"
}
yarntest2 | SUCCESS => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python"
    },
    "changed": false,
    "ping": "pong"
}
yarntest3 | SUCCESS => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python"
    },
    "changed": false,
    "ping": "pong"
}


## 参考

    [ansible快速入门](https://www.cnblogs.com/yanjieli/p/10969089.html)
