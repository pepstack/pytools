#!/usr/bin/python
#-*- coding: UTF-8 -*-
#
# @file: kafka_bulkload.py
#
#   大量写入消息到 kafka topic.
#
# Dependencies:
#   python2.7
#   kafka-python-2.0.2.tar.gz
#
# 测试
#   $ /opt/anaconda2/bin/python2.7 kafka_bulkload.py -T mpaylog
#
# See Also:
#    http://kafka-python.readthedocs.io/en/master/apidoc/KafkaProducer.html
#
# version: 1.0.0
# create: 2020-11-23
# update: 2021-01-26
#
# 删除 kafka topic:
#   auto.create.topics.enable = false
#   delete.topic.enable=true
#
# $ kafka-topics.sh --delete --zookeeper zk1:2181,zk2:2182,zk3:2183 --topic mpaylog
#
########################################################################
from __future__ import print_function
import os, sys, stat, signal, shutil, inspect, commands, time, datetime

import yaml, codecs, uuid, platform

import optparse, ConfigParser

# kafka-python
#   https://pypi.org/project/kafka-python/
from kafka import KafkaProducer
from kafka.errors import KafkaError
from kafka import TopicPartition

# KafkaConsumer, KafkaClient, SimpleProducer, SimpleConsumer

# avro
import avro.schema
import avro.io
from avro.io import DatumWriter

########################################################################
# import your local modules
import utils.utility as util
import utils.evntlog as elog

from utils.error import try_except_log

osname = platform.system().lower()

########################################################################
# application specific
APPFILE = os.path.realpath(sys.argv[0])
APPHOME = os.path.dirname(APPFILE)
APPNAME,_ = os.path.splitext(os.path.basename(APPFILE))
APPVER = "1.0.0"
APPHELP = "load bulky messages into kafka topic"

########################################################################
def makeup_messages(nmsgs, gid, partition_id, logtime):
    messages = []

    for i in range(0, nmsgs):
        custid = "1"
        gameid = gid
        accnt = "0-3119404451"
        ip = "192.168.10.121"

        nip = "61443341500"
        fillpoint = "100.00"
        objid="www.github.com"
        orderid="9603267803212"
        orderidpt="326032678106535710"

        zoneid="2"

        line = "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % (logtime, custid, gameid, accnt, ip, nip, fillpoint, objid, orderid, orderidpt, zoneid)

        messages.append(line)
        pass

    return messages


@try_except_log
def produce_messages(kaf_producer, gid, nmsgs, topic, logtime = None, partition_id = 0, utf8_encode = False, send_verbose = False):
    if logtime:
        messages = makeup_messages(nmsgs, gid, partition_id, logtime)
    else:
        messages = makeup_messages(nmsgs, gid, partition_id, util.datetime_to_string())

    for line in messages:
        if utf8_encode:
            line = line.encode('utf-8')

        if send_verbose:
            elog.force("-{{%s}}-", line)

        kaf_producer.send(topic, value=line, partition=partition_id)
        pass

    if nmsgs > 0:
        kaf_producer.flush()


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

    servers = options.bootstrap_servers.split(",")

    kaf_producer = KafkaProducer(
                client_id = options.client_id,
                bootstrap_servers = options.bootstrap_servers,
                acks = 1,
                batch_size = 102400,
                linger_ms = 5)

    kafka_topic = options.kafka_topic

    for partition_id in range(0, options.partitions):
        for r in range(0, options.rounds):
            elog.info("(round:%d/%d) produce %d messages to kafka {%s#%d}...", r, options.rounds, options.messages, kafka_topic, partition_id)

            produce_messages(kaf_producer, options.gameid, options.messages, kafka_topic, options.logtime, partition_id, options.utf8_encode, options.send_verbose)

    elog.force("total %d messages produced to kafka {%s#%d}.", options.rounds * options.messages, kafka_topic, partition_id)
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
