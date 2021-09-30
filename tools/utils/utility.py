#!/usr/bin/python
#-*- coding: UTF-8 -*-
#
# @file: utility.py
#   Python utility functions
#
# @create: 2015-12-02
#
# @update: 2021-09-06
#
#######################################################################
from __future__ import print_function
import os, errno, sys, shutil, inspect, select
import signal, threading, collections
import codecs, tempfile, fileinput

import hashlib, itertools, binascii

import time, datetime
from datetime import datetime, timedelta

import optparse

if sys.version_info < (3, 0):
    import ConfigParser
    reload(sys)
    sys.setdefaultencoding('utf-8')
elif sys.version_info <= (3, 3):
    import configparser, imp
    from configparser import ConfigParser
    imp.reload(sys)
else:
    import configparser, importlib
    from configparser import ConfigParser
    importlib.reload(sys)

#######################################################################

def error(s):
    print('\033[31m[ERROR] %s\033[0m' % s)

def info(s):
    print('\033[32m[INFO] %s\033[0m' % s)

def info_pair(name, value):
    print('    \033[34m%s=\033[0m%r' % (name, value))

def info2(s):
    print('\033[34m[INFO] %s\033[0m' % s)

def warn(s):
    print('\033[33m[WARN] %s\033[0m' % s)

def except_print(s = None):
    (errtype, errmsg, traceback) = sys.exc_info()
    if s:
        error("({}) {}: {}".format(s, errtype, errmsg))
    else:
        error("{}: {}".format(s, errtype, errmsg))

def pretty_dict(d, indent=2, ensure_ascii=False, sort_keys=True, separators=(',', ': ')):
    import json
    return json.dumps(d, indent=indent, ensure_ascii=ensure_ascii, sort_keys=sort_keys, separators=separators)

def print_object(obj):
    print("%r: %s = {\n%s\n}\n" % (
            obj,
            obj.__class__,
            '\n'.join(['  %s: %s' % item for item in obj.__dict__.items()]))
        )


def list_append(l, elem):
    l.append(elem)
    return l[-1]


def list_addnot(l, elem):
    if elem not in l:
        l.append(elem)
        return True
    else:
        return False


def list_addnot_list(l, elems):
    for elem in elems:
        list_addnot(l, elem)


def list_addnot_sort(l, elem):
    if elem not in l:
        l.append(elem)
        l.sort()
        return True
    else:
        return False


def dictlist_add(dl, pair):
    added = False
    try:
        (key, elem) = pair
        if elem not in dl[key]:
            dl[key].append(elem)
            added = True
    except KeyError:
        dl[key] = [elem]
        added = True
    return added


def dictlist_add_sort(dl, pair):
    added = False
    try:
        (key, elem) = pair
        if elem not in dl[key]:
            dl[key].append(elem)
            added = True
    except KeyError:
        dl[key] = [elem]
        added = True
    finally:
        dl[key].sort()
        pass
    return added


def dict_to_list(d):
    kl = d.keys()
    vl = d.values()
    l = [ (k, v) for k, v in zip(kl, vl) ]
    return l


def split_strip(l, div=","):
    if l is None:
        return None
    elif isinstance(l, str):
        arr = l.split(div)
        return [s.strip() for s in arr if s.strip()]
    elif isinstance(l, list):
        return [s.strip() for s in l if s.strip()]
    elif isinstance(l, dict):
        return dict_to_list(l)
    else:
        arr = str(l).split(div)
        return [s.strip() for s in arr if s.strip()]


def kvlist_sorted(l):
    d = collections.OrderedDict()
    if isinstance(l, list):
        for el in l:
            if isinstance(el, dict):
                k, v = el.items()[0]
                d[k] = v
            else:
               d[el] = "N/A"
    elif l is not None:
        keys = sorted(l.keys())
        for k in keys:
            d[k] = l[k]
    return zip(d.keys(), d.values())


def replace_var(s, varsdict, begintag = "{{", endtag = "}}"):
    try:
        var = s[s.index(begintag) + len(begintag) : s.index(endtag)]
        rep = varsdict[var]
        s = s.replace("%s%s%s" % (begintag, var, endtag), rep)
        return replace_var(s, varsdict, begintag, endtag)
    except (ValueError, KeyError, TypeError, AttributeError):
        return s


