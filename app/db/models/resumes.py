# -*- coding: utf-8 -*-
# @Time    : 2024/11/1 16:43
# @Author  : Galleons
# @File    : resumes.py

"""
简历数据模型
"""
from babel.localedata import Alias
from pydantic import ConfigDict, BaseModel, Field, EmailStr, AliasChoices
from typing import List, Optional, Annotated, Any, Dict, Union, TypeVar, Generic
from datetime import date, datetime, time
from pydantic import BaseModel, EmailStr, Field, ValidationInfo
from enum import Enum
from pydantic import StringConstraints, field_validator
from pydantic import BeforeValidator
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClient


PyObjectId = Annotated[str, BeforeValidator(str)]



# 定义性别枚举
class Gender(str, Enum):
    UNLIMITED = "" # 不限
    MALE = "男"
    FEMALE = "女"


class WorkType(str, Enum):
    FULL_TIME = "全职"
    PART_TIME = "兼职"
    INTERNSHIP = "实习"
    FULL_OR_PART = "全/兼职"


class DutyTime(str, Enum):
    IMMEDIATELY = "随时"
    WITHIN_WEEK = "1周内"
    WITHIN_MONTH = "1个月内"
    WITHIN_THREE_MONTHS = "3个月内"
    TO_BE_DETERMINED = "待定"


class Certificate(BaseModel):
    """证书信息"""
    certificate_id: int
    certificate_name: str = Field(..., description="证书名称")
    certificate_date: Optional[datetime] = Field(None, description="获得日期")
    certificate_desc: Optional[str] = Field("", description="证书描述")


class WorkExperience(BaseModel):
    """工作经历"""
    experience_id: int = Field(..., description="对应ID")
    work_type: WorkType = Field(None, description="岗位类型")
    company_name: str = Field(..., description="公司名称")
    position: str = Field(..., description="职位名称")
    start_date: datetime = Field(..., description="开始日期")
    end_date: datetime | str = Field(None, description="结束日期")
    department: Optional[str] = Field("", description="部门")
    company_industry: Optional[str] = Field("", description="公司行业")
    company_nature: Optional[str] = Field("", description="公司性质")
    company_scale: Optional[str] = Field("", description="公司规模")
    experience_description: str = Field(..., description="工作描述")


class Education(BaseModel):
    """教育经历"""
    education_id: int = Field(..., description="自增主键，每段经历标识")
    school_name: str = Field(..., description="学校名称")
    major: str = Field(..., description="专业")
    degree: str = Field(..., description="学历")
    start_date: datetime = Field(..., description="开始日期")
    end_date: datetime | str = Field(..., description="结束日期")
    major_description: Optional[str] = Field("", description="专业描述")
    gpa: Optional[str] = Field("", description="绩点")


class ProjectExperience(BaseModel):
    """项目经验"""
    project_id: int = Field(..., description="项目ID")
    project_name: str = Field(..., description="项目名称")
    company_name: Optional[str] = Field(None, description="所属公司")
    start_date: datetime = Field(..., description="开始日期")
    end_date: datetime | str = Field(..., description="结束日期")
    project_description: str = Field(..., description="项目描述")
    responsibility: str = Field(..., description="项目职责")


class LeadershipExperience(BaseModel):
    """领导经历"""
    leadership_id: int
    position: str = Field(..., description="职位")
    start_date: datetime = Field(..., description="开始日期")
    end_date: datetime | str = Field(..., description="结束日期")
    experience_description: str = Field(..., description="经历描述")


class JobIntention(BaseModel):
    """求职意向"""
    industry: str = Field(..., description="期望行业")
    company_property: Optional[str] = Field(None, description="期望公司性质")
    province: str = Field(..., description="期望省份")
    city: str = Field(..., description="期望城市")
    salary_min: int = Field(..., ge=0, description="期望最低薪资")
    salary_max: int = Field(..., ge=0, description="期望最高薪资")
    job_type: WorkType = Field(..., description="工作类型")
    category: str = Field(..., description="职位类别")
    second_category: Optional[str] = Field(None, description="职位二级类别")
    parent_category: Optional[str] = Field(None, description="职位父级类别")
    duty_time: Optional[DutyTime] = Field(None, description="到岗时间")





