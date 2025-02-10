# -*- coding: utf-8 -*-
# @Time    : 2025/1/10 11:15
# @Author  : Galleons
# @File    : schools.py

"""
学校数据模型
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from motor.motor_asyncio import AsyncIOMotorClient

class SchoolBase(BaseModel):
    token: str = Field(default="", description="学校唯一标识符，16位字符串")
    school_name: str = Field(..., description="学校名称，最大长度25个字符")
    school_code: str = Field(default="", description="学校代码，最大长度10个字符，用于教育部统一编码")
    logo: str = Field(default="", description="学校LOGO图标的URL地址")
    address: str = Field(default="", description="学校详细地址，最大长度50个字符")
    is_211: bool = Field(default=False, description="是否为211工程高校")
    is_985: bool = Field(default=False, description="是否为985工程高校")
    is_11: bool = Field(default=False, description="是否为双一流高校")
    is_yun: bool = Field(default=False, description="是否支持云就业服务")
    is_online: bool = Field(default=False, description="学校是否已上线，False表示未上线，True表示已上线")
    state: str = Field(default="未审核", description="学校审核状态，可选值：未审核、已通过、未通过")
    is_disable: bool = Field(default=False, description="是否禁用该学校账号")
    school_level: str = Field(default="", description="学校层次，如本科、专科等")
    faculty_count: int = Field(default=0, description="学院数量")
    major_count: int = Field(default=0, description="专业数量")
    student_count: int = Field(default=0, description="在校生数量")
    area_name: str = Field(default="", description="所在区域名称")
    province_name: str = Field(default="", description="所在省份名称")
    city_name: str = Field(default="", description="所在城市名称")
    tel_area_code: str = Field(default="", description="电话区号，最大长度4位")
    is_commend: bool = Field(default=False, description="是否为运营推荐学校")
    introduce: int = Field(default=0, description="学校介绍的公告ID（外键）")
    guide: int = Field(default=0, description="办事指南的公告ID（外键）")
    contact_dept: str = Field(default="", description="对接部门名称，最大长度100字符")
    contact_address: str = Field(default="", description="部门联系地址，最大长度100字符")
    contact_tel: str = Field(default="", description="就业处联系电话，最大长度100字符")
    contact_mail: str = Field(default="", description="就业处联系邮箱，最大长度100字符")
    introduction: Optional[str] = Field(default=None, description="学校详细介绍，富文本格式")
    special_major: Optional[str] = Field(default=None, description="特色专业介绍")
    students_distribute_pic: str = Field(default="", description="生源分布图片的URL地址")
    sex_ratio: float = Field(default=0.0, description="女生比例，取值0-1之间，如0.6表示60%为女生")
    view_count: int = Field(default=0, description="学校主页被访问次数")
    school_type: str = Field(default="", description="学校类型")
    sch_type: int = Field(default=0, description="学校分类：0表示普通学校，1表示省中心，9表示云就业公众号")
    contact_dept_index: str = Field(default="", description="就业部门主页URL")
    recruit_index: str = Field(default="", description="招生首页URL")
    public_jy_url: str = Field(default="", description="学校对公就业网地址")
    redirect_jy_url: str = Field(default="", description="就业网转跳后的目标地址")
    proxy_jy_url: str = Field(default="", description="学校就业网反向代理URL")
    proxy_jy_directory: str = Field(default="", description="学校反向代理二级目录")
    is_center: bool = Field(default=False, description="是否为省级就业中心")
    union_from: int = Field(default=0, description="数据来源标识：0表示云就业数据，1表示51uns")
    function_show_type: int = Field(default=0, description="功能导航显示设置")
    is_account_expire: bool = Field(default=False, description="是否启用账号密码过期功能")
    account_expire_day: int = Field(default=0, description="密码过期天数")

    model_config = ConfigDict(json_schema_extra={"example": {"school_name": "示例大学","school_code": "10001","is_211": True,"is_985": False,"province_name": "北京","city_name": "北京","school_level": "本科"}})

class SchoolCreate(SchoolBase):
    school_id: int = Field(description="学校ID，系统自动生成的唯一标识")
    last_updated: datetime = Field(default_factory=lambda: datetime.now(), description="最后修改时间戳")
    create_by: int = Field(default=0, description="创建者用户ID")
    model_config = ConfigDict(json_schema_extra={"example": {"school_id":111,"school_name": "示例大学","school_code": "10001","is_211": True,"is_985": False,"province_name": "北京","city_name": "北京","school_level": "本科"}})


class SchoolUpdate(SchoolBase):
    school_id: int = Field(description="学校ID，系统自动生成的唯一标识")
    last_updated: datetime = Field(default_factory=lambda: datetime.now(), description="最近一次修改时间")


class SchoolInDB(SchoolBase):
    school_id: int = Field(description="学校ID，系统自动生成的唯一标识")
    last_updated: datetime = Field(default_factory=lambda: datetime.now(), description="最后修改时间戳")
    create_by: int = Field(default=0, description="创建者用户ID")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    # 示例1：综合性大学
                    "school_id": 1001,
                    "token": "PKU20240110ABCDEF",
                    "school_name": "北京大学",
                    "school_code": "10001",
                    "logo": "https://static.university.edu/logos/pku.png",
                    "address": "北京市海淀区颐和园路5号",
                    "is_211": True,
                    "is_985": True,
                    "is_11": True,
                    "is_yun": True,
                    "is_online": True,
                    "state": "已通过",
                    "school_level": "本科",
                    "faculty_count": 50,
                    "major_count": 200,
                    "student_count": 35000,
                    "area_name": "华北",
                    "province_name": "北京市",
                    "city_name": "北京市",
                    "tel_area_code": "010",
                    "contact_dept": "就业指导中心",
                    "contact_address": "北京市海淀区颐和园路5号就业指导中心",
                    "contact_tel": "010-12345678",
                    "contact_mail": "career@pku.edu.cn",
                    "introduction": "北京大学创建于1898年...",
                    "special_major": "数学、物理、计算机科学等",
                    "modify_time": 1704857140,
                    "create_by": 1
                },
                {
                    # 示例2：专科院校
                    "school_id": 2001,
                    "token": "BVTC20240110XYZW",
                    "school_name": "北京职业技术学院",
                    "school_code": "12345",
                    "logo": "https://static.university.edu/logos/bvtc.png",
                    "address": "北京市大兴区博兴七路",
                    "is_211": False,
                    "is_985": False,
                    "is_11": False,
                    "is_yun": True,
                    "is_online": True,
                    "state": "已通过",
                    "school_level": "专科",
                    "faculty_count": 15,
                    "major_count": 45,
                    "student_count": 12000,
                    "area_name": "华北",
                    "province_name": "北京市",
                    "city_name": "北京市",
                    "tel_area_code": "010",
                    "contact_dept": "就业服务处",
                    "contact_address": "北京市大兴区博兴七路就业服务处",
                    "contact_tel": "010-87654321",
                    "contact_mail": "jobs@bvtc.edu.cn",
                    "introduction": "北京职业技术学院是一所...",
                    "special_major": "机械制造、电子技术、计算机应用",
                    "modify_time": 1704857140,
                    "create_by": 1
                }
            ]
        }
    )

class BatchUpdateSchools(BaseModel):
    schools: List[SchoolUpdate] = Field(description="需要批量更新的学校列表")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    # 示例1：更新多所学校的基本信息
                    "schools": [
                        {
                            "school_id": 1001,
                            "school_name": "北京大学",
                            "contact_tel": "010-12345679",
                            "contact_mail": "career_new@pku.edu.cn",
                            "is_online": True,
                            "student_count": 36000
                        },
                        {
                            "school_id": 1002,
                            "school_name": "清华大学",
                            "contact_tel": "010-98765432",
                            "is_yun": True,
                            "faculty_count": 55,
                            "major_count": 210
                        }
                    ]
                },
                {
                    # 示例2：更新学校状态和联系信息
                    "schools": [
                        {
                            "school_id": 2001,
                            "state": "已通过",
                            "is_online": True,
                            "contact_dept": "就业指导中心",
                            "contact_tel": "010-11112222",
                            "contact_mail": "career@bvtc.edu.cn"
                        },
                        {
                            "school_id": 2002,
                            "state": "未通过",
                            "is_online": False,
                            "contact_dept": "学生就业处",
                            "contact_tel": "010-33334444"
                        }
                    ]
                }
            ]
        }
    )









class Database:
    client: AsyncIOMotorClient = None


async def get_database() -> Database:
    return Database()


async def get_school_collection():
    db = await get_database()
    return db.client.schools.school_info


async def create_school(school: SchoolCreate) -> SchoolInDB:
    collection = await get_school_collection()

    # Get the next school_id
    last_school = await collection.find_one(
        sort=[("school_id", -1)]
    )
    new_school_id = (last_school["school_id"] + 1) if last_school else 1

    school_dict = school.model_dump()
    school_dict["school_id"] = new_school_id
    school_dict["latest_time"] = int(datetime.now().timestamp())
    school_dict["create_time"] = int(datetime.now().timestamp())
    school_dict["modify_time"] = int(datetime.now().timestamp())

    await collection.insert_one(school_dict)
    return SchoolInDB(**school_dict)


async def get_school(school_id: int) -> Optional[SchoolInDB]:
    collection = await get_school_collection()
    school = await collection.find_one({"school_id": school_id})
    if school:
        return SchoolInDB(**school)
    return None


async def update_schools(schools: List[SchoolUpdate]) -> List[SchoolInDB]:
    collection = await get_school_collection()
    current_time = int(datetime.now().timestamp())

    updated_schools = []
    for school in schools:
        school_dict = school.model_dump()
        school_dict["modify_time"] = current_time
        school_dict["latest_time"] = current_time

        result = await collection.find_one_and_update(
            {"school_id": school.school_id},
            {"$set": school_dict},
            return_document=True
        )

        if result:
            updated_schools.append(SchoolInDB(**result))

    return updated_schools


async def delete_school(school_id: int) -> bool:
    collection = await get_school_collection()
    result = await collection.delete_one({"school_id": school_id})
    return result.deleted_count > 0


async def list_schools(
        skip: int = 0,
        limit: int = 10,
        filters: dict = None
) -> List[SchoolInDB]:
    collection = await get_school_collection()

    query = filters or {}
    cursor = collection.find(query).skip(skip).limit(limit)
    schools = await cursor.to_list(length=limit)

    return [SchoolInDB(**school) for school in schools]