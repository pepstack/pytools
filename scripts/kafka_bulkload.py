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
@try_except_log
def produce_messages(kaf_producer, topic, partition_id = 0, utf8_encode = False, send_verbose = False):
    messages = [
        "2021-01-26 16:10:19,1,5078,0-1119404459,36.159.130.135,614433415,128.00,com.juzi.balls.mogu.140,key9603267803212,qa316032678106525710,2"
    ]

    for line in messages:
        if utf8_encode:
            line = line.encode('utf-8')

        if send_verbose:
            elog.force("-{{%s}}-", line)

        kaf_producer.send(topic, value=line, partition=partition_id)
        pass

    if len(messages) > 0:
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
        elog.info("produce messages to kafka...{%s#%d}", kafka_topic, partition_id)
        produce_messages(kaf_producer, kafka_topic, partition_id, options.utf8_encode, options.send_verbose)
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