# dl = { "k1": ["v1", "v2", "v3"], "k2": [9, 5, 0], ... }
def dict_vlist_add(dl, k, v):
    try:
        vl = dl[k]
    except KeyError:
        dl[k] = []
        vl = dl[k]
    finally:
        list_addnot(vl, v)


def dict_dict_vlist_add(ddl, dk, k, v):
    try:
        dl = ddl[dk]
    except KeyError:
        ddl[dk] = {}
        dl = ddl[dk]
    finally:
        dict_vlist_add(dl, k, v)

#######################################################################

# 当前进程 pid, pname
def pidname():
    import multiprocessing
    return (os.getpid(), multiprocessing.current_process().name)


def check_import_module(module_name):
    import importlib
    try:
        module = importlib.import_module(module_name)
        return module
    except ImportError as ie:
        error("ImportError: {}.".format(str(ie)))
        sys.exit(-1)


def check_start_daemon(appName, daemon):
    if daemon:
        cmdargs = filter(lambda x: x != '--daemon', sys.argv[1:])
        startcmd = "nohup {prog:} {cmdline:} > /dev/null 2>&1 &".format(prog=sys.argv[0], cmdline=' '.join(cmdargs))
        info("startcmd=[{}]".format(startcmd))
        ret = os.system(startcmd)
        if ret == 0:
            info2("{} start daemon succeeded.".format(appName))
        else:
            error("{} start daemon failed.".format(appName))
        sys.exit(ret)


#######################################################################
# returns current datetime as string
def nowtime(dtfmt = '%Y-%m-%d %H:%M:%S'):
    return time.strftime(dtfmt, time.localtime(time.time()))


def datetime_to_string(dt = None, ms_width = 0, setdefault = datetime.now()):
    if dt is None:
        dt = setdefault
    dtfmt = '%Y-%m-%d %H:%M:%S.%f'
    y,m,d,H,M,S = dt.timetuple()[:6]
    ms = timedelta(microseconds = round(dt.microsecond/1000.0)*1000)
    ms_date = datetime(y, m, d, H, M, S) + ms
    return ms_date.strftime(dtfmt)[: (ms_width - 6)].strip('.')


def string_to_datetime(dtstr = None, setdefault = '9999-12-31 23:59:59.999999'):
    if dtstr is None:
        dtstr = setdefault
    if dtstr.rfind('.') == -1:
        dtfmt = '%Y-%m-%d %H:%M:%S'
    else:
        dtfmt = '%Y-%m-%d %H:%M:%S.%f'
    return time.strptime(dtstr, dtfmt)


# 分析路径字符串, 得到分组路径: [[group1],[group2],[group3]]
#  "/tmp/logstash/a.log"
#  "/tmp/logstash/{a.log,b.log}"
#  "/tmp/logstash/{a.log,b.log}:/tmp/logstash2/{c.log,d.log}"
#  "./stashcsv::/tmp/stash::/opt{a,b,c}"
#
def parse_path_groups(pathstr):
    pathgrps = pathstr.split('::')
    parsed_path_groups = []
    for grpstr in pathgrps:
        arrpaths = []
        for pl in grpstr.split(':'):
            s1, s2 = pl.find("{"), pl.find("}")
            if s1 > 1 and s2 > s1 + 1:
                path = pl[0 : s1].strip()

                for sub in pl[s1 + 1 : s2].split(','):
                    relp = os.path.join(path, sub.strip().rstrip('/'))
                    arrpaths.append(os.path.realpath(relp))
            elif s1 < 0 and s2 < 0:
                relp = pl.strip().rstrip('/')
                arrpaths.append(os.path.realpath(relp))
        parsed_path_groups.append(arrpaths)
    return parsed_path_groups