# 新建总表
class Resume(BaseModel):
    """完整的简历信息"""
    # 基本信息
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: int = Field(..., description="用户唯一标识")
    is_school_user: bool | None= Field(False, description="是否是高校群体")
    school_id: int | None = Field(..., description="学校ID")
    student_key: str | None = Field(..., description="学生唯一标识")
    name: str = Field(..., description="姓名")
    gender: Gender = Field(..., alias='sex', description="性别")
    id_number: str | None = Field(None, description="身份证号")
    nationality: Optional[str] = Field(None, description="民族")
    birth_place: str | None = Field(None, alias='birth', description="籍贯")
    phone: Annotated[str | None, StringConstraints(pattern=r'^\d{11}$')] = Field(..., alias='mobile',description="手机号")
    email: EmailStr | None = Field(None, alias='mail', description="电子邮箱")
    birthday: datetime = Field(None, description="出生日期")
    political_status: Optional[str] = Field(None, description="政治面貌")
    profession: str | None = Field(default=None, alias="professional", description="职业")

    # 教育和工作状态
    highest_degree: str = Field(..., alias='degree', description="最高学历")
    graduate_year: int = Field(..., ge=1900, le=2100, description="毕业年份")
    work_years: str = Field(0, description="工作年限")
    current_status: Optional[str] = Field(None, description="当前状态")

    # 技能和个人描述
    skill_description: str | None = Field(None, validation_alias=AliasChoices('profile', 'signs'),description="技能描述")
    self_introduction: str | None = Field(None, validation_alias=AliasChoices('introduction', 'self_desc'), description="自我介绍")

    # 详细信息
    education_experience: Optional[List[Education]] = Field(default_factory=list, description="教育经历")
    work_experience: Optional[List[WorkExperience]] = Field(default_factory=list, description="工作经历")
    project_experience: Optional[List[ProjectExperience]] = Field(default_factory=list, description="项目经历")
    leadership_experience: Optional[List[LeadershipExperience]] = Field(default_factory=list, description="领导经历")
    certificates: Optional[List[Certificate]] = Field(default_factory=list, description="证书")
    job_intention: Optional[JobIntention] = Field(None, description="求职意向")

    # 简历状态
    is_public: bool = Field(True, description="是否公开")
    is_disable: bool = Field(False, description="是否禁用账户")
    is_agree_privacy: bool = Field(True, description="是否同意隐私政策")
    language: str = Field("中文", description="简历语言")
    completion_percent: int = Field(0, ge=0, le=100, description="完成度")
    last_updated: datetime | None = Field(None, description="最后更新时间")
    last_login_time: datetime | None = Field(None, description="最后登录时间")
    last_apply_time: datetime | None = Field(None, description="最后投递时间")



    @classmethod
    def __get_validators__(cls):
        yield cls.validate_datetime

    @classmethod
    def validate_datetime(cls, v: Any) -> datetime:
        """自定义日期时间验证器"""
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            try:
                # 首先尝试解析完整的日期时间格式
                return datetime.fromisoformat(v)
            except ValueError:
                try:
                    # 如果失败，尝试解析日期格式并添加时间部分
                    return datetime.strptime(v, '%Y-%m-%d')
                except ValueError:
                    raise ValueError('非法日期格式。 请用：YYYY-MM-DD 作为输入')
        raise ValueError('非法日期格式。')

    model_config = ConfigDict(
        populate_by_name=True,  # 允许使用原始名称创建实例
        validate_assignment=True,
        str_strip_whitespace=True,
        extra='ignore',
        json_encoders={
            datetime: lambda dt: dt.strftime('%Y-%m-%d')
        },
        json_schema_extra={
            "example": {
                # 基本信息
                "user_id": 22222,
                "is_school_user": True,
                "school_id": 1001,
                "student_key": "BIT20240001",
                "name": "张明",
                "gender": "男",
                "id_number": "110101199001150123",
                "nationality": "汉族",
                "birth_place": "北京市",
                "phone": "13800138000",
                "email": "zhangming@example.com",
                "birthday": "1990-01-15",
                "political_status": "群众",
                "profession": "计算机",

                # 教育和工作状态
                "highest_degree": "硕士",
                "graduate_year": 2024,
                "work_years": '3',
                "current_status": "在读",

                # 技能和个人描述
                "skill_description": "精通Python/FastAPI后端开发，熟悉微服务架构设计，具备良好的系统设计能力",
                "self_introduction": "具有3年后端开发经验，参与过多个大型项目开发。擅长高并发系统设计和性能优化",

                # 教育经历
                "education_experience": [
                    {
                        "education_id": 1,
                        "school_name": "北京理工大学",
                        "major": "计算机科学与技术",
                        "degree": "硕士",
                        "start_date": "2021-09-01",
                        "end_date": "2024-06-30",
                        "major_description": "主修课程：高级算法、分布式系统、机器学习",
                        "gpa": "3.8/4.0",
                    }
                ],

                # 工作经历
                "work_experience": [
                    {
                        "experience_id": 1,
                        "company_name": "字节跳动",
                        "position": "后端开发工程师",
                        "start_date": "2022-03-01",
                        "end_date": "2023-06-30",
                        "department": "基础架构部",
                        "company_industry": "互联网",
                        "company_nature": "民营企业",
                        "company_scale": "10000人以上",
                        "experience_description": "负责核心服务架构设计和性能优化"
                    }
                ],

                # 项目经历
                "project_experience": [
                    {
                        "project_id": 1,
                        "project_name": "企业级微服务平台",
                        "company_name": "字节跳动",
                        "start_date": "2022-03-01",
                        "end_date": "2023-06-30",
                        "project_description": "设计并实现基于FastAPI和微服务架构的企业级应用平台",
                        "responsibility": "担任核心开发者，负责微服务架构设计"
                    }
                ],

                # 领导经历
                "leadership_experience": [
                    {
                        "leadership_id": 1,
                        "position": "技术组长",
                        "start_date": "2022-06-01",
                        "end_date": "2023-08-31",
                        "experience_description": "带领6人团队完成核心业务系统开发"
                    }
                ],

                # 证书
                "certificates": [
                    {
                        "certificate_id": 1,
                        "certificate_name": "AWS Certified Solutions Architect",
                        "certificate_date": "2023-05-15",
                        "certificate_desc": "国际认证的AWS解决方案架构师认证"
                    }
                ],

                # 求职意向
                "job_intention": {
                    "industry": "互联网",
                    "company_property": "外企",
                    "province": "北京市",
                    "city": "北京市",
                    "salary_min": 35000,
                    "salary_max": 50000,
                    "job_type": "全职",
                    "category": "后端开发",
                    "second_category": "Python开发工程师",
                    "parent_category": "技术研发"
                },

                # 简历状态
                "is_public": True,
                "language": "中文",
                "completion_percent": 90,
                "last_updated": "2024-01-10T14:30:00"
            }
        }
    )





