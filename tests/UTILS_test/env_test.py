# -*- coding: utf-8 -*-
# @Time    : 2025/1/6 22:11
# @Author  : Galleons
# @File    : env_test.py

"""
这里是文件说明
"""

from dotenv import load_dotenv
import os

load_dotenv('../../.env')

COMET_API_KEY: str = os.getenv('COMET_API_KEY')
print(COMET_API_KEY)