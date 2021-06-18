#!/usr/bin/python
#-*- coding: UTF-8 -*-
#
# @file: gen_project.py
#
#   根据模板自动生成项目
#
########################################################################
from __future__ import print_function
import os, sys, stat, signal, shutil, inspect, commands, time, datetime

import yaml, codecs, uuid, platform

import optparse, ConfigParser

# http://docs.jinkan.org/docs/jinja2/
# http://docs.jinkan.org/docs/jinja2/templates.html
from jinja2 import Environment, PackageLoader, FileSystemLoader

########################################################################
# application specific
APPFILE = os.path.realpath(sys.argv[0])
APPHOME = os.path.dirname(APPFILE)
APPNAME,_ = os.path.splitext(os.path.basename(APPFILE))
APPVER = "1.0.0"
APPHELP = "Generate project by template."

########################################################################
# import your local modules
import utils.utility as util
import utils.evntlog as elog
import utils.ddict as ddict

from utils.error import try_except_log

osname = platform.system().lower()

pytools_root = os.path.dirname(APPHOME)

###############################################################
@try_except_log
def writeout_cb(fout, content):
    fout.write(content)
    pass


@try_except_log
def render_file(srcfile, dstfile, projectCfg):
    elog.debug_clean("render: %s => %s",
        os.path.relpath(srcfile, projectCfg.template_root),
        os.path.relpath(dstfile, projectCfg.generate_root))

    j2tmpl = projectCfg.j2env.get_template(os.path.relpath(srcfile, projectCfg.template_root))

    content = j2tmpl.render(
        project = ddict.dotdict(
            date = util.nowtime()
            ,name = projectCfg.project_name
            ,NAME = projectCfg.project_name.upper()
            ,vars = projectCfg.vars
            ,Guids = projectCfg.uuids
        )
    )

    util.create_outfile(dstfile, writeout_cb, content)
    pass


@try_except_log
def copy_file(srcfile, dstfile, projectCfg):
    elog.debug_clean("copy: %s => %s",
        os.path.relpath(srcfile, projectCfg.template_root),
        os.path.relpath(dstfile, projectCfg.generate_root))

    shutil.copyfile(srcfile, dstfile)
    pass


@try_except_log
def copy_project_cb(srcfile, dstfile, projectCfg):
    dstpre, ext = os.path.splitext(dstfile)

    if ext == ".template":
        render_file(srcfile, dstpre, projectCfg)
    else:
        copy_file(srcfile, dstfile, projectCfg)
    pass


###############################################################
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

    # 模板根目录
    templateProjectDir = os.path.join(pytools_root, "templates", "%" + options.template + "%")

    generateProjectDir = os.path.join(os.path.realpath(options.output_dir), options.project)

    kvpairs, varsdict = options.vars.split('&'), ddict.dotdict()
    for pair in kvpairs:
        kvpair = pair.split('=')
        key = kvpair[0].strip()
        val = kvpair[1].strip()
        varsdict[key] = val

    elog.force("template project: %s", templateProjectDir)
    elog.force("generate project: %s", generateProjectDir)
    elog.force("vars dict: %r", varsdict)

    if util.dir_exists(generateProjectDir):
        elog.warn("project already existed: %s", generateProjectDir)
        if not options.force:
            elog.warn("using '--force' to overwrite existed project");
            sys.exit(1)
        pass

    try:
        shutil.rmtree(generateProjectDir)
    except:
        pass

    uuids = []
    for i in range(0, options.num_uuids):
        uuids.append("{" + str(uuid.uuid4()).upper() + "}")

    projectCfg = ddict.dotdict(
        j2env = Environment(loader=FileSystemLoader(templateProjectDir))
        ,template_name = "%" + options.template + "%"
        ,project_name  = options.project
        ,template_root = templateProjectDir
        ,generate_root = generateProjectDir
        ,vars = varsdict
        ,uuids = uuids
    )

    util.copydirtree(projectCfg.template_root, projectCfg.generate_root,
            [
                (projectCfg.template_name, projectCfg.project_name)
                ,(projectCfg.template_name.upper(), projectCfg.project_name.upper())
            ],
            copy_project_cb, projectCfg)

    elog.force("project generated successfully at: %s", generateProjectDir)
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
