# -*- coding: utf-8 -*-
# @Time    : 2024/11/18 15:43
# @Author  : Galleons
# @File    : career_talk_inject.py

"""
这里是文件说明
"""
import sys
import os

# 获取项目根目录路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(project_root)

# 现在可以导入app模块了
from app.db.qdrant import QdrantClientManager

import pandas as pd
from tqdm import tqdm
import time
import logging
from typing import List, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential
from qdrant_client import models

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 读取CSV文件
df = pd.read_csv("/home/weyon2/DATA/test_data/c_career_talk_job.csv")


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def batch_update_career_talk(
        collection_name: str,
        updates: List[Dict[str, Any]],
        timeout: int = 10
) -> None:
    """批量更新多个数据点的payload"""
    with QdrantClientManager.get_client_context() as qdrant_client:
        try:
            # 构建批量更新操作
            update_operations = []
            for update in updates:
                publish_id = update['publish_id']
                career_talk_id = update['career_talk_id']

                # 查询现有数据
                search_result = qdrant_client.scroll(
                    collection_name=collection_name,
                    scroll_filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="publish_id",
                                match=models.MatchValue(value=publish_id)
                            ),
                        ],
                    ),
                    with_payload=True,
                    limit=1
                )

                if not search_result[0]:
                    # logger.warning(f"未找到publish_id {publish_id}")
                    continue

                point_id = search_result[0][0].id  # 获取点的ID
                career_jobs_list = search_result[0][0].payload.get('career_talk', [])

                if career_talk_id not in career_jobs_list:
                    career_jobs_list.append(career_talk_id)

                    update_operations.append(
                        models.SetPayloadOperation(
                            set_payload=models.SetPayload(
                                payload={"career_talk": career_jobs_list},
                                points=[point_id]  # 直接使用点ID列表
                            )
                        )
                    )

            if update_operations:
                # 执行批量更新
                qdrant_client.batch_update_points(
                    collection_name=collection_name,
                    update_operations=update_operations,
                )
                logger.debug(f"成功批量更新 {len(update_operations)} 条记录")

        except Exception as e:
            logger.error(f"批量更新时出错: {str(e)}")
            raise


def process_dataframe_in_batches(
        df: pd.DataFrame,
        collection_name: str,
        batch_size: int = 50
) -> None:
    """批量处理DataFrame数据"""
    if not QdrantClientManager.check_health():
        raise ConnectionError("Qdrant服务不可用")

    failed_updates = []
    total_processed = 0

    try:
        for start_idx in tqdm(range(0, len(df), batch_size), desc="处理批次"):
            batch = df.iloc[start_idx:start_idx + batch_size]
            updates = [
                {
                    'publish_id': row['publish_id'],
                    'career_talk_id': row['career_talk_id']
                }
                for _, row in batch.iterrows()
            ]

            try:
                batch_update_career_talk(
                    collection_name=collection_name,
                    updates=updates
                )
                total_processed += len(updates)

                # 添加小延迟避免服务器过载
                time.sleep(0.1)

            except Exception as e:
                failed_updates.extend([
                    {**update, 'error': str(e)}
                    for update in updates
                ])
                logger.error(f"批次更新失败: {str(e)}")

            # 每批次结束后检查服务健康状态
            if not QdrantClientManager.check_health():
                logger.error("Qdrant服务不可用，暂停处理")
                time.sleep(30)  # 等待30秒后继续
                if not QdrantClientManager.check_health():
                    raise ConnectionError("Qdrant服务持续不可用")

            # 定期报告进度
            if total_processed % 1000 == 0:
                logger.info(f"已处理 {total_processed} 条记录，失败 {len(failed_updates)} 条")

    finally:
        # 报告处理结果
        logger.info(f"处理完成: 总计 {len(df)} 条，成功 {total_processed} 条，失败 {len(failed_updates)} 条")

        # 保存失败记录
        if failed_updates:
            failed_file = f'failed_updates_{time.strftime("%Y%m%d_%H%M%S")}.csv'
            pd.DataFrame(failed_updates).to_csv(failed_file, index=False)
            logger.info(f"失败记录已保存至: {failed_file}")


def main():
    """主函数"""
    try:
        logger.info(f"开始处理数据，总行数: {len(df)}")

        process_dataframe_in_batches(
            df=df,
            collection_name="job_test3",
            batch_size=50
        )

        logger.info("数据处理完成")

    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}")
        raise


if __name__ == "__main__":
    main()