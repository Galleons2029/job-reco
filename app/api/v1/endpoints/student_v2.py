from fastapi import FastAPI, HTTPException, APIRouter, Request
from pydantic import BaseModel, validator
from typing import Optional, Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import random
import datetime

import logging
# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# MongoDB setup
client = AsyncIOMotorClient("mongodb://root:weyon%40mongodb@192.168.15.79:27017,192.168.15.79:27018,192.168.15.79:27019/?replicaSet=app")
db = client["college"]

# FastAPI setup
router = APIRouter()


from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
from app.db.qdrant import QdrantClientManager
from app.config import settings

qdrant_connection = QdrantClient(url="192.168.100.146:6333")

from xinference.client import Client
client2 = Client("http://192.168.100.111:9997")
embed_model = client2.get_model("bge-small-zh-v1.5")
embed_model_pro = client2.get_model("bge-m3")
COLLECTION_NAME = settings.COLLECTION_TEST



# Pydantic models
class StudentCreateModel(BaseModel):
    student_key: str
    name: str
    sex: str
    ID_card: str
    nationality: str
    province_city: str
    phone_number: str
    email: str
    education: str
    institute: str
    major_number: str
    major: str
    student_number: str
    graduate_year: int
    poor_type: str
    normal_type: Optional[str] = ""
    politics_status: str
    employ_intention: Dict[str, Any]
    resume: Dict[str, Any]

class StudentUpdateModel(BaseModel):
    school_id: str
    student_key: str
    data: Dict[str, Any]

class StudentDeleteModel(BaseModel):
    school_id: str
    student_key: str
    data: Dict[str, Any]  # Path to the specific nested field to delete

class UpdateDataModel(BaseModel):
    school_id: str | int
    student_key: str
    data: Dict[str, Any]  # 动态字段的数据类型


class DeleteDataModel(BaseModel):
    school_id: str | int
    student_key: str
    fields: List[str]  # 动态字段的数据类型


def get_collection(collection_name: str):
    """
    动态获取指定的集合。
    """
    return db.get_collection(collection_name)



# Create a new student
@router.post("/creat_students/")
async def create_student(school_id: str, student: StudentCreateModel):
    collection = db[school_id]
    existing_student = await collection.find_one({"student_key": student.student_key})
    if existing_student:
        raise HTTPException(status_code=400, detail="Student already exists.")
    await collection.insert_one(student.dict())
    return {"message": "Student created successfully"}

# Read student data
@router.get("/students/{school_id}/{student_key}")
async def read_student(school_id: str, student_key: str, fields: Optional[str] = None):
    collection = db[school_id]
    student = await collection.find_one({"student_key": student_key}, {"_id": 0})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")
    if fields:
        field_list = fields.split(",")
        student = {key: student[key] for key in field_list if key in student}
    return student

# Update student data
@router.put("/students/")
async def update_student(student_update: StudentUpdateModel):
    collection = db[student_update.school_id]
    student = await collection.find_one({"student_key": student_update.student_key})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")
    update_data = {"$set": student_update.data}
    await collection.update_one({"student_key": student_update.student_key}, update_data)
    return {"message": "Student updated successfully"}



# 学生信息修改同步
@router.post("/update_student_record/")
async def update_student_record(update_data: UpdateDataModel):

    collection = db[str(update_data.school_id)]

    # 执行更新操作
    result = await collection.update_one(
        {"student_key": update_data.student_key},
        {"$set": update_data.data}         # 使用请求体中的 data 字段进行更新
    )
    if result.raw_result['updatedExisting'] == 0:
         raise HTTPException(status_code=404, detail="学生文档不存在")

    return {"message": "学生档案修改成功。"}



# Delete specific nested data
@router.delete("/students/")
async def delete_student_data(student_delete: StudentDeleteModel):
    collection = db[student_delete.school_id]
    student = await collection.find_one({"student_key": student_delete.student_key})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")
    # 将路径转换成 MongoDB 支持的嵌套字段格式
    keys = student_delete.data.split("/")
    current_data = student
    for key in keys[:-1]:
        if key in current_data:
            current_data = current_data[key]
        else:
            raise HTTPException(status_code=400, detail="Invalid data path.")
    # Remove the target key
    if keys[-1] in current_data:
        del current_data[keys[-1]]
        await collection.update_one({"student_key": student_delete.student_key}, {"$set": student})
        return {"message": "数据成功删除。"}
    else:
        raise HTTPException(status_code=400, detail="Invalid data path.")



