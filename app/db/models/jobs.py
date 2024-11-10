# -*- coding: utf-8 -*-
# @Time    : 2024/11/5 13:50
# @Author  : Galleons
# @File    : jobs.py

"""
这里是文件说明
"""

from pydantic import BaseModel, Field
from typing import List, Optional
import datetime


class CareerTalk(BaseModel):
    career_talk_id: int
    company_id: int

# 宣讲会职位
class Career_talk(BaseModel):
    school_id: str | int
    student_key: str
    career_talk: List[CareerTalk]

class Response_CareerTalk(BaseModel):
    career_talk_id: int
    job_id: List[int]





"""
双选会
"""

# 定义 JobFair 模型
class JobFair(BaseModel):
    fair_id: int                 # 双选会ID
    company_id: List[int]         # 公司ID列表

# 定义 Career 模型
class Career(BaseModel):
    career_talk_id: int           # 宣讲会ID

# 定义主模型
class JobRequestModel(BaseModel):
    # student_key: str | int | None = None
    # desire_industry: str          # 期望行业
    # attribute: str                # 单位性质
    # category: str                 # 岗位类型
    # second_category: str          # 职位分类
    # cities: str                   # 工作地点
    # desire_salary: str            # 期望薪水
    # major: str                    # 专业名称
    # fair_id: str                  # 双选会
    # fair_company_id: str
    # career: Optional[List[Career]] = []  # 宣讲会 (可选,默认为空列表)
    student_key: str | int = None
    desire_industry: str
    attribute: str
    category: str
    second_category: str
    cities: str
    desire_salary: str
    major: str
    fair_id: str | int
    fair_company_id: str

    # {
    #     "student_key": "2c88bb981ed75e870ce26cd4996765e2",
    #     "desire_industry": "电力、热力、燃气及水生产和供应业+信息传输、软件和信息技术服务业",
    #     "attribute": "高等教育单位+民营企业",
    #     "category": "全职+全职",
    #     "second_category": "销售总监+高级软件工程师",
    #     "cities": "天津市+长沙市",
    #     "desire_salary": "3k-3k+5k-9k",
    #     "major": "纺织工程",
    #     "fair_id": 9104,
    #     "fair_company_id": "486217,507755"
    # }

class Bilateral_record(BaseModel):
    apply_job_id: str | int = Field(..., alias='jobfair_apply_job_id')
    recruit_guid: str
    apply_id: int
    school_id: int
    fair_id: int
    company_id: int
    income_id: int
    publish_id: int
    is_registered: str | bool = Field(..., alias='is_regist')
    is_income: str | bool
    is_sign_up: int
    create_time: int
    create_by: int
    modify_timestamp: str | None = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class BilateralCollection(BaseModel):
    """
    一个容器，包含多个 `StudentModel` 实例。
    这是因为在 JSON 响应中提供最高级数组可能存在漏洞。
    """

    data: List[Bilateral_record]



class Bilateral_delete_record(BaseModel):
    fair_id: str | int = Field(..., alias='jobfair_apply_job_id')
    publish_id: List[int]

    class Config:
        populate_by_name = True


class BilateralDeleteCollection(BaseModel):
    """
    一个容器，包含多个 `StudentModel` 实例。
    这是因为在 JSON 响应中提供最高级数组可能存在漏洞。
    """

    data: List[Bilateral_delete_record]



class CareerTalkRecord(BaseModel):
    recruit_guid: str | None = None  # Nullable or Optional UUID if not provided
    career_talk_id: str | int
    school_id: str | int
    company_id: str | int
    income_id: str | int
    publish_id: str | int
    is_registered: str | bool = Field(..., alias='is_regist')
    is_income: str | int
    is_sign_up: str | int
    create_time: str | int
    create_by: str | int
    career_talk_job_id: str | int | None = None
    # m_company_id: str | int | None = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        # orm_mode = True




class CareerTalkCollection(BaseModel):
    """
    一个容器，包含多个 `CareerTalkRecord` 实例。
    这是因为在 JSON 响应中提供最高级数组可能存在漏洞。
    """

    data: List[CareerTalkRecord]



class CareerTalkDelete(BaseModel):
    career_talk_id: str | int = Field(..., alias='career_id')
    publish_id: List[int]

    class Config:
        populate_by_name = True


class CareerTalkDeleteCollection(BaseModel):
    """
    一个容器，包含多个 `StudentModel` 实例。
    这是因为在 JSON 响应中提供最高级数组可能存在漏洞。
    """

    data: List[CareerTalkDelete]
