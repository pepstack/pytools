#!/usr/bin/python
#-*- coding: UTF-8 -*-
#
# @create: 2021-01-06 15:19:12
# @update: 2021-02-04 18:01:12
#######################################################################
import sys

# https://pypi.org/project/

pkgs = ["python-devel"
        ,"yaml-0.2.5"
        ,"PyYAML-5.3.1"
        ,"setuptools-40.0.0"
        ,"MarkupSafe-1.1.1"
        ,"Jinja2-2.11.2"
        ,"six-1.15.0"
        ,"scandir-1.10.0"
        ,"pathlib2-2.3.5"
        ,"pyparsing-2.4.7"
        ,"packaging-20.9"
    ]


try:
    import yaml
    import setuptools
    import jinja2
    from markupsafe import Markup,escape
    from pathlib2 import Path
    import six.moves.urllib as urllib
    import pyparsing
    import packaging

    print "SUCCESS:", ",".join(pkgs)
except Exception as ex:
    print "ERROR:", ex
