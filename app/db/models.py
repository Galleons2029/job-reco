from typing import Optional, List
from datetime import datetime
from pydantic import ConfigDict, BaseModel, Field, EmailStr
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated
from bson import ObjectId
from uuid import uuid4


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
                "company_name": "长沙市云研网络科技有限公司",
                #"position_name": "PHP开发工程师",
                "companyIntro": """云研科技稳中前进，不断发展，顺应“互联网+”时代潮流，积极推进就业工作。为高校打造移动化、智能化、精准化的“互联网+就业”平台，以实际行动践行 “创新引领创业，创业带动就业”。
        公司致力于：
         · 用互联网思维优化就业方式
         · 用大数据平台指引就业服务
         · 用精准服务帮助天下毕业生走稳求职第一步
        云就业创新性：
         · 配置型SaaS模式高校就业云平台
         · 大型招聘会实时数据分析平台
         · 校园招聘单位诚信评估体系
         · 高校O2O线上招聘会
         · 高校云宣讲直播平'""",
                "positionIntro": """'PHP开发工程师 8000左右，长沙市 本科 2人 人工智能，计算机类，计算机科学与技术，软件工程，物联网工程，电子与计算机工程，数据科学与大数据技术
        公司福利：年底双薪 绩效奖金 岗前培训 节日礼物 扁平管理
        岗位职责
        1、独立或者分组进行针对项目需求的功能开发和优化；
        2、对现有产品进行二次开发；
        3、根据项目开发进度和任务分配，开发相应的模块；
        4、根据需要不断修改完善项目功能
        5、深入理解产品原型，保持与产品人员的随时沟通，不断改进产品功能流程或逻辑；
        6、解决项目开发过程中遇到的技术和业务问题。
        简历投递说明
        简历投递邮箱123123123123@qq.com，联系电话：13612345678
        岗位要求
        1、熟悉掌握php，有良好的编程规范，熟悉掌握Thinkphp、Larvel中的任意一种框架；
        2、熟悉MySQL，能独立设计良好的数据库结构，懂SQL优化；
        3、熟悉使用redis等nosql技术；
        4、熟悉linux开发环境，熟悉LNMP环境搭建及设置；
        5、计算机相关专业本科以上学历，两年以上后端研发工作经验优先；
        6、熟悉swoole协程方式开发，有hyperf框架开发经验优先；
        7、应届本科及以上毕业，有物联网开发经验或大数据分析经验优先；'。""",
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
    province: str = Field(...)
    cities: str = Field(...)
    attribute: str = Field(...)
    education: str = Field(...)
    salary: str = Field(...)
    about_major: str = Field(...)
    number: int = Field(..., gt=0)
    tempt: str = Field(...)

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

class Job2StudentModel(BaseModel):
    """
    单个职位描述的容器。
    """

    # 职位模型的主键，存储为实例上的 `str`。
    # 这将在发送到 MongoDB 时别名为 `_id`，
    # 但在 API 请求和响应中提供为 `id`。
    # id: Optional[PyObjectId] = Field(alias="_id", default=None)
    desire_industry: str = Field(...)
    attribute: str = Field(...)
    category: str = Field(...)
    second_category: str = Field(...)
    cities: str = Field(...)
    desire_salary: str = Field(...)
    reason: str | None = None
    # about_major: str = Field(...)
    # number: int = Field(..., gt=0)
    # tempt: str = Field(...)

    # duty: str = Field(...)
    # explain: str = Field(...)
    # requirements: str = Field(...)

    # model_config = ConfigDict(
    #     populate_by_name=True,
    #     arbitrary_types_allowed=True,
    #     json_schema_extra={
    #         "example": {
    #             "job_name": "营养师",
    #             "parent_category": "生物/制药/医疗/护理",
    #             "second_category": "医院/医疗",
    #             "cities": "长沙市",
    #             "attribute": "校招",
    #             "education": "本科及以上",
    #             "salary": "长沙市",
    #             "about_major": "经济学",
    #             "number": 5,
    #         }
    #     },
    # )

class Major2StudentModel(BaseModel):
    """
    单个职位描述的容器。
    """

    # 职位模型的主键，存储为实例上的 `str`。
    # 这将在发送到 MongoDB 时别名为 `_id`，
    # 但在 API 请求和响应中提供为 `id`。
    # id: Optional[PyObjectId] = Field(alias="_id", default=None)
    # desire_industry: str = Field(...)
    # attribute: str = Field(...)
    # category: str = Field(...)
    # second_category: str = Field(...)
    # cities: str = Field(...)
    # desire_salary: str = Field(...)
    major: str = Field(...)

    reason: str | None = None


