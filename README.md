# pytools

A set of devops scripts tools for python2.7.x.

这是一套方便 Python2.7.x 脚本开发的工具箱。简单的复制几个文件，改个名字，就提供了命令行参数、日志等常用功能，大大提高开发速度。

请参考 scripts/sample.py。默认的程序脚本 sample.py 使用同名的配置文件 options/sample.yaml。


## Prepare for python2.7

- Linux (rhel7+, centos7+, ubuntu18+)

	$ cd prepare/

	$ sudo sh ./preinstall_py27_linux.sh

- Windows (Only for cygwin64)

	If has errors, install python2-devel, python27-devel for cygwin first!

	If an installation of usb0 driver required when running setup-x86_64.exe for cygwin, you could found it in below zip:

		libusb-win32-devel-filter-1.2.6.0.zip

	Run cygwin64 and in its terminal:

	$ cd prepare/

	$ sh ./preinstall_py27_cygwin.sh


## Run sample

	$ cd scripts/

	$ ./sample.py

		[ERROR] log path not found: '/var/log/pytools-logs/sample-1.0.0'

	$ mkdir -p /var/log/pytools-logs/sample-1.0.0

	$ ./sample.py

		[2021-01-06 18:44:58 - evntlog.py:260 - init_logger] <9009:INFO> load logging.config: /cygdrive/c/Users/cheungmine/Workspace/github.com/pytools/scripts/config/logger.config
		[2021-01-06 18:44:58 - logger.py:45 - set_logger] <9009:FORCE> logging config : /cygdrive/c/Users/cheungmine/Workspace/github.com/pytools/scripts/config/logger.config
		[2021-01-06 18:44:58 - logger.py:46 - set_logger] <9009:FORCE> logger file    : /var/log/pytools-logs/sample-1.0.0/sample.log
		[2021-01-06 18:44:58 - logger.py:47 - set_logger] <9009:FORCE> logger level   : DEBUG
		[2021-01-06 18:44:58 - logger.py:48 - set_logger] <9009:FORCE> logger name    : main
		[INFO] TODO


NOTE: default config yaml file for sample.py (sample.yaml) lies at:

	./scripts/options/sample.yaml


## Add your script file

1) make a copy of sample.py and sample.yaml;

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

	$ cd scripts/

	$ ./revise.py -F cpp -P /path/to/mydir

	$ ./revise.py -F cpp -N 0.1.1 -P /path/to/mydir

注：不包括上面的头信息的文件不会做任何改变。