from typing import Optional, List
from pydantic import ConfigDict, BaseModel, Field, EmailStr
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated
from bson import ObjectId

# 表示数据库中的 ObjectId 字段。
# 它将在模型中表示为 `str`，以便可以序列化为 JSON。
PyObjectId = Annotated[str, BeforeValidator(str)]

class StudentModel(BaseModel):
    """
    单个学生记录的容器。
    """

    # 学生模型的主键，存储为实例上的 `str`。
    # 这将在发送到 MongoDB 时别名为 `_id`，
    # 但在 API 请求和响应中提供为 `id`。
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str = Field(...)
    email: EmailStr = Field(...)
    major: str = Field(...)
    gpa: float = Field(..., le=4.0)
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "name": "柳佳龙",
                "email": "jdoe@example.com",
                "major": "数据科学",
                "gpa": 3.0,
            }
        },
    )

class UpdateStudentModel(BaseModel):
    """
    要对数据库中的文档进行的可选更新集。
    """

    name: Optional[str] = None
    email: Optional[EmailStr] = None
    major: Optional[str] = None
    gpa: Optional[float] = None
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "name": "柳佳龙",
                "email": "jdoe@example.com",
                "major": "纳米光子学",
                "gpa": 3.0,
            }
        },
    )

class StudentCollection(BaseModel):
    """
    一个容器，包含多个 `StudentModel` 实例。
    这是因为在 JSON 响应中提供最高级数组可能存在漏洞。
    """

    students: List[StudentModel]





class JobInModel(BaseModel):
    """
    输入上下文以及需要解析的文本描述的容器。
    """

    #id: Optional[PyObjectId] = Field(alias="_id", default=None)
    #job_name: str = Field(...)
    company_name: str = Field(...)
    #position_name: str = Field(...)
    companyIntro: str = Field(...)
    positionIntro: str = Field(...)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "job_name": "PHP工程师",
                "company_name": "云烟科技有限公司",
                "position_name": "数据科学",
                "companyIntro": "wafjiawjfiojawiofjawjf",
                "positionIntro": "dhaiwdhiawhfiawhi"
            }
        },
    )


class JobOutModel(BaseModel):
    """
    单个职位描述的容器。
    """

    # 职位模型的主键，存储为实例上的 `str`。
    # 这将在发送到 MongoDB 时别名为 `_id`，
    # 但在 API 请求和响应中提供为 `id`。
    #id: Optional[PyObjectId] = Field(alias="_id", default=None)
    job_name: str = Field(...)
    parent_category: str = Field(...)
    second_category: str = Field(...)
    cities: str = Field(...)
    attribute: str = Field(...)
    education: str = Field(...)
    salary: str = Field(...)
    about_major: str = Field(...)
    number: int = Field(..., le=0)

    duty: str = Field(...)
    explain: str = Field(...)
    requirements: str = Field(...)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "job_name": "营养师",
                "parent_category": "生物/制药/医疗/护理",
                "second_category": "医院/医疗",
                "cities": "长沙市",
                "attribute": "校招",
                "education": "本科及以上",
                "salary": "长沙市",
                "about_major": "经济学",
                "number": 5,
            }
        },
    )


