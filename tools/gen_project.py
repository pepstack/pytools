#!/usr/bin/python
#-*- coding: UTF-8 -*-
#
# @file: gen_project.py
#
#   根据模板自动生成项目
# 2021-07-01
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

    if dstfile.endswith(".sh"):
        os.chmod(dstfile, stat.S_IRWXU)
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

    project_timestamp = util.nowtime('%Y%m%d.%H%M%S')

    # 模板根目录
    templateProjectDir = os.path.join(pytools_root, "templates", "%" + options.template + "%")

    #输出目录支持用环境变量: ${env:WORKSPACE_ROOT_BASH}
    output_absdir = None
    if options.output_dir.startswith("${env:") and options.output_dir.endswith("}"):
        envVar = options.output_dir[6:-1]
        output_absdir = os.getenv(envVar)
        if output_absdir is None:
            elog.error("environment variable not set: %s", envVar);
            sys.exit(1)
    else:
        output_absdir = os.path.realpath(options.output_dir)

    generateProjectDir = os.path.join(output_absdir, options.project + "-" + project_timestamp)

    if osname.startswith("cygwin_nt"):
        generateProjectDir = "/cygdrive" + generateProjectDir

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
        ,timestamp = project_timestamp
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

    genPackageFile = os.path.join(pytools_root, "gen-projects", os.path.basename(generateProjectDir) + ".tar.gz")

    util.compress_targz(genPackageFile, generateProjectDir)

    elog.force("generated project at: %s", generateProjectDir)
    elog.force("project package file: %s", genPackageFile)
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

    if osname.startswith("cygwin_nt"):
        elog.info("checking environments for Windows:")

        env_MSYS2_PATH_TYPE = os.getenv('MSYS2_PATH_TYPE')
        env_MSYS64_HOME = os.getenv('MSYS64_HOME')
        env_MSYS64_ROOT_BASH = os.getenv('MSYS64_ROOT_BASH')
        env_WORKSPACE_ROOT_BASH = os.getenv('WORKSPACE_ROOT_BASH')

        elog.force_clean("MSYS2_PATH_TYPE=%s", env_MSYS2_PATH_TYPE)
        elog.force_clean("MSYS64_HOME=%s", env_MSYS64_HOME)
        elog.force_clean("MSYS64_ROOT_BASH=%s", env_MSYS64_ROOT_BASH)
        elog.force_clean("WORKSPACE_ROOT_BASH=%s", env_WORKSPACE_ROOT_BASH)

        if env_MSYS2_PATH_TYPE is None:
            elog.error("${env:MSYS2_PATH_TYPE} not found")
            sys.exit(1)

        if env_MSYS64_HOME is None:
            elog.error("${env:MSYS64_HOME} not found")
            sys.exit(1)

        if env_MSYS64_ROOT_BASH is None:
            elog.error("${env:MSYS64_ROOT_BASH} not found")
            sys.exit(1)

        if env_WORKSPACE_ROOT_BASH is None:
            elog.error("${env:WORKSPACE_ROOT_BASH} not found")
            sys.exit(1)

        if env_MSYS2_PATH_TYPE != "inherit":
            elog.error("${env:MSYS2_PATH_TYPE} not inherit")
            sys.exit(1)        

        if env_MSYS64_HOME.startswith("/") or env_MSYS64_HOME.find("/") != -1 or env_MSYS64_HOME.find(" ") != -1:
            elog.error("${env:MSYS64_HOME} not a Windows path. for example: MSYS64_HOME=C:\DEVPACK\msys64")
            sys.exit(1)

        if not env_MSYS64_ROOT_BASH.startswith("/") or env_MSYS64_ROOT_BASH.find("\\") != -1 or env_MSYS64_ROOT_BASH.find(" ") != -1:
            elog.error("${env:MSYS64_ROOT_BASH} not a bash path. for example: MSYS64_ROOT_BASH=/C/DEVPACK/msys64")
            sys.exit(1)

        if not env_WORKSPACE_ROOT_BASH.startswith("/") or env_WORKSPACE_ROOT_BASH.find("\\") != -1 or env_WORKSPACE_ROOT_BASH.find(" ") != -1:
            elog.error("${env:WORKSPACE_ROOT_BASH} not a bash path. for example: WORKSPACE_ROOT_BASH=/C/Users/cheungmine/Workspace/github.com")
            sys.exit(1)

        WPath = env_MSYS64_HOME.upper()
        for Drv in ["C:\\", "D:\\", "E:\\", "F:\\", "G:\\", "H:\\", "J:\\", "K:\\", "\\"]:
            if WPath.startswith(Drv):
                break
        if Drv == "\\":
            elog.error("${env:MSYS64_HOME} not a Windows path. for example: MSYS64_HOME=C:\DEVPACK\msys64")
            sys.exit(1)

        BashPath = "/" + env_MSYS64_HOME[0:1] + "/" + env_MSYS64_HOME[3:].replace("\\", "/")
        if BashPath != env_MSYS64_ROOT_BASH:
            elog.error("${env:WORKSPACE_ROOT_BASH} not a slash(/) path equivalent of ${env:MSYS64_HOME}")
            sys.exit(1)

    # 主函数
    main(parser)

    sys.exit(0)