# get filename by minutes
#   t = "2018-12-31 23:59:59"
#
def name_by_split_minutes(dtstr, splitMinutes, prefixName = None, suffixName = None):
    if splitMinutes >= 60:
        # by hour
        SPLIT_HOURS = (splitMinutes + 59)/60
        dtstr = dtstr[:dtstr.find(':')]
        d = dtstr[:dtstr.find(' ')].replace('-', '').strip()
        h = int(dtstr[dtstr.find(' '):].strip())
        h = (h/SPLIT_HOURS) * SPLIT_HOURS

        if prefixName:
            if suffixName:
                return "%s%s%02d%s" % (prefixName, d, h, suffixName)
            else:
                return "%s%s%02d" % (prefixName, d, h)
        else:
            if suffixName:
                return "%s%02d%s" % (d, h, suffixName)
            else:
                return "%s%02d" % (d, h)
    else:
        m = int(dtstr[dtstr.find(':') + 1 : dtstr.rfind(':')])
        m = (m / splitMinutes) * splitMinutes
        dh = dtstr[ : dtstr.find(':')].replace(' ', '').replace('-', '').strip(' ')

        if prefixName:
            if suffixName:
                return "%s%s%02d%s" % (prefixName, dh, m, suffixName)
            else:
                return "%s%s%02d" % (prefixName, dh, m)
        else:
            if suffixName:
                return "%s%02d%s" % (dh, m, suffixName)
            else:
                return "%s%02d" % (dh, m)


#######################################################################

def sig_chld(signo, frame):
    pid, status = os.waitpid(-1, os.WNOHANG)
    if pid:
        error("child(%d) on signal(SIGCHLD)." % pid)
    pass


def sig_int(signo, frame):
    error("process(%d) on int signal(SIGINT)." % os.getpid())
    os.kill(os.getpid(), 9)
    pass


def sig_term(signo, frame):
    error("process(%d) on term signal(SIGTERM)." % os.getpid())
    os.kill(os.getpid(), 9)
    pass


def select_sleep(timeout_ms):
    select.select([], [], [], timeout_ms*0.001)
    pass


def is_exit_process(exit_queue, timeout_ms, exit_flag = 'EXIT'):
    from multiprocessing import Queue
    from Queue import Empty

    is_exit, arg = False, None

    try:
        if timeout_ms == 0:
            flag, arg = exit_queue.get_nowait()
        else:
            flag, arg = exit_queue.get(block=True, timeout=timeout_ms*0.001)

        if flag == exit_flag:
            is_exit = True
    except Empty:
        pass
    finally:
        return (is_exit, arg)


#######################################################################
# for case in switch(var):
#   if case("a"):
#       print("is a")
#       break
#   if case("b"):
#       print("is b")
#       break
#   else:
#       print("other")
#
class switch(object):
    def __init__ (self, value):
        self.value=value
        self.fall=False
    def __iter__ (self):
        yield self.match
        raise StopIteration
    def match (self, *args):
        if self.fall or not args:
            return True
        elif self.value in args:
            self.fall=True
            return True
        else:
            return False


#######################################################################

