from pymongo import MongoClient

from app.config import settings


client = MongoClient(settings.MONGO_DATABASE_HOST)
prompt_templates_db = client['prompt_templates']
prompt_templates_collection = prompt_templates_db['tests']

# 插入文档
document = {"name": "Alice", "age": 25, "city": "New York"}
prompt_templates_collection.insert_one(document)


user_db = client['users']
basic = user_db['basic']
basic.create_index("用户名", unique=True)
basic.create_index("邮箱", unique=True)