class EducationUpdate(BaseModel):
    """用于更新教育经历的模型"""
    education_id: int = Field(..., description="自增主键，每段经历标识")
    school_name: Optional[str] = Field(None, description="学校名称")
    major: Optional[str] = Field(None, description="专业")
    degree: Optional[str] = Field(None, description="学历")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    major_description: Optional[str] = Field(None, description="专业描述")
    gpa: Optional[str] = Field(None, description="绩点")

    class Config:
        json_schema_extra = {
            "example": {
                "education_id": 1,
                "degree": "硕士"
            }
        }


class WorkExperienceUpdate(BaseModel):
    """用于更新工作经历的模型"""
    experience_id: int = Field(..., description="经历ID")
    company_name: Optional[str] = None
    position: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    department: Optional[str] = None
    company_industry: Optional[str] = None
    company_nature: Optional[str] = None
    company_scale: Optional[str] = None
    experience_description: Optional[str] = None


class ProjectExperienceUpdate(BaseModel):
    """用于更新项目经验的模型"""
    project_id: int = Field(..., description="项目ID")
    project_name: Optional[str] = None
    company_name: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    project_description: Optional[str] = None
    responsibility: Optional[str] = None


class LeadershipExperienceUpdate(BaseModel):
    """用于更新领导经历的模型"""
    leadership_id: int = Field(..., description="领导经历ID")
    position: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    experience_description: Optional[str] = None


class CertificateUpdate(BaseModel):
    """用于更新证书信息的模型"""
    certificate_id: int = Field(..., description="证书ID")
    certificate_name: Optional[str] = None
    certificate_date: Optional[datetime] = None
    certificate_desc: Optional[str] = None

class JobIntentionUpdate(BaseModel):
    """用于更新求职意向的模型"""
    industry: Optional[str] = None
    company_property: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    salary_min: Optional[int] = Field(None, ge=0)
    salary_max: Optional[int] = Field(None, ge=0)
    job_type: Optional[WorkType] = None
    category: Optional[str] = None
    second_category: Optional[str] = None
    parent_category: Optional[str] = None


