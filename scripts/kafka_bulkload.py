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

import yaml, codecs, uuid, platform, string, random

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
sum_value = 0.00

def makeup_messages(nmsgs, gamids, logtime, urls):
    messages = []

    global sum_value

    if not logtime:
        finishtime = util.datetime_to_string(None, 0, datetime.datetime.now())

    for i in range(0, nmsgs):
        urlcols = random.choice(urls).strip().split(",")

        strvalue = "%.2lf" % random.uniform(1, 500)

        sum_value += float(strvalue)

        #<col:0>
        # finishtime

        #<col:1>
        custid = str(random.randint(1, 99999))

        #<col:2>
        gameid = random.choice(gamids)

        #<col:3>
        accnt = str(random.randint(100, 999))

        #<col:4>
        ip = urlcols[1]

        #<col:5>
        nip = random.randint(10000000, 10001000)

        #<col:6>
        fillpoint = strvalue

        #<col:7>
        objid=urlcols[3] + "/" + ''.join(random.sample(string.ascii_letters + string.digits, random.randint(4, 20)))

        #<col:8>
        orderid=util.name_by_split_minutes(finishtime, 1, None, str(random.randint(1, 1000000)))

        #<col:9>
        orderidpt=urlcols[0] + orderid

        #<col:10>
        zoneid=urlcols[0]

        # row=[cols:0, col:10]
        line = "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % (finishtime, custid, gameid, accnt, ip, nip, fillpoint, objid, orderid, orderidpt, zoneid)

        messages.append(line)
        pass

    return messages


@try_except_log
def produce_messages(kaf_producer, gamids, nmsgs, urls, topic, partitions, logtime = None, utf8_encode = False, verbose = False):
    messages = makeup_messages(nmsgs, gamids, logtime, urls)

    linenum = 0

    for line in messages:
        partition_id = int(linenum) % int(partitions)

        linenum += 1

        if utf8_encode:
            line = line.encode('utf-8')

        if verbose:
            print("{%s#%d:{%s}}" % (topic, partition_id, line))

        kaf_producer.send(topic, value=line, partition=partition_id)
        pass

    if nmsgs > 0:
        kaf_producer.flush()


########################################################################
# 主入口函数
@try_except_log
def main(parser, urls):
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

    # https://blog.csdn.net/qq_32599479/article/details/91042234
    #  random.seed(0)
    gamids = options.gameid.split(",")

    global sum_value

    for r in range(0, options.rounds):
        elog.info("(%d/%d) produce %d messages to kafka {%s}...", r, options.rounds, options.messages, kafka_topic)
        produce_messages(kaf_producer, gamids, options.messages, urls, kafka_topic, options.partitions, options.logtime, options.utf8_encode, options.verbose)

    elog.force("total %d messages(sum_value=%.4lf) produced to kafka {%s}.", options.rounds * options.messages, sum_value, kafka_topic)
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

    sitesfile = os.path.join(APPHOME, "config", "websites.csv")
    with open(sitesfile) as csvfile:
        urls = csvfile.readlines()

    # 主函数
    main(parser, urls)

    sys.exit(0)