def init_parser_group(**kargs):
    apphome = kargs.get('apphome')
    appname = kargs.get('appname')
    appver = kargs.get('appver')
    apphelp = kargs.get('apphelp')
    usage = kargs.get('usage', '%prog [options] ...')
    group_options = kargs.get('group_options')

    profile  = "\033[32m************************************************************************\033[32;m\n" + \
        "\033[32m* %-72s *\033[32;m\n" % (appname + " version: " + appver)
    helps = apphelp.split('\n')
    for helpstr in helps:
        profile += "\033[32m* %-72s *\033[32;m\n" % helpstr
    profile += "\033[32m************************************************************************\033[32;m"

    parser = optparse.OptionParser(usage=usage,version="%prog " + appver)

    parser.add_option("-v", "--verbose",
                action="store_true", dest="verbose", default=False,
                help="verbose or not (default not verbose).")

    parser.add_option("-q", "--quiet",
                action="store_false", dest="verbose",
                help="quiet (no output).")

    app_group = optparse.OptionGroup(parser, appname, apphelp)

    if group_options:
        yamlmod = check_import_module("yaml")

        if isinstance(group_options, list):
            options_files = group_options
        elif isinstance(group_options, tuple):
            options_files = list(group_options)
        elif isinstance(group_options, str):
            options_files = group_options.split(",")
        else:
            raise TypeError("group_options")

        for options_file in options_files:
            fd = open_file(options_file, 'r')
            with fd:
                try:
                    optscfg = yamlmod.safe_load(fd)
                except:
                    optscfg = yamlmod.load(fd, Loader=yamlmod.FullLoader)
                pass

                for grpkey in optscfg.keys():
                    title = optscfg[grpkey]['title']
                    descr = optscfg[grpkey]['description']
                    gopts = optscfg[grpkey].get('options', None)

                    title = title.replace("$APPNAME", appname).replace("$APPHELP", apphelp).replace("$APPVER", appver)
                    descr = descr.replace("$APPNAME", appname).replace("$APPHELP", apphelp).replace("$APPVER", appver)

                    if title == appname:
                        group = app_group
                    else:
                        group = optparse.OptionGroup(parser, title, descr)

                    parser.add_option_group(group)

                    if gopts:
                        for optdict in gopts:
                            # python3: 'dict_keys' object is not subscriptable
                            dest = list(optdict.keys())[0]
                            
                            optcfg = optdict[dest]

                            optarg = optcfg.get('optarg', "--" + dest.lower().replace("_", "-"))

                            action = optcfg.get('action', 'store')
                            type = optcfg.get('type', 'string')

                            defval = optcfg.get('default', None)
                            if isinstance(defval, str):
                                defval = defval.replace("$APPNAME", appname).replace("$APPHOME", apphome).replace("$APPVER", appver)

                            helpstr = optcfg.get('help', None)
                            if helpstr:
                                helpstr = helpstr.replace("$APPNAME", appname).replace("$APPVER", appver).replace("$APPHOME", apphome)

                            if action == "store_true":
                                metavar = optcfg.get('metavar', False)
                            else:
                                metavar = optcfg.get('metavar', optarg.split("-")[-1].upper())

                            if defval is not None:
                                helpstr += " ('%s' default)" % str(defval)
                            else:
                                helpstr += " ('None' default)"

                            args = optarg.split(' ')
                            if len(args) == 2:
                                if action == "store_true":
                                    group.add_option(args[0], args[1], action=action, dest=dest, default=defval, help=helpstr)
                                else:
                                    group.add_option(args[0], args[1], action=action, dest=dest, type=type, default=defval, help=helpstr, metavar=metavar)
                            else:
                                if action == "store_true":
                                    group.add_option(args[0], action=action, dest=dest, default=defval, help=helpstr)
                                else:
                                    group.add_option(args[0], action=action, dest=dest, type=type, default=defval, help=helpstr, metavar=metavar)
                            pass

    return (parser, app_group, optparse, profile)


def assert_notnone_attrs(options, attrs):
    try:
        for attr in attrs:
            attrval = getattr(options, attr)
            assert attrval, "attribute '%s' not given" % attr
    except AssertionError as reason:
        error("%s: %s" %(reason.__class__.__name__, reason))
        sys.exit(-4)
        pass


def print_options_attrs(options, attrs):
    for attr in attrs:
        attrval = getattr(options, attr)
        info_pair(attr, attrval)
        pass


def print_options_attrs2(options, attrs2):
    for attr, display in attrs2:
        attrval = getattr(options, attr)
        info_pair(display, attrval)
        pass


def options_getattr_default(options, attrname, defval):
    try:
        return getattr(options, attrname)
    except AttributeError:
        return defval


def read_config_file(configFile, encodingPage='utf-8'):
    # https://www.cnblogs.com/huey/p/4334152.html
    if sys.version_info < (3, 0):
        config = ConfigParser.SafeConfigParser()
    else:
        config = ConfigParser()
    with codecs.open(configFile, 'r', encoding=encodingPage) as fd:
        if sys.version_info < (3, 0):
            config.readfp(fd)
        else:
            config.read_file(fd)
    return config
#######################################################################

def open_file(fname, mode='w+b', encoding='utf-8'):
    fd = codecs.open(fname, mode, encoding)
    return fd


def file_exists(pathfile):
    ret = False
    try:
        if pathfile and os.path.exists(pathfile) and os.path.isfile(pathfile):
            ret = True
    except:
        pass
    finally:
        return ret


def dir_exists(path):
    ret = False
    try:
        if path and os.path.isdir(path) and os.path.exists(path):
            ret = True
    except:
        pass
    finally:
        return ret


def close_file_nothrow(fd):
    if not fd is None:
        try:
            fd.close()
        except:
            pass


def remove_file_nothrow(fname):
    if file_exists(fname):
        try:
            os.remove(fname)
        except OSError:
            pass
        except:
            pass


