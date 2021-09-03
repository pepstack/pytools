# pytools

A set of devops tools for python2.7.x (Linux and Cygwin tested), python3.x (msys2 test ok)

这是一套方便 Python2.7+, Python3+ 脚本开发的工具箱。简单的复制几个文件，改个名字，就提供了命令行参数、日志等常用功能，大大提高开发速度。

请参考 tools/sample.py。默认的程序脚本 sample.py 使用同名的配置文件 options/sample.yaml。


## Prepare for python2.7

- Linux (rhel7+, centos7+, ubuntu18+)

	$ cd prepare/

	$ sudo sh ./preinstall_py27_linux.sh

- Windows7, 10 (Only for cygwin64)

	If has errors, install python2-devel or python27-devel for cygwin first (using setup-x86_64.exe).

	If an installation of usb0 driver required when running setup-x86_64.exe for cygwin, you could found it in below zip:

		libusb-win32-devel-filter-1.2.6.0.zip

	Run cygwin64 and in its terminal:

	$ cd prepare/

	$ sh ./preinstall_py27_cygwin.sh

## Prepare for python3 with msys2

	see packages/python3.md

## Run sample

	$ cd tools/

	$ ./sample.py

		[ERROR] log path not found: '/var/log/pytools-logs/sample-1.0.0'

	$ mkdir -p /var/log/pytools-logs/sample-1.0.0

	$ ./sample.py

		[2021-01-06 18:44:58 - evntlog.py:260 - init_logger] <9009:INFO> load logging.config: /cygdrive/c/Users/cheungmine/Workspace/github.com/pytools/tools/config/logger.config
		[2021-01-06 18:44:58 - logger.py:45 - set_logger] <9009:FORCE> logging config : /cygdrive/c/Users/cheungmine/Workspace/github.com/pytools/tools/config/logger.config
		[2021-01-06 18:44:58 - logger.py:46 - set_logger] <9009:FORCE> logger file    : /var/log/pytools-logs/sample-1.0.0/sample.log
		[2021-01-06 18:44:58 - logger.py:47 - set_logger] <9009:FORCE> logger level   : DEBUG
		[2021-01-06 18:44:58 - logger.py:48 - set_logger] <9009:FORCE> logger name    : main
		[INFO] TODO


NOTE: default config yaml file for sample.py (sample.yaml) lies at:

	./tools/options/sample.yaml


## Add yourself tool script

1) make a copy of files 'sample.py' and 'sample.yaml';

2) rename them as you want;

3) rewrite them as your requirement.

## revise.py

自动更新代码文件头信息的工具。要求一个代码文件(mydir/sample.h)包含如下信息头：


```
/**
 * @file:
 *   sample c header file.
 * 
 * @author: $author$
 * @create: $create$
 * @update:
 * @version:
 */

#include <stdio.h>

```

当运行 revise.py 指定这个文件的父目录，自动更新上面的文件头。

	$ cd tools/

	$ ./revise.py -F cpp -P /path/to/mydir

	$ ./revise.py -F cpp -N 0.1.1 -P /path/to/mydir

注：不包括上面的头信息的文件不会做任何改变。

## gen_project.py

按照项目模板(在 templates 目录下) 自动生成项目。默认提供的模板(%clib%)是一个 C 语言的静态库+动态库+测试程序。

按照这个模板(%clib%)生成一个你自己的项目 (例如项目名：myclib)，输入下面的命令：

  tools/gen_project.py --project=myclib

生成的项目 myclib-$timestamp 默认(未通过--output-dir 指定)在环境变量 ${WORKSPACE_ROOT_BASH} 指向的目录下。同时 gen-projects 目录下有项目打包文件:

  myclib-$timestamp.tar.gz

其中：$timestamp 是当前项目生成的时间戳。


项目 myclib 支持下面几种方式编译:

	1) 使用 vs2015+ 编译和调试 Windows 版本。打开 ${WORKSPACE_ROOT_BASH}/myclib-$timestamp/msvc/myclib-ALL-vs2015.sln，生成全部。

	2) 使用 cygwin, mingw, linux shell 编译

		$ cd ${WORKSPACE_ROOT_BASH}/myclib-$timestamp/

		$ make help

	3) 在 Windows 上使用 VSCode 本地调试 Windows 上的项目(要求 mingw)
	
		使用 VSCode 打开本地项目(项目目录必须在 ${WORKSPACE_ROOT_BASH} 下)：${WORKSPACE_ROOT_BASH}/myclib-$timestamp/

	4) 在 Windows 上使用 VSCode 远程调试 Linux 上的项目
	
		使用 VSCode 打开远程(Linux)上的项目目录(项目目录位置任意)：/path/to/myclib-$timestamp/
	
	务必参考项目的 README.md 文件获取更多帮助！

TODO:

    1) build for Android

	2) build for Mac/ios