@router.post("/delete_student_field/")
async def delete_student_field(delete_data: DeleteDataModel):
    collection = get_collection(str(delete_data.school_id))
    student_key = delete_data.student_key

    # 构建删除操作
    # 构建 $unset 更新字典
    try:
        unset_data = {field: "" for field in delete_data.fields}  # MongoDB 中 $unset 的值可以是任意值，这里用空字符串

        # 执行删除操作
        result = await collection.update_one(
            {"student_key": student_key},
            {"$unset": unset_data}  # 使用 $unset 删除字段
        )

        if result.modified_count == 0:  # 使用 modified_count 替代 raw_result
            raise HTTPException(status_code=404, detail="学生文档不存在")

        return {"message": "学生档案删除成功。"}

    except AttributeError:
        raise HTTPException(status_code=400, detail="Invalid data path: 删除档案已不存在")

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"删除操作失败: {str(e)}"
        )



class StudentJobModel(BaseModel):
    school_id: str | int
    student_key: str
    zh: bool
    jyyx: bool
    zy: bool
    zycp: bool


import random


@router.post("/job_recom/")
async def job_recom_student(request: StudentJobModel):
    collection = get_collection(str(request.school_id))
    student_key = request.student_key

    student = await collection.find_one({"student_key": student_key})

    with QdrantClientManager.get_client_context() as qdrant_client:
        try:
            job_filter = Filter(
                        must=[
                            FieldCondition(
                                key='is_publish',
                                match=MatchValue(value=1)
                            ),
                            FieldCondition(
                                key='job_status',
                                range=models.Range(
                                    gt=0,
                                ),
                            ),
                            FieldCondition(
                                key="end_time",
                                range=models.Range(
                                    gt=None,
                                    gte=datetime.datetime.now().timestamp(),
                                    lt=None,
                                    lte=None,
                                ),
                            )
                        ]
                    )
            if student is None:
                raise HTTPException(status_code=404, detail="学生档案不存在")

            if request.zh == 1:
                my_list = ["专业","安全工程", "电子信息", "计算机", "生物"]
                random_value = random.choice(my_list)
                value = "综合"

                _jobs = qdrant_connection.query_points(
                    collection_name=COLLECTION_NAME,
                    query=embed_model_pro.create_embedding(random_value)['data'][0]['embedding'],  # <--- Dense vector
                    # query_filter= job_filter
                    using='job_descript',
                ).points
                job_list = [publish_id.payload['publish_id'] for publish_id in _jobs]

                logger.info(f"推荐岗位：{job_list}")
                return job_list
            else:
                field_value = "无专业"

                _jobs = qdrant_connection.query_points(
                    collection_name=COLLECTION_NAME,
                    query=embed_model_pro.create_embedding(field_value)['data'][0]['embedding'],  # <--- Dense vector
                    # query_filter=job_filter
                    using='job_descript',
                ).points

                job_list =  [publish_id.payload['publish_id'] for publish_id in _jobs]
                logger.info(f"推荐岗位：{job_list}")
                return random.sample(job_list, len(job_list))
        except Exception as e:
            logger.error(f"推荐岗位时出错: {str(e)}")
            raise





class Dislike(BaseModel):
    school_id: str | int
    student_key: str
    publish_id: str
    reason: str


@router.post("/diss/")
async def delete_student_field(dislike: Dislike):
    collection = get_collection(str(dislike.school_id))
    student_key = dislike.student_key

    student = await collection.find_one({"student_key": student_key})

    if student is None:
        raise HTTPException(status_code=404, detail="用户不存在")

    return {"message": "成功获取用户偏好。"}



class Follow(BaseModel):
    school_id: str | int
    student_key: str
    publish_id: str
    action: str | int



@router.post("/follow/")
async def delete_student_field(request: Follow):
    collection = get_collection(str(request.school_id))

    student = await collection.find_one({"student_key": request.student_key})

    if student is None:
        raise HTTPException(status_code=404, detail="用户不存在")

    return {"message": "成功获取用户偏好。"}