def make_dirs_nothrow(path, mode='0755'):
    try:
        os.makedirs(path, mode)
    except OSError as e:
        if e.errno == errno.EEXIST:
            # [Errno 17] File exists
            os.chmod(path, mode)
        else:
            # re-raise the exception
            raise


def file_size_nothrow(fname):
    size = -1
    try:
        size = os.stat(fname).st_size
    except:
        pass
    finally:
        return size


def file_mtime_nothrow(fname):
    mtime = 0
    try:
        mtime = os.stat(fname).st_mtime
    except:
        pass
    finally:
        return mtime


def read_first_line_nothrow(fname):
    fd, line = None, None
    try:
        fd = open(fname, "r")
        line = fd.readline().strip('\n')
    except:
        pass
    finally:
        close_file_nothrow(fd)
        return line


def write_first_line_nothrow(fname, line):
    fd, ret = None, False
    try:
        fd = open(fname, "w", 0)
        fd.write(line)
        ret = True
    except:
        pass
    finally:
        close_file_nothrow(fd)
        return ret


def read_file_content_utf8(pathfile, tabreplace = "    ", rtrimspace = False):
    content = ""
    fd = None
    try:
        fd = open_file(pathfile, mode='r+b', encoding='utf-8')
        for line in fd.readlines():
            if tabreplace and pathfile.find("Makefile") == -1:
                line = line.replace('\t', tabreplace)

            if rtrimspace:
                a = len(line)
                line = line.rstrip('\n')
                b = len(line)
                line = line.rstrip()

                while b < a:
                    b += 1
                    line += '\n'

            content += line.encode('utf-8')
    finally:
        if fd:
            fd.close()
        pass
    return content


def read_properties(pathfile, encoding='utf-8'):
    fd, props, comments, prop = codecs.open(pathfile, mode='r+b', encoding=encoding), [], [], None
    try:
        for l in fd.readlines():
            line = l.strip()
            if prop is None:
                if line.startswith('#'):
                    # ignore comment
                    comments.append(line)
                    continue
                else:
                    eqat = line.find('=')
                    if eqat == -1:
                        # name => []
                        prop = (line.rstrip('\\').strip(), [])
                    else:
                        # name => value
                        prop = (line[0: eqat].strip(), [line[eqat + 1: ].rstrip('\\').strip()])
                    pass
            else:
                (n, vl) = prop
                vl.append(line.rstrip('\\').strip())
                prop = (n, vl)

            if not line.endswith('\\'):
                props.append(prop)
                prop = None
        return props, comments
    finally:
        fd.close()


def remove_properties(properties, propname):
    if properties is None:
        return None
    else:
        for prop in properties:
            (name, _) = prop
            if propname == name:
                properties.remove(prop)
                return prop
        return None


def upsert_properties(properties, prop):
    (name, _), ret = prop, []
    if properties is None:
        ret = [prop]
    else:
        added = False
        for el in properties:
            if el[0] == name:
                ret.append(prop)
                added = True
            else:
                ret.append(el)
        if not added:
            ret.append(prop)
    return ret


def relay_read_messages(pathfile, posfile, stopfile, chunk_size=65536, read_maxsize=16777216, message_separator='\n'):
    infd, messages, last_position, position = (None, [], 0, 0)

    if not file_exists(posfile):
        os.mknod(posfile)
        write_first_line_nothrow(posfile, str(last_position))

    if file_exists(posfile):
        last_position = int(read_first_line_nothrow(posfile))
        position = last_position

    try:
        infd = open(pathfile, 'rb')

        while position - last_position < read_maxsize:

            # 移动infd文件第position个字节处, 绝对位置
            infd.seek(position, 0)

            chunk = infd.read(chunk_size)

            if not chunk:
                # read EOF of source
                break
            else:
                start = 0
                end = start
                cbsize = len(chunk)

                for i in xrange(cbsize):
                    end = end + 1
                    if chunk[i] == message_separator:
                        line = chunk[start : end]
                        position = position + end - start
                        start = end

                        msg = line.strip(" \r\n").strip(message_separator)
                        if msg and len(msg):
                            messages.append(msg)

                # 成功保存当前位置点
                if position > last_position:
                    write_first_line_nothrow(posfile, str(position))

            if file_exists(stopfile):
                break
    finally:
        close_file_nothrow(infd)
        pass

    return (messages, last_position, position)


