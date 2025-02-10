# -*- coding: utf-8 -*-
# @Time    : 2025/1/12 16:19
# @Author  : Galleons
# @File    : resume_request.py

"""
这里是文件说明
"""

from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field


# 性别枚举
class Gender(str, Enum):
    UNLIMITED = "不限"
    MALE = "男"
    FEMALE = "女"


# 学历层次枚举
class SchoolType(str, Enum):
    SPECIALIZED = "专科院校"
    UNDERGRADUATE = "本科院校"
    PROJECT_211 = "211院校"
    PROJECT_985 = "985院校"


# 活跃时长枚举
class ActiveDuration(str, Enum):
    UNLIMITED = "不限"
    TODAY = "当天活跃"
    THREE_DAYS = "3天内活跃"
    SEVEN_DAYS = "7天内活跃"


# 院校类型枚举
class CollegeType(str, Enum):
    COMPREHENSIVE = "综合"
    NORMAL = "师范"
    ENGINEERING = "理工"
    TECHNOLOGY = "工科"
    AGRICULTURE = "农林"
    FINANCE = "财经"
    LAW = "政法"
    MILITARY = "军事"
    MEDICAL = "医药"
    LANGUAGE = "语言"
    ART = "艺术"
    SPORTS = "体育"
    ETHNIC = "民族"
    TOURISM = "旅游"


# 查看范围枚举
class ViewScope(str, Enum):
    UNLIMITED = "不限"
    FILTERED_VIEWED = "过滤我已看过"
    FILTERED_INVITED = "过滤我已邀请"


# 学历要求枚举
class Education(str, Enum):
    HIGH_SCHOOL = "高中及以下"
    JUNIOR_COLLEGE = "大专"
    BACHELOR = "本科"
    MASTER = "硕士"
    PHD = "博士及以上"


# 毕业年限枚举
class GraduationTime(str, Enum):
    STUDENT = "在校学生"
    FRESH_GRADUATE = "应届毕业生"
    ONE_TO_THREE = "1-3年"
    THREE_TO_FIVE = "3-5年"
    FIVE_TO_TEN = "5-10年"
    ABOVE_TEN = "10年以上"


# 请求模型
class ResumeFilterRequest(BaseModel):
    publish_id: int | None = Field(default=None, description="岗位ID")
    gender: Gender = Field(default=Gender.UNLIMITED, description="性别筛选")
    school_types: List[SchoolType] = Field(default=[], description="学历层次")
    active_duration: ActiveDuration = Field(default=ActiveDuration.UNLIMITED, description="活跃时长")
    college_types: List[CollegeType] = Field(default=[], description="院校类型")
    view_scope: ViewScope = Field(default=ViewScope.UNLIMITED, description="查看范围")
    education: List[Education] = Field(default=[], description="学历要求")
    graduation_time: List[GraduationTime] = Field(default=[], description="毕业年限")

    class Config:
        json_schema_extra = {
            "publish_id": 123456,
            "gender": "男",
            "school_types": ["本科院校", "211院校"],
            "active_duration": "3天内活跃",
            "college_types": ["综合", "理工"],
            "view_scope": "过滤我已看过",
            "education": ["本科", "硕士"],
            "graduation_time": ["应届毕业生", "1-3年"]
        }

