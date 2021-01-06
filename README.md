# pytools

python scripts tools for dev and ops.

这是一套方便 Python2.7.x 脚本开发的工具箱。简单的复制几个文件，改个名字，就提供了命令行参数、日志等常用功能，大大提高开发速度。

请参考 scripts/sample.py。默认的程序脚本 sample.py 使用同名的配置文件 options/sample.yaml。


## Prepare for python2.7

- el7 (rhel7, centos 7)

	$ cd prepare/

	$ sudo sh ./preinstall_py27_el7.sh

- cygwin amd64

	If has errors, install python27-devel for cygwin first!

	If an installation of usb0 driver required when running setup-x86_64.exe for cygwin, you could found it in below zip:
		
		libusb-win32-devel-filter-1.2.6.0.zip

	Run cygwin64 and in its terminal:

	$ cd prepare/

	$ sh ./preinstall_py27_cygwin.sh


## Run sample

	$ cd scripts/ && ./sample.py

default config yaml file for sample.py (sample.yaml) lies at:

	./scripts/options/sample.yaml


## Add your script file

1) make a copy of sample.py and sample.yaml;

2) rename them as you want;

3) rewrite them as your requirement.