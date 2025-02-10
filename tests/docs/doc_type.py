# -*- coding: utf-8 -*-
# @Time    : 2024/10/25 23:19
# @Author  : Galleons
# @File    : doc_type.py

"""
这里是文件说明
"""
import os

def check_file_type(source_file_path):
    # 获取文件扩展名并转换为小写
    file_extension = os.path.splitext(source_file_path)[1].lower()

    # 根据文件扩展名判断文件类型
    if file_extension == ".pdf":
        return "PDF"
    elif file_extension in [".doc", ".docx"]:
        return "Word"
    else:
        return "Unknown"

print(check_file_type("/fe/feasf/waf.pdf"))