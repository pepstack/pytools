#!/usr/bin/python
#-*- coding: UTF-8 -*-
#
# @file: kafka_dumpout.py
#
#   导出 kafka topic 到文件.
#   默认导出文件位置:  /tmp/kafka-dumps/${topic}/${group}_${offset}-${limit}.dumpout
#
# Dependencies:
#   python2.7
#   kafka-python-2.0.2.tar.gz
#
# 测试
#   $ /opt/anaconda2/bin/python2.7 kafka_dumpout.py -T mpay-log
#
# See Also:
#    http://kafka-python.readthedocs.io/en/master/apidoc/KafkaProducer.html
#
# version: 1.0.0
# create: 2020-11-23
# update: 2020-11-23
#
########################################################################
from __future__ import print_function
import os, sys, stat, signal, shutil, inspect, commands, time, datetime

import yaml, codecs, uuid, platform

import optparse, ConfigParser

# kafka-python
#   https://pypi.org/project/kafka-python/
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from kafka import TopicPartition

########################################################################
# application specific
APPFILE = os.path.realpath(sys.argv[0])
APPHOME = os.path.dirname(APPFILE)
APPNAME,_ = os.path.splitext(os.path.basename(APPFILE))
APPVER = "1.0.0"
APPHELP = "dumps out all messages of kafka topic to local file"

########################################################################
# import your local modules
import utils.utility as util
import utils.evntlog as elog

from utils.error import try_except_log

osname = platform.system().lower()

########################################################################
@try_except_log
def consume_messages(kaf_consumer, kvcfg):
    wfd = util.open_file(kvcfg.dumpfile)

    start, count = 0, 0

    try:
        for record in kaf_consumer:
            if start < kvcfg.offset:
                start += 1
            else:
                count += 1

                if kvcfg.limit > 0 and count > kvcfg.limit:
                    elog.debug("[%s] dumped: %d", kvcfg.topic, kvcfg.limit)
                    break

                util.writeln_file_utf8(wfd, record.value)

                if count % 10000 == 0:
                    elog.debug("[%s] dumped: %d", kvcfg.topic, count)
                    wfd.flush();
    finally:
        wfd.flush();
        util.close_file_nothrow(wfd)
        pass

    elog.info("dump file ok: %s", kvcfg.dumpfile)
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

    group_id = options.group_id.replace("${time}", str(int(time.time())))

    dumpdir = os.path.join(options.dump_root, "kafka-dumpout", options.kafka_topic)

    util.make_dirs_nothrow(dumpdir)

    dumpfile = os.path.join(dumpdir, "%s_%d-%d.dumpout" % (group_id, options.offset, options.limit))

    util.remove_file_nothrow(dumpfile)

    servers = options.kafka_servers.split(",")

    kaf_consumer = KafkaConsumer(
            options.kafka_topic
            ,group_id = group_id
            ,bootstrap_servers = servers
            ,auto_offset_reset = 'earliest'
            ,enable_auto_commit = True        # 自动提交消费数据的offset
            ,consumer_timeout_ms = 10000      # 如果 10 秒内 kafka 中没有可供消费的数据自动退出
        )

    elog.info("topic: %r", options.kafka_topic)
    elog.info("group: %s", group_id)
    elog.info("offset: %d", options.offset)
    elog.info("limit: %d", options.limit)
    elog.info("dump file: %s", dumpfile)

    consume_messages(kaf_consumer, util.DotDict(
        dumpfile = dumpfile,
        topic = options.kafka_topic,
        offset = options.offset,
        limit = options.limit)
    )
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