def write_lines(wfd, lines, encoding=None):
    if encoding:
        for l in lines:
            wfd.write(unicode(l, encoding))
    else:
        for l in lines:
            wfd.write(l)
    pass


def writeln_lines(wfd, lines, encoding=None):
    if encoding:
        for l in lines:
            wfd.write(unicode(l, encoding))
            wfd.write(unicode('\n', encoding))
    else:
        for l in lines:
            wfd.write(l)
            wfd.write('\n')
    pass


def write_file(fd, encoding, format = None, *arg):
    if format:
        fd.write(unicode((format % arg), encoding))
    pass


def write_file_utf8(fd, format = None, *arg):
    if format:
        content = format % arg
        fd.write(unicode(content, 'utf-8'))
    pass

def writeln_file_utf8(fd, format = None, *arg):
    if format:
        content = format % arg
        fd.write(unicode(content, 'utf-8'))
    fd.write(unicode('\n', 'utf-8'))
    pass

def remove_bom_header(filename):
    BOM = b'\xef\xbb\xbf'
    try:
        f = open(filename, 'rb')
        if f.read(3) == BOM:
            fbody = f.read()
            f.close()

            with open(filename, 'wb') as f:
                f.write(fbody)
    finally:
        f.close()


def add_bom_header(filename):
    BOM = b'\xef\xbb\xbf'
    try:
        f = open(filename, 'rb')
        if f.read(3) != BOM:
            f.close()
            f = open(filename, 'rb')
            fbody = f.read()
            f.close()
            with open(filename, 'wb') as f:
                f.write(BOM)
                f.write(fbody)
    finally:
        f.close()


# deprecated: create file and write to it
#
def create_output_file(outfile, output_callback, param = None, fileExistsError=True, verboseInfo=False):
    import os, tempfile, codecs, shutil
    warn("create_output_file() is deprecated. please use create_outfile() !")
    # create temp file
    tmpfd = tempfile.NamedTemporaryFile(delete = False)
    tmpfname = tmpfd.name
    tmpfd.close()

    try:
        if fileExistsError:
            # failed if file existed
            if os.path.isfile(outfile):
                raise OSError(-1001, "FileExistsError: %s" % outfile)

        # create path if not exists
        path = os.path.dirname(outfile);
        if not os.path.exists(path):
            os.makedirs(path)

        fd = open_file(tmpfname)
        try:
            if output_callback:
                output_callback(fd, param)
        finally:
            fd.close()
            pass

        # copy tmpfile to destfile
        if os.path.basename(outfile) != '~':
            shutil.copy2(tmpfname, outfile)
            if verboseInfo:
                info("create file: %s" % outfile)
        else:
            if verboseInfo:
                info("create dir: %s" % os.path.dirname(outfile))
            pass
    finally:
        os.unlink(tmpfname)


# create file and write to it
#
def create_outfile(outfile, write_callback, userarg = None, **kvargs):
    import os, tempfile, codecs, shutil

    # configs
    fileExistsAsError = kvargs.get('fileExistsAsError', False)
    makedirsIfNotExists = kvargs.get('makedirsIfNotExists', True)
    charsetEncoding = kvargs.get('charsetEncoding', 'utf-8')
    chunkSizeBytes = kvargs.get('chunkSizeBytes', 4096)

    # create temp file
    tmpfd = tempfile.NamedTemporaryFile(delete = False)
    tmpfname = tmpfd.name
    tmpfd.close()

    try:
        if os.path.isfile(outfile) and fileExistsAsError == True:
            raise OSError(-1001, "FileAlreadyExists: %s" % outfile)

        path = os.path.dirname(outfile)
        if not os.path.exists(path):
            if makedirsIfNotExists == True:
                os.makedirs(path)
            else:
                raise OSError(-1002, "PathNotExists: %s" % path)

        # write data to tmpfname
        try:
            # open tmpfile to write to
            if charsetEncoding is None:
                tmpfd = open(tmpfname, mode='w+b')
            else:
                tmpfd = open_file(tmpfname, mode='w+b', encoding=charsetEncoding)

            # call function to write tmpfile
            write_callback(tmpfd, userarg)
        finally:
            tmpfd.close()
            pass

        # copy tmpfile to outfile
        try:
            tmpfd, outfd = open(tmpfname, mode='r+b'), open(outfile, mode='w+b')
            chunk = tmpfd.read(chunkSizeBytes)
            while chunk:
                outfd.write(chunk)
                chunk = tmpfd.read(chunkSizeBytes)
        finally:
            tmpfd.close()
            outfd.close()
            pass
    finally:
        # always drop tmpfname
        os.unlink(tmpfname)
        pass


