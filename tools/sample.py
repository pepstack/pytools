#!/usr/bin/python
#-*- coding: UTF-8 -*-
#
# @file: sample.py
#
# refer docs:
#   https://www.cnblogs.com/dachenzi/p/8242713.html
#   https://www.cnblogs.com/mauricewei/p/10056379.html
#
# init created: 2015-12-22
# last updated: 2021-01-06
########################################################################
from __future__ import print_function
import os, sys, stat, signal, shutil, inspect, time, datetime

import yaml, codecs, uuid, platform

import optparse

if sys.version_info < (3, 0):
    import ConfigParser
    reload(sys)
    sys.setdefaultencoding('utf-8')
elif sys.version_info <= (3, 3):
    import configparser, imp
    imp.reload(sys)
else:
    import configparser, importlib
    importlib.reload(sys)

# http://docs.jinkan.org/docs/jinja2/
# http://docs.jinkan.org/docs/jinja2/templates.html
#!-- from jinja2 import Environment, PackageLoader, FileSystemLoader

########################################################################
# application specific
APPFILE = os.path.realpath(sys.argv[0])
APPHOME = os.path.dirname(APPFILE)
APPNAME,_ = os.path.splitext(os.path.basename(APPFILE))
APPVER = "1.0.0"
APPHELP = "A python sample"

########################################################################
# import your local modules
import utils.utility as util
import utils.evntlog as elog
import utils.ddict as ddict

from utils.error import try_except_log

osname = platform.system().lower()

########################################################################
# 主入口函数
@try_except_log
def main(parser):
    import utils.logger as logger
    (options, args) = parser.parse_args(args=None, values=None)
    loggerConfig = ddict.dotdict(
        logging_config = options.log_config,
        file = APPNAME + '.log',
        name = options.logger
    )
    logger_dictConfig = logger.set_logger(loggerConfig, options.log_path, options.log_level)

    util.info("TODO")
    pass


########################################################################
# Usage:
#    $ %prog
#  or
#    $ %prog --force
#
if __name__ == "__main__":
    parser, group, optparse, profile = util.init_parser_group(
        apphome = APPHOME,
        appname = APPNAME,
        appver = APPVER,
        apphelp = APPHELP,
        usage = "%prog [Options]",
        group_options = os.path.join(APPHOME, "options", APPNAME + ".yaml")
    )

    # 主函数
    main(parser)

    sys.exit(0)
