# pytools

A set of devops tools for python2.7.x.

这是一套方便 Python2.7.x 脚本开发的工具箱。简单的复制几个文件，改个名字，就提供了命令行参数、日志等常用功能，大大提高开发速度。

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

安装项目模板(在 templates 目录下) 自动生成项目。默认提供的模板(%clib%)是一个 C 语言的静态库+动态库+测试程序。

安装这个模板(%clib%)生成一个你自己的项目，按照下面的命令：

  gen_project.py --project=pureclib --force

生成的项目 pureclib 默认在 gen-projects 目录下。

支持下面几种方式编译: pureclib

	1) 使用 vs2015+ 打开 gen-projects/pureclib/msvc/pureclib-ALL-vs2015.sln，生成全部。

	2) 使用 cygwin, mingw, linux shell 编译
	
		cd gen-projects/pureclib

		make clean && make dist

TODO:

    Android

	Mac/ios
