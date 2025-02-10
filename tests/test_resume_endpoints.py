import pytest
from httpx import AsyncClient
from datetime import date, datetime
from app.api.v2.endpoints.resume_v1 import router as resume_v1_router


@pytest.mark.asyncio
async def test_create_resume():
    """测试创建简历的基本功能"""
    async with AsyncClient(app=resume_v1_router, base_url="http://test") as ac:
        resume_data = {
            "user_id": "test123",
            "is_school_user": True,
            "school_id": 1,
            "student_key": "2024001",
            "name": "张三",
            "gender": "男",
            "phone": "13800138000",
            "email": "test@example.com",
            "birthday": "1995-01-01",
            "highest_degree": "本科",
            "graduate_year": 2024,
            "work_years": 0,
            "education_experience": [{
                "education_id": 1,
                "school_name": "测试大学",
                "major": "计算机科学",
                "degree": "本科",
                "start_date": "2020-09-01",
                "end_date": "2024-06-30"
            }]
        }
        
        response = await ac.post("/resumes/create_resume", json=resume_data)
        assert response.status_code == 201, "简历创建应该返回201状态码"
        assert response.json()["id"] is not None, "返回的简历数据中应包含ID"

@pytest.mark.asyncio
async def test_update_resume():
    """测试更新简历的各种操作"""
    async with AsyncClient(app=resume_v1_router, base_url="http://test") as ac:
        update_data = {
            "user_id": 123123,
            # 测试追加教育经历
            "education_experience": {
                "operation": "append",
                "data": [{
                    "education_id": 2,
                    "school_name": "新大学",
                    "major": "人工智能",
                    "degree": "硕士",
                    "start_date": "2024-09-01",
                    "end_date": "2026-06-30"
                }]
            },
            # 测试替换证书信息
            "certificates": {
                "operation": "replace",
                "data": [{
                    "certificate_name": "新证书",
                    "certificate_date": "2024-01-01",
                    "certificate_desc": "描述"
                }]
            }
        }
        
        response = await ac.post("/resumes/update_resume", json=update_data)
        assert response.status_code == 200, "简历更新应该返回200状态码"
        
        # 验证更新结果
        result = response.json()
        assert len(result["education_experience"]) == 2, "教育经历应该增加一条"
        assert result["education_experience"][1]["school_name"] == "新大学", "新增的教育经历数据不正确"
        assert len(result["certificates"]) == 1, "证书信息应该被替换为一条"

@pytest.mark.asyncio
async def test_create_resume_duplicate():
    """测试创建重复简历的错误处理"""
    async with AsyncClient(app=resume_v1_router, base_url="http://test") as ac:
        resume_data = {
            "user_id": "test123",
            "student_key": "2024001",  # 使用已存在的student_key
            # ... 其他必要字段 ...
        }
        
        response = await ac.post("/resumes/create_resume", json=resume_data)
        assert response.status_code == 400, "重复创建简历应该返回400状态码"
        assert "已存在" in response.json()["detail"], "错误信息应该提示简历已存在"

@pytest.mark.asyncio
async def test_update_resume_not_found():
    """测试更新不存在简历的错误处理"""
    async with AsyncClient(app=resume_v1_router, base_url="http://test") as ac:
        update_data = {
            "user_id": "nonexistent",
            "name": "测试更新"
        }
        
        response = await ac.post("/resumes/update_resume", json=update_data)
        assert response.status_code == 404, "更新不存在的简历应该返回404状态码" 