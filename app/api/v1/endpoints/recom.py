# -*- coding: utf-8 -*-
# @Time    : 2024/10/16 16:25
# @Author  : Galleons
# @File    : recom.py

"""
这里是文件说明
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.db.models import Double_choose


router = APIRouter()