# 复制目录树, 并根据设置替换目标文件夹. 参考下面的例子:
#
#   copydirtree("/root/mydata", "/root/mydata2", [("%clib%", "clib")])
#
def copyfile_cb_default (src, dst, cbarg):
    info("copyfile: %s -> %s" % (src, dst))
    shutil.copyfile(src, dst)
    pass


def copydirtree(srcdir, dstdir, replaces = [], copyfile_cb = copyfile_cb_default, copyfile_cbarg = None):
    for (oldname, newname) in replaces:
        dstdir = dstdir.replace(oldname, newname)

    if not dir_exists(dstdir):
        os.makedirs(dstdir)

    for f in os.listdir(srcdir):
        srcfile = os.path.join(srcdir, f)

        for (oldname, newname) in replaces:
            f = f.replace(oldname, newname)

        dstfile = os.path.join(dstdir, f)

        if os.path.isfile(srcfile):
            copyfile_cb(srcfile, dstfile, copyfile_cbarg)
        else:
            copydirtree(srcfile, dstfile, replaces, copyfile_cb, copyfile_cbarg)
    pass


def compress_targz(outputfile_targz, source_dir):
    """
    https://www.cnblogs.com/liangqihui/p/9219333.html
    """
    import tarfile
    with tarfile.open(outputfile_targz, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))


#######################################################################

def script_abspath(frame=inspect.currentframe()):
    p = os.path.split(inspect.getfile( frame ))[0]
    absdir = os.path.realpath(os.path.abspath(p))
    return absdir


def script_abspath_parent(frame=inspect.currentframe()):
    return os.path.dirname(script_abspath(frame))


def include_dir(subdir=None, frame=inspect.currentframe()):
    # NOTES:
    # DO NOT USE __file__ !!!
    # dir = os.path.dirname(os.path.abspath(__file__))
    # __file__ fails if script is called in different ways on Windows
    # __file__ fails if someone does os.chdir() before
    # sys.argv[0] also fails because it doesn't not always contains the path
    #
    # realpath() will make your script run, even if you symlink it
    p = os.path.split(inspect.getfile( frame ))[0]
    incdir = os.path.realpath(os.path.abspath(p))
    if incdir not in sys.path:
        sys.path.insert(0, incdir)
    if subdir:
        # use this if you want to include modules from a subfolder
        incdir = os.path.realpath(os.path.abspath(os.path.join(p, subdir)))
        if incdir not in sys.path:
            sys.path.insert(0, incdir)

# cfgfile: full path for config file
# cfgitem: a config item in cfgfile might use abspath or relative path
def source_abspath(cfgfile, cfgitem=None, p=script_abspath()):
    dp = os.path.realpath(os.path.join(p, cfgfile))
    if cfgitem:
        return os.path.realpath(os.path.join(os.path.dirname(dp), cfgitem))
    else:
        return dp

#######################################################################
#enc = rc4('1234abcd', str(123))
#hstr = binascii.b2a_hex(enc)
#plain = rc4(binascii.a2b_hex(hstr), str(123))
#print plain, hstr
def rc4(data, key):
    x = 0
    box = range(256)
    for i in range(256):
        x = (x + box[i] + ord(key[i % len(key)])) % 256
        box[i], box[x] = box[x], box[i]
    x = 0
    y = 0
    out = []
    for char in data:
        x = (x + 1) % 256
        y = (y + box[x]) % 256
        box[x], box[y] = box[y], box[x]
        out.append(chr(ord(char) ^ box[(box[x] + box[y]) % 256]))
    return ''.join(out)


def md5sum_file(pathfile):
    with open(pathfile, 'rb') as fh:
        m = hashlib.md5()
        while True:
            chunk = fh.read(8192)
            if not chunk:
                break
            m.update(chunk)
        return m.hexdigest()


def md5sum_str(s, encoding='utf8'):
    return hashlib.md5(s.encode(encoding)).hexdigest()
