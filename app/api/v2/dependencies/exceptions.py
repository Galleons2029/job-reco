# -*- coding: utf-8 -*-
# @Time    : 2025/1/6 17:55
# @Author  : Galleons
# @File    : exceptions.py

"""
异常处理模块
"""

# exceptions.py
from fastapi import HTTPException, status


class ResumeNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="简历查找不到。"
        )


class DuplicateResumeException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="该用户简历已存在！"
        )


class SchoolNotFoundException(HTTPException):
    """学校不存在异常"""
    def __init__(self):
        super().__init__(
            status_code=404,
            detail="School not found"
        )