class OperationType(str, Enum):
    APPEND = "append"  # 追加新数据
    UPDATE = "update"  # 更新特定项
    DELETE = "delete"  # 删除指定项



# 定义泛型类型变量
T = TypeVar('T')

class ListUpdateOperation(BaseModel, Generic[T]):
    """支持泛型的列表更新操作模型"""
    operation: OperationType
    data: Union[
        List[T],          # 用于追加操作
        Dict[int, T],     # 用于更新操作
        List[int]         # 用于删除操作
    ] = Field(
        ...,
        description="数据内容，根据operation类型接受不同格式：\n"
                   "- APPEND: List[T] 用于追加新数据\n"
                   "- UPDATE: Dict[int, T] 用于更新特定索引的数据\n"
                   "- DELETE: List[int] 用于删除指定ID的数据"
    )

    @field_validator('data')
    def validate_data_format(cls, v: Union[List[T], Dict[int, T], List[int]], info: ValidationInfo) -> Any:
        """验证data字段格式是否与operation匹配"""
        operation = info.data.get('operation')
        
        match operation:
            case OperationType.APPEND:
                if not isinstance(v, list) or isinstance(v[0], int):
                    raise ValueError("追加操作需要提供数据对象列表")
            case OperationType.UPDATE:
                if not isinstance(v, dict):
                    raise ValueError("更新操作需要提供 {id: data} 格式的字典")
            case OperationType.DELETE:
                if not isinstance(v, list) or not all(isinstance(x, int) for x in v):
                    raise ValueError("删除操作需要提供ID列表")
        
        return v



# 更新总表
class ResumeUpdate(BaseModel):
    """用于更新操作的简历模型"""
    user_id: int
    # 基本信息更新
    name: Optional[str] = None
    gender: Optional[Gender] = None
    phone: Optional[Annotated[str, StringConstraints(pattern=r'^\d{11}$')]] = None
    email: Optional[EmailStr] = None
    birthday: Optional[datetime] = None
    birth_place: Optional[str] = None
    highest_degree: Optional[str] = None
    graduate_year: Optional[int] = Field(None, ge=1900, le=2100)
    work_years: Optional[str] = Field(None)
    skill_description: Optional[str] = None
    self_introduction: Optional[str] = None
    profession: Optional[str] = Field(default=None, alias="professional", description="职业")
    duty_time: Optional[DutyTime] = Field(None, description="到岗时间")


    # 列表类型更新 - 使用泛型ListUpdateOperation
    education_experience: Optional[ListUpdateOperation[Education]] = None
    work_experience: Optional[ListUpdateOperation[WorkExperience]] = None
    project_experience: Optional[ListUpdateOperation[ProjectExperience]] = None
    leadership_experience: Optional[ListUpdateOperation[LeadershipExperience]] = None
    certificates: Optional[ListUpdateOperation[Certificate]] = None
    
    # 求职意向更新
    job_intention: Optional[JobIntentionUpdate] = None

    is_public: bool | None = Field(True, description="是否公开")
    is_disable: bool | None = Field(False, description="是否禁用账户")
    is_agree_privacy: bool | None = Field(True, description="是否同意隐私政策")
    language: str | None = Field("中文", description="简历语言")
    completion_percent: int | None = Field(0, ge=0, le=100, description="完成度")
    last_updated: datetime | None = Field(None, description="最后更新时间")
    last_login_time: datetime | None = Field(None, description="最后登录时间")
    last_apply_time: datetime | None = Field(None, description="最后投递时间")


    model_config = ConfigDict(
        populate_by_name=True,           # 允许使用原始名称创建实例
        validate_assignment=True,
        str_strip_whitespace=True,
        extra='ignore',
        json_schema_extra={
            "example": {
                "user_id": 123456,
                # 基本信息更新
                "name": "张明",
                "phone": "13800138000",
                "email": "zhangming@example.com",
                "skill_description": "精通Python/FastAPI后端开发，熟悉微服务架构",
                "self_introduction": "3年后端开发经验，专注于高并发系统设计",

                # 教育经历 - 追加操作
                "education_experience": {
                    "operation": "append",
                    "data": [{
                        "education_id": 2,
                        "school_name": "北京大学",
                        "major": "计算机科学与技术",
                        "degree": "硕士",
                        "start_date": "2021-09-01",
                        "end_date": "2024-06-30",
                        "major_description": "主修课程：分布式系统、高级算法设计",
                        "gpa": "3.8/4.0"
                    }]
                },

                #
                # # 项目经历 - 更新特定项操作
                # "project_experience": {
                #     "operation": "update",
                #     "data": {
                #         0: {  # 更新project_id为0的项目经历
                #             "project_name": "企业级微服务平台",
                #             "company_name": "字节跳动",
                #             "start_date": "2022-03-01",
                #             "end_date": "2023-12-31",
                #             "project_description": "设计并实现基于FastAPI的微服务架构平台",
                #             "responsibility": "负责整体架构设计和核心模块开发"
                #         }
                #     }
                # },
                #
                # # 证书 - 追加操作
                # "certificates": {
                #     "operation": "append",  # 在certificates字段下添加新的字典，其中键名为certificate_id
                #     "data": {
                #         "1234": {
                #             "certificate_name": "AWS Certified Solutions Architect",
                #             "certificate_date": "2023-12-15",
                #             "certificate_desc": "Amazon Web Services 解决方案架构师认证"
                #         }
                #     }
                # },
                #
                # # 领导经历 - 删除特定项操作
                # "leadership_experience": {
                #     "operation": "delete",
                #     "data": [123123, 3124] # 删除leadership_experience下id为123123和3124的整个字段
                # },

                # 求职意向更新
                "job_intention": {
                    "industry": "互联网",
                    "company_property": "外企",
                    "province": "北京市",
                    "city": "北京市",
                    "salary_min": 40000,
                    "salary_max": 60000,
                    "job_type": "全职",
                    "category": "后端开发",
                    "second_category": "Python开发工程师",
                    "parent_category": "技术研发"
                }
            }
        },
    )




