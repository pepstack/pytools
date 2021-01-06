#!/usr/bin/python
#-*- coding: UTF-8 -*-
#
# @file: revise.py
#
#   源代码文件修改之后，运行这个脚本会自动更新代码的版本和时间
#
# @author: $author$
# @create: $create$
# @update: 2021-01-06 20:40:50
# @version: 1.0.0
########################################################################
import os, sys, stat, signal, shutil, inspect, commands, time, datetime
import yaml, codecs, uuid, platform
import optparse, ConfigParser

########################################################################
# application specific
APPFILE = os.path.realpath(sys.argv[0])
APPHOME = os.path.dirname(APPFILE)
APPNAME,_ = os.path.splitext(os.path.basename(APPFILE))
APPVER = "1.0.0"
APPHELP = "revise version and time for source code files"

########################################################################
# import your local modules
import utils.utility as util
import utils.evntlog as elog

from utils.error import try_except_log

osname = platform.system().lower()

########################################################################

file_counter = 0

# Add your specified directory to be ignored:
ignored_dirs = [
        "deps",
        "deplibs",
        "libs",
        "test",
        "doc",
        "build",
        "dist",
        "target",
        "tmp",
        "temp"
    ]


# Add your specified filename to be ignored:
ignored_files = [
        ".gitignore"
    ]


# Add your specified filter for filename to be included:
included_filter = {
    'java': ['.java', '.properties', '.xml', '.jsp', '.cresql'],
    'c': ['.h', '.c', '.mk'],
    'cpp': ['.h', '.c', '.cpp', '.cxx', '.hpp', '.mk'],
    'python': ['.py'],
    'php': ['.php'],
    'html': ['.html', '.htm', '.js', '.css'],
    'shell': ['.sh']
}


#######################################################################
files_count = 0

def parse_strarr(str):
    strs = []
    if not str:
        return strs
    arr = str.split(',')
    for src in arr:
        s = src.strip(" '")
        if len(s) > 0:
            strs.append(s)
    return strs


def test_file(pathfile, fstat):
    global files_count
    files_count += 1
    util.info("[%d] TEST: %s" % (files_count, pathfile))
    pass


def revise_file(pathfile, filename, fstat, author, verno, curtime, istest):
    global files_count

    ct = time.localtime(fstat.st_ctime)
    mt = time.localtime(fstat.st_mtime)
    at = time.localtime(fstat.st_atime)

    cts = time.strftime('%Y-%m-%d %H:%M:%S', ct)
    mts = time.strftime('%Y-%m-%d %H:%M:%S', mt)
    ats = time.strftime('%Y-%m-%d %H:%M:%S', at)

    cmds = [
        "sed -i 's/@file:.*/@file: %s/' %s" % (filename, pathfile),
        "sed -i 's/@create: $create$.*/@create: %s/' %s" % (cts, pathfile),
        "sed -i 's/@update:.*/@update: %s/' %s" % (mts, pathfile)
    ]

    if verno:
        cmds.append("sed -i 's/@version:.*/@version: %s/' %s" % (verno, pathfile))

    if author:
        cmds.append("sed -i 's/@author: $author$.*/@author: %s/' %s" % (author, pathfile))

    cmds.append("sed -i 's/ *$//' %s" % pathfile)

    for cmd in cmds:
        (retcode, retstring) = commands.getstatusoutput(cmd)

    os.utime(pathfile, (fstat.st_atime, fstat.st_mtime))

    files_count += 1

    util.info("[%d] REV: %s" % (files_count, pathfile))
    pass


def sweep_dir(path, included_exts, author, verno, curtime, istest):
    filelist = os.listdir(path)
    filelist.sort(key=lambda x:x[0:20])

    for f in filelist:
        pf = os.path.join(path, f)

        try:
            fs = os.stat(pf)
            
            mod = fs.st_mode

            if stat.S_ISDIR(mod):
                # is dir
                if f.startswith(".") or f in ignored_dirs:
                    util.warn("ignored dir: %s" % pf)
                    pass
                elif util.dir_exists(pf):
                    sweep_dir(pf, included_exts, author, verno, curtime, istest)
                    pass
                else:
                    util.error("not existing dir: %s" % pf)
                pass
            elif stat.S_ISREG(mod):
                # is file
                ignored = True

                if pf == APPFILE or f == "__init__.py":
                    pass
                elif f.startswith(".") or f.startswith("~") or f in ignored_files:
                    util.warn("ignored file: %s" % pf)
                elif not util.file_exists(pf):
                    util.error("not existing file: %s" % pf)
                else:
                    _, ext = os.path.splitext(f)
                    if ext in included_exts:
                        ignored = False
                        pass

                if not ignored:
                    if istest:
                        test_file(pf, fs)
                    else:
                        revise_file(pf, f, fs, author, verno, curtime, istest)
                    pass
        except OSError:
            util.except_print("OSError")
        except:
            util.except_print("unexcept")
    pass


########################################################################
# 主入口函数
@try_except_log
def main(parser):
    import utils.logger as logger
    (options, args) = parser.parse_args(args=None, values=None)
    loggerConfig = util.DotDict(
        logging_config = options.log_config,
        file = APPNAME + '.log',
        name = options.logger
    )
    logger_dictConfig = logger.set_logger(loggerConfig, options.log_path, options.log_level)

    # 当前脚本绝对路径
    abspath = util.script_abspath(inspect.currentframe())

    if not options.path:
        util.error("No path specified. using: -P, --path=PATH")
        exit(-1)

    # 取得配置项 options.path 的绝对路径
    pathprefix = util.source_abspath(APPFILE, options.path, abspath)

    # 取得文件扩展名数组
    included_exts = []
    filters = parse_strarr(options.filter)

    for filter in filters:
        if filter.startswith('.'):
            if filter not in included_exts:
                included_exts.append(filter)

        if filter in included_filter.keys():
            for ext in included_filter[filter]:
                if ext not in included_exts:
                    included_exts.append(ext)

    curtime = time.time()

    util.info("path:      %r" % pathprefix)
    util.info("exts:      %r" % included_exts)
    util.info("time:      %r" % curtime)

    if options.verno:
        util.info("verno:     %r" % options.verno)

    if options.author:
        util.info("author:    %r" % options.author)
  
    sweep_dir(pathprefix, included_exts, options.author, options.verno, curtime, options.test)

    pass


#######################################################################
# Usage:
#
#   $ ./revise.py -F "cpp,java" -P /path/to/file
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
