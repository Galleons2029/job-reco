# -*- coding: utf-8 -*-
# @Time    : 2024/9/17 17:09
# @Author  : Galleons
# @File    : flow_test.py

"""
这里是文件说明
"""


import bytewax.operators as op
from bytewax.connectors.stdio import StdOutSink
from bytewax.dataflow import Dataflow
from bytewax.testing import TestingSource

flow = Dataflow("a_simple_example")

stream = op.input("input", flow, TestingSource(range(10)))


def times_two(inp: int) -> int:
    return inp * 2


double = op.map("double", stream, times_two)

op.output("out", double, StdOutSink())