class Batch_resumes_update(BaseModel):

    resumes: List[ResumeUpdate]



class ResumeResponse(BaseModel):
    """API响应使用的简历模型"""
    id: Optional[PyObjectId] =Field(default=None, alias="_id", description="简历ID")
    last_updated: datetime | None = Field(None, description="最后更新时间")

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True
        arbitrary_types_allowed = True


# 用于简历搜索的模型
class ResumeSearchParams(BaseModel):
    keyword: str = Field(..., min_length=1)
    skills: Optional[List[str]] = None
    min_experience: Optional[int] = Field(None, ge=0)
    max_salary: Optional[int] = Field(None, ge=0)



class ProfileUpdater:
    def __init__(self, mongo_client: AsyncIOMotorClient, database: str, collection: str):
        """初始化MongoDB连接"""
        self.client = mongo_client
        self.db = self.client[database]
        self.collection = self.db[collection]

    def _convert_date_to_datetime(self, value: Any) -> Any:
        """将 date 对象转换为 datetime 对象"""
        if isinstance(value, date) and not isinstance(value, datetime):
            return datetime.combine(value, time())
        elif isinstance(value, dict):
            return {k: self._convert_date_to_datetime(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._convert_date_to_datetime(item) for item in value]
        return value

    def _prepare_update_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理更新数据，确保所有日期类型都被正确转换"""
        return self._convert_date_to_datetime(data)

    def _handle_append_operation(self, field: str, data: Union[List, Dict]) -> Dict:
        """处理追加操作"""
        if isinstance(data, list):
            # 处理列表形式的追加
            return {f"{field}": {"$each": data}} if data else {}
        else:
            # 处理字典形式的追加
            return {f"{field}.{k}": v for k, v in data.items()}

    def _handle_update_operation(self, field: str, data: Dict) -> Dict:
        """处理更新操作"""
        updates = {}
        for key, value in data.items():
            if isinstance(key, (int, str)):
                updates[f"{field}.{key}"] = value
        return updates

    def _handle_delete_operation(self, field: str, data: Union[List, Dict]) -> Dict:
        """处理删除操作"""
        if isinstance(data, list):
            # 如果是列表，创建一个删除这些ID的条件
            return {f"{field}": {
                "$unset": {str(item_id): "" for item_id in data}
            }}
        return {}

    def update_profile(self, update_data: ResumeUpdate) -> Dict[str, Any]:
        """更新用户档案的主方法"""
        try:
            # 构建基本更新操作
            set_operations = {}
            push_operations = {}
            unset_operations = {}

            # 使用 model_dump() 获取字典形式的数据
            update_dict = update_data.model_dump(exclude_unset=True)
            
            # 处理基本字段
            base_fields = [
                'user_id', 'is_school_user', 'school_id', 'student_key', 'gender',
                'id_number', 'nationality', 'birth_place', 'birthday', 'political_status',
                'highest_degree', 'graduate_year', 'work_years', 'current_status',
                'name', 'phone', 'email', 'skill_description',
                'self_introduction', 'profession',
            ]

            for field in base_fields:
                if field in update_dict and update_dict[field] is not None:
                    set_operations[field] = update_dict[field]

            # 处理求职意向更新
            if update_data.job_intention:
                job_intention_dict = update_data.job_intention.model_dump(exclude_unset=True)
                if job_intention_dict:
                    set_operations['job_intention'] = job_intention_dict

            # 处理复杂字段操作
            complex_fields = [
                'education_experience',
                'project_experience',
                'certificates',
                'leadership_experience'
            ]

            for field in complex_fields:
                field_data = getattr(update_data, field, None)
                if not field_data:
                    continue

                match field_data.operation:
                    case OperationType.APPEND:
                        if isinstance(field_data.data, list):
                            # 将Pydantic模型转换为字典
                            serialized_data = [
                                item.model_dump() if hasattr(item, 'model_dump') else item
                                for item in field_data.data
                            ]
                            push_operations.update({
                                field: {"$each": serialized_data}
                            })
                        else:
                            # 如果是字典形式，也需要序列化每个值
                            serialized_dict = {
                                k: v.model_dump() if hasattr(v, 'model_dump') else v
                                for k, v in field_data.data.items()
                            }
                            set_operations.update(
                                self._handle_append_operation(field, serialized_dict)
                            )

                    case OperationType.UPDATE:
                        # 序列化更新数据
                        serialized_data = {
                            k: v.model_dump() if hasattr(v, 'model_dump') else v
                            for k, v in field_data.data.items()
                        }
                        set_operations.update(
                            self._handle_update_operation(field, serialized_data)
                        )

                    case OperationType.DELETE:
                        unset_operations.update(
                            self._handle_delete_operation(field, field_data.data)
                        )


            # 构建最终更新操作
            update_operations = {}
            if set_operations:
                update_operations['$set'] = set_operations
            if push_operations:
                update_operations['$push'] = push_operations
            if unset_operations:
                update_operations['$unset'] = unset_operations

            # 添加更新时间戳
            if '$set' not in update_operations:
                update_operations['$set'] = {}
            update_operations['$set']['last_updated'] = datetime.now()

            # 执行更新操作
            result = self.collection.update_one(
                {'user_id': update_data.user_id},
                update_operations,
                # return_document=True,
                upsert=False
            )

            if not result:
                raise ValueError(f"未找到用户ID为 {update_data.user_id} 的文档")

            return result


        except Exception as e:
            raise Exception(f"更新档案时出错：{str(e)}")

    def close(self):
        """关闭MongoDB连接"""
        self.client.close()


from typing import Any, Dict, Type, TypeVar, get_args, get_origin
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)


class ResumeFieldProcessor:
    """简历字段处理器"""

    @staticmethod
    def process_list_operation(field_value: ListUpdateOperation[Any]) -> Dict[str, Any]:
        """处理列表操作类型的字段"""
        match field_value.operation:
            case OperationType.APPEND:
                return {
                    "$push": {
                        "$each": [
                            item.model_dump() if isinstance(item, BaseModel) else item
                            for item in field_value.data
                        ]
                    }
                }
            case OperationType.UPDATE:
                return {
                    "$set": {
                        str(k): v.model_dump() if isinstance(v, BaseModel) else v
                        for k, v in field_value.data.items()
                    }
                }
            case OperationType.DELETE:
                return {
                    "$pull": {
                        "id": {"$in": field_value.data}
                    }
                }

        raise ValueError(f"Unsupported operation: {field_value.operation}")

    @staticmethod
    def process_nested_model(field_value: BaseModel) -> Dict[str, Any]:
        """处理嵌套的Pydantic模型"""
        return field_value.model_dump(exclude_unset=True)

    @classmethod
    def process_field(cls, field_name: str, field_value: Any, field_type: Type) -> Dict[str, Any]:
        """处理字段值，返回对应的MongoDB更新操作"""
        if field_value is None:
            return {}

        # 处理ListUpdateOperation类型
        if (origin := get_origin(field_type)) is not None and origin is ListUpdateOperation:
            return cls.process_list_operation(field_value)

        # 处理嵌套的Pydantic模型
        if isinstance(field_value, BaseModel):
            return {"$set": {field_name: cls.process_nested_model(field_value)}}

        # 处理基本类型
        return {"$set": {field_name: field_value}}


class ResumeUpdateHandler:
    """简历更新处理器"""

    def __init__(self):
        # self.resume_update = resume_update
        self.processor = ResumeFieldProcessor()

    def prepare_update_operations(self, resume_update: ResumeUpdate) -> Dict[str, Any]:
        """准备MongoDB更新操作"""
        operations: Dict[str, Dict[str, Any]] = {}

        # 获取模型的所有字段
        for field_name, field_info in resume_update.model_fields.items():
            field_value = getattr(resume_update, field_name)
            if field_value is None:
                continue

            # 获取字段的处理结果
            field_ops = self.processor.process_field(
                field_name,
                field_value,
                field_info.annotation
            )

            # 合并操作
            for op_type, op_data in field_ops.items():
                if op_type not in operations:
                    operations[op_type] = {}
                operations[op_type].update(op_data)

        # 添加更新时间
        if "$set" not in operations:
            operations["$set"] = {}
        operations["$set"]["last_updated"] = datetime.now()

        return operations






# 定义学历层次枚举
class SchoolType(str, Enum):
    SPECIALIZED = "专科院校"
    UNDERGRADUATE = "本科院校"
    PROJECT_211 = "211院校"
    PROJECT_985 = "985院校"

# 定义活跃时长枚举
class ActiveDuration(str, Enum):
    UNLIMITED = "不限"
    TODAY = "当天活跃"
    THREE_DAYS = "3天内活跃"
    SEVEN_DAYS = "7天内活跃"

# 定义院校类型枚举
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

# 定义查看范围枚举
class ViewScope(str, Enum):
    UNLIMITED = "不限"
    FILTERED_VIEWED = "过滤我已看过"
    FILTERED_INVITED = "过滤我已邀请"

# 定义学历要求枚举
class Education(str, Enum):
    HIGH_SCHOOL = "高中及以下"
    JUNIOR_COLLEGE = "大专"
    BACHELOR = "本科"
    MASTER = "硕士"
    PHD = "博士及以上"

# 定义毕业年限枚举
class GraduationTime(str, Enum):
    STUDENT = "在校学生"
    FRESH_GRADUATE = "应届毕业生"
    ONE_TO_THREE = "1-3年"
    THREE_TO_FIVE = "3-5年"
    FIVE_TO_TEN = "5-10年"
    ABOVE_TEN = "10年以上"

class resume_recom(BaseModel):
    publish_id: int
    profession: str | None = Field(default=None, alias="professional", description="职业")
    is_school_user: bool = False
    school_id: int = None
    
    # 添加分页参数
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=10, ge=1, le=100, description="每页数量")

    gender: Gender = Field(default=Gender.UNLIMITED, validation_alias="sex", description="性别筛选")
    school_types: List[SchoolType] = Field(default=[], description="学历层次")
    active_duration: ActiveDuration = Field(default=ActiveDuration.UNLIMITED, description="活跃时长")
    college_types: List[CollegeType] = Field(default=[], description="院校类型")
    view_scope: ViewScope = Field(default=ViewScope.UNLIMITED, description="查看范围")
    education: List[Education] = Field(default=[], description="学历要求")
    graduation_time: List[GraduationTime] = Field(default=[], description="毕业年限")

    model_config = ConfigDict(
        populate_by_name=True,  # 允许使用原始名称创建实例
        validate_assignment=True,
        str_strip_whitespace=True,
        extra='ignore',

        json_schema_extra = {
            "example": {
                "publish_id": 222,
                "page": 1,
                "page_size": 10,
                "gender": "男",
                "school_types": ["本科院校", "211院校"],
                "active_duration": "3天内活跃",
                "college_types": ["综合", "理工"],
                "view_scope": "过滤我已看过",
                "education": ["本科", "硕士"],
                "graduation_time": ["应届毕业生", "1-3年"]
            }
        }
    )