class Jobs(BaseModel):
    """
    单个岗位对象
    """
    id : str = Field(default_factory=lambda: uuid4().hex,)
    publish_id : str = Field(frozen=True)       # 职位id(不可更改）
    company_id : str = Field(...)               # 企业id
    m_company_id : str = Field(...)             # 合并后的单位ID
    company_name : str = Field(default="未知")   # 企业名称
    job_id : str = Field(...)
    end_time : datetime = None                  # 职位过期时间
    is_practice : int = 0                       # 是否实习 0：校招 1：实习 2：社招
    is_zpj_job : str = Field(...)               # 招聘节职位
    apply_count : int = Field(ge=0)             # 收到多少份简历
    job_name : str = Field(...)                 # 职位名称
    edu_category : str | None = None            # 教育部职位分类
    category : str = Field(...)                 # 职位类别
    category_id : str = Field(...)              # 职位类别ID
    parent_category : str = Field(...)          # 父级职位类别
    parent_category_id : str = Field(...)       # 父级职位类别ID
    second_category : str = Field(...)          # 二级职位分类
    second_category_id : str = Field(...)       # 二级职位分类ID
    category_teacher_type : str | None = None   # 教师子类别
    job_number : int = Field(ge=0)              # 招聘人数
    job_status : int = Field(...)               # 1招聘中，0已结束，-1屏蔽
    job_require : str = Field(...)              # 职位要求
    job_descript : str = Field(...)             # 职位描述，前端还用来区分新旧职位
    salary : str | None = None                  # 年薪，为空直接是面议
    salary_min : int = Field(ge=0)              # 薪资范围 - 最少
    salary_max : int = Field(le=1000000)        # 薪资范围 - 最多
    contact_tel : str = Field(default="未提供")  # 联系电话手机或者座机
    city_name : str = Field(default="未知")      # 工作城市
    work_address : str = Field(default="未知")   # 工作地点
    keywords : str | None = None                # 关键字 空格分开
    welfare : str | None = None                 # 薪酬福利
    intro_apply : str | None = None             # 投递说明
    intro_screen : str | None = None            # 筛选简历说明
    intro_interview : str | None = None         # 面试说明
    intro_sign : str | None = None              # 签约说明
    source : str = Field(...)                   # 来源：hr、school
    province : str | None = None                # 省份 - 运营处理
    degree_require : str                        # 学历要求
    experience : str | None = None              # 经验要求：1:不限，2:1年以下，3:1-3年，4:3-5年，5:5-10年，6:10年以上
    job_desc : str | None = None                # 职位描述
    biz_salary : str | None = None              # 运营填写的年薪字段
    about_major : str                           # 相关专业
    view_count : int = Field(default=0, ge=0)   # 职位浏览数量
    job_other : str | None = None               # 职位其他描述
    source_school_id : str | None = None        # 来源学校ID
    source_school : str = Field(default="未知")  # 来源学校名称
    is_commend : bool = 0                       # 是否推荐
    commend_time : str | None = None
    is_publish : bool                           # 是否发布：0下架 1上架
    publish_hr_id : str | None = None           # HRID，如果是PC端，没有openid
    publish_hr_openid : str | None = None       # 发布人HR的openid
    publish_time : str | None = None            # 发布时间
    amount_welfare_min:int=Field(ge=0, default=0)# 特殊处理：福利金额最小值
    amount_welfare_max:int=Field(le=1000000, default=0)# 特殊处理：福利金额最大值
    time_type : str | None = None               # 特殊湖南化工职业技术学院增加工作时间类型
    is_top : bool = 0                           # 是否置顶 0.否 1.是（该字段貌似不生效了）
    job_type : bool                             # 职位类型： 0.普通职位 1.平台职位
    create_by : str | None = None
    create_time : datetime = None
    # modify_by
    # modify_time
    # modify_timestamp
    # 记录的修改时间，自动维护
    # is_default
    # 是否企业默认职位
    # company_id_bak
    # 历史公司ID
    # removed
    # 已删除标识：0
    # 否，1
    # 已删除


class Double_choose(BaseModel):
    """
    单个岗位对象
    """
    desire_industry : str = Field(default_factory=lambda: uuid4().hex,)
    attribute : str = Field(frozen=True)       # 职位id(不可更改）
    category : str = Field(...)               # 企业id


class QueryRequest(BaseModel):
    collection_name: str = 'jobs'
    content : str
    is_vector : bool = True
    top_k : int = 10
    filtered : dict = None



# 定义 JobFair 模型
class JobFair(BaseModel):
    fair_id: int                 # 双选会ID
    company_id: List[int]         # 公司ID列表

# 定义 Career 模型
class Career(BaseModel):
    career_talk_id: int           # 宣讲会ID

# 定义主模型
class JobRequestModel(BaseModel):
    desire_industry: str          # 期望行业
    attribute: str                # 单位性质
    category: str                 # 岗位类型
    second_category: str          # 职位分类
    cities: str                   # 工作地点
    desire_salary: str            # 期望薪水
    major: str                    # 专业名称
    jobfair: JobFair              # 双选会
    career: Optional[List[Career]] = []  # 宣讲会 (可选,默认为空列表)