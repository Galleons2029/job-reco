# -*- coding: utf-8 -*-
# @Time    : 2024/11/2 19:31
# @Author  : Galleons
# @File    : data_clean.py

"""
这里是文件说明
"""
import json
import re

def clean_json(data):
    # 处理字符串中的特殊字符和多余的转义字符
    if isinstance(data, str):
        data = data.replace('\\"', '"')  # 去除多余的转义字符
        data = re.sub(r'\\n', ' ', data)  # 替换换行符
        data = re.sub(r'None', '', data)  # 将 "None" 替换为空字符串
        return data.strip()  # 去除首尾多余空格

    # 递归处理列表中的元素
    elif isinstance(data, list):
        return [clean_json(item) for item in data]

    # 递归处理字典中的值
    elif isinstance(data, dict):
        cleaned_data = {}
        for key, value in data.items():
            cleaned_value = clean_json(value)
            if cleaned_value != "":  # 排除空字符串和空字段
                cleaned_data[key] = cleaned_value
        return cleaned_data

    # 直接返回其他数据类型（整数、浮点数等）
    else:
        return data

# 示例：调用清理函数
json_data = '''{"student_key": "1cd86bcd5182f18396dc040038b66dba", "xm": "贾馥阳", "xb": "女", "sfzh": "1302231995********", "mz": "汉族", "syszd": "河北省滦州市", "mobilephone": "16631210353", "email": "1003012484@qq.com", "xl": "二学位毕业", "szyx": "国际经贸学院", "zydm": "120801", "zy": "电子商务", "xh": "4200949", "graduate_year": 2022, "knslb": "非困难生", "sfslb": "", "zzmm": "共青团员", "employ_intention": {"employ_intention_102232": {"industry": "批发和零售业", "company_property": "民营企业", "province": "江西省", "city": "南昌市", "salary_min": 4000, "salary_max": 8000, "job_type": "全职", "priority": "工作类型", "category": "市场推广", "second_category": "市场/营销", "parent_category": "广告/市场/媒体/艺术"}}, "resume": {"resume_1829367": {"resume_basic": {"data_year": 2021, "title": "土地资源管理电子商务贾馥阳女", "head_url": "https://yun-campus-res.oss-cn-shenzhen.aliyuncs.com/practice/1637205147-2563.png", "birthday": "1995-12-01", "start_work_year": 0, "expected_salary_min": 0, "expected_salary_max": 0, "work_type": "", "duty_time": "", "open_state": "公开", "language_type": "中文", "percent_complete": 77, "is_school_recommend": "是", "is_default": "否"}, "attribute": {"skill_desc": "CET-6、教师资格证、机动车驾驶证、普通话二级甲等；\\n熟练使用办公软件excel、ppt、ps，会使用专业软件GIS、CAD、ERP", "introduction": "善于沟通，有良好的沟通表达能力和人际交往能力\\n良好心态，善于解决问题，有责任感，勇于面对困难和挑战细心耐心，时间观念强，积极主动完成工作任务，性格开朗，兴趣广泛，喜欢弹吉他，健身，旅行，摄影", "birth_place": "河北省"}, "intention": {}, "work_experience": {"work_experience_1588478": {"work_type": "", "start_date": "2019-01-01", "end_date": "2019-05-01", "company_name": "北京地星伟业科技有限公司", "company_industry": "", "company_nature": "", "company_scale": "", "position": "三调技术员", "department": "", "experience_description": "1.使用GIS软件勾绘图斑，制图绘图等工作\\n2.外调，对接等工作"}, "work_experience_1588477": {"work_type": "", "start_date": "2019-07-01", "end_date": "2020-07-01", "company_name": "北京新兴华安智慧科技有限公司", "company_industry": "", "company_nature": "", "company_scale": "", "position": "规划师助理", "department": "", "experience_description": "1.参与多个项目工作调研，对接甲方，商务宣传，做会议记录整理、存储；\\n2.技术资料收集整理、分析处理、项目归档整理； \\n3.担任小组长--负责国土空间规划基数转换工作；\\n4.积累了一定的团队管理经验，执行能力较强，能协调统一多项任务。"}, "work_experience_1588476": {"work_type": "", "start_date": "2021-08-01", "end_date": "2021-10-01", "company_name": "中国建设银行", "company_industry": "", "company_nature": "", "company_scale": "", "position": "综合管理部总经理助理", "department": "", "experience_description": "1.主要负责中国建设银行赣江新区分行所有人事档案管理以及相关会议安排工作\\n工作内容：\\n2.按照新的人事档案装订管理规范进行审核，纠正，通知相关人员补充材料，重新装订等；  \\n实践收获：这份工作极大的锻炼了我的细心和耐心程度，考验严谨性以及沟通表达能力。"}}, "project_experience": {}, "education": {"education_1661488": {"start_date": "2020-09-01", "end_date": "2022-07-01", "school_name": "江西财经大学", "major": "电子商务", "major_description": "", "degree": "本科", "gpa": ""}, "education_1661489": {"start_date": "2015-09-01", "end_date": "2019-06-01", "school_name": "中国地质大学长城学院", "major": "土地资源管理", "major_description": "", "degree": "本科", "gpa": ""}}, "honor": {}, "leadership_position": {"leadership_position_282874": {"start_date": "2020-09-01", "end_date": "2022-06-01", "position": "班级勤工委员", "experience_description": "帮助同学完成资助服务工作，以及鼓励同学积极参与勤工助学活动"}, "leadership_position_282875": {"start_date": "2015-09-01", "end_date": "2018-09-01", "position": "院团委干事", "experience_description": "1.组织安排相关学生活动，如运动会，知识竞赛等 \\n2.拉外联，租借事务，开发票等 \\n主要收获：锻炼了统筹安排，协调能力，沟通表达能力"}}, "certificate": {"certificate_222512": {"certificate_date": "None", "certificate_name": "教师资格证", "certificate_desc": "", "certificate_img_url": "[\\"https://yun-campus-res.oss-cn-shenzhen.aliyuncs.com/practice/1637209804-8299.jpg\\"]"}, "certificate_222511": {"certificate_date": "None", "certificate_name": "机动车驾驶证", "certificate_desc": "", "certificate_img_url": "[\\"https://yun-campus-res.oss-cn-shenzhen.aliyuncs.com/practice/1637209778-7891.jpg\\",\\"https://yun-campus-res.oss-cn-shenzhen.aliyuncs.com/practice/1637209793-4529.jpg\\"]"}, "certificate_222510": {"certificate_date": "None", "certificate_name": "大学英语六级", "certificate_desc": "", "certificate_img_url": "[\\"https://yun-campus-res.oss-cn-shenzhen.aliyuncs.com/practice/1637209753-3735.png\\"]"}}}, "resume_1579134": {"resume_basic": {"data_year": 2021, "title": "我的简历20211014", "head_url": "https://yun-campus-res.oss-cn-shenzhen.aliyuncs.com/practice/1634182132-8620.png", "birthday": "1995-12-01", "start_work_year": 0, "expected_salary_min": 7, "expected_salary_max": 8, "work_type": "", "duty_time": "", "open_state": "公开", "language_type": "中文", "percent_complete": 92, "is_school_recommend": "是", "is_default": "是"}, "attribute": {"birth_place": "河北省", "introduction": "有良好的沟通能力、表达能力，性格开朗，工作中积极主动，有执行力，愿意为工作付出努力，喜欢沉浸式的工作状态，有自己的独立思考能力，注重团队合作，有良好的合作精神，注重集体利益高于个人利益。", "skill_desc": "有丰富的社会经验，善于分析总结，吸取经验，完善推进项目的开展；办公动手能力强，熟悉软件操作。"}, "intention": {"city": "北京", "work_type": "全职", "industry": "信息传输、软件和信息技术服务业", "job": "市场助理"}, "work_experience": {"work_experience_1588376": {"work_type": "", "start_date": "2019-07-01", "end_date": "2020-07-01", "company_name": "北京新兴华安智慧科技有限公司", "company_industry": "", "company_nature": "", "company_scale": "", "position": "规划师助理", "department": "", "experience_description": "商务宣传，业务对接，技术处理等工作。\\n1.参与多个项目工作调研，对接甲方，商务宣传，做会议记录整理、存储； 2.技术资料收集整理、分析处理、项目归档整理；\\n3.担任小组长--独立负责国土空间规划基数转换工作,有软件技术操作能力； \\n4.积累了一定的团队管理经验，执行能力较强，能协调统一多项任务。"}}, "project_experience": {"project_experience_142220": {"start_date": "2019-07-01", "end_date": "2020-07-01", "project_name": "多个地区国土空间规划", "company_name": "北京新兴华安智慧科技有限公司", "project_description": "根据甲方要求，在规定时间完成专题文本的撰写，期间还有调研走访收集资料任务。1.撰写规划文本\\n 2.使用ARCGIS制图出图 \\n3.调研走访，收集资料 \\n4.培训", "responsibility": "需要在规定期间完成文本的撰写，驻点期间，听从甲方领导的要求；学习新的技术规范，为员工培训，在项目中学习新的优质的项目经验，反馈给公司；协助总规划师完成各项工作，以及沟通对接甲方。"}}, "education": {"education_1661365": {"start_date": "2020-09-01", "end_date": "2022-06-01", "school_name": "江西财经大学", "major": "电子商务", "major_description": "", "degree": "本科", "gpa": ""}}, "honor": {}, "leadership_position": {"leadership_position_282791": {"start_date": "2016-09-01", "end_date": "2018-03-01", "position": "干事", "experience_description": "1.校院团委组织部——负责组织活动，申请款项，做活动预算策划；\\n2.团总支办公室——管理运动会幕后工作，举办各种活动；\\n3.诺风创意社团——制作创意视频，举办比赛。"}, "leadership_position_282790": {"start_date": "2020-09-01", "end_date": "2022-06-01", "position": "勤工委员", "experience_description": "主要是帮助勤工助学同学,传达资助及勤工助学消息，协助同学完成资助服务，以及组织同学开展校内外各种勤工助学活动。"}}, "certificate": {"certificate_222440": {"certificate_date": "None", "certificate_name": "大学英语四级", "certificate_desc": "", "certificate_img_url": "[\\"https://yun-campus-res.oss-cn-shenzhen.aliyuncs.com/practice/1634183700-3792.jpg\\"]"}, "certificate_222441": {"certificate_date": "None", "certificate_name": "大学英语六级", "certificate_desc": "", "certificate_img_url": "[\\"https://yun-campus-res.oss-cn-shenzhen.aliyuncs.com/practice/1634185136-9722.png\\"]"}, "certificate_222442": {"certificate_date": "None", "certificate_name": "教师资格证", "certificate_desc": "", "certificate_img_url": "[\\"https://yun-campus-res.oss-cn-shenzhen.aliyuncs.com/practice/1634185353-9956.jpg\\",\\"https://yun-campus-res.oss-cn-shenzhen.aliyuncs.com/practice/1634185388-6182.jpg\\"]"}, "certificate_222443": {"certificate_date": "None", "certificate_name": "机动车驾驶证", "certificate_desc": "", "certificate_img_url": "[\\"https://yun-campus-res.oss-cn-shenzhen.aliyuncs.com/practice/1634185476-2187.jpg\\",\\"https://yun-campus-res.oss-cn-shenzhen.aliyuncs.com/practice/1634185482-2651.jpg\\"]"}}}}}'''  # 请替换为完整 JSON 数据
data = json.loads(json_data)  # 加载 JSON 字符串为 Python 字典
cleaned_data = clean_json(data)

# 将清洗后的 JSON 数据重新转换为字符串
cleaned_json_data = json.dumps(cleaned_data, ensure_ascii=False, indent=4)
print(cleaned_json_data)
