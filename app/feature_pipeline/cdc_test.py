from pymongo import MongoClient
from app.config import settings


def insert_data_to_mongodb(uri, database_name, collection_name, data):
    """
    将数据导入Mongodb集合中.

    :param uri: MongoDB URI
    :param database_name: 数据库名
    :param collection_name: 集合名
    :param data: 需要插入的数据 (dict)
    """
    client = MongoClient(uri)
    db = client[database_name]
    collection = db[collection_name]

    try:
        result = collection.insert_one(data)
        print(f"Data inserted with _id: {result.inserted_id}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client.close()

import uuid
new_uuid = uuid.uuid4()
print(f"new_uuid: {new_uuid}")
print(type(str(new_uuid)))

if __name__ == "__main__":
    # insert_data_to_mongodb(
    #     settings.MONGO_DATABASE_HOST,
    #     "scrabble",
    #     "posts",
    #     {
    #         '_id': str(new_uuid),
    #         "platform": "Zhihu",
    #         "content": {
    #             "title": "Kyutai开源Moshi",
    #             "content":
    #                 """
    #                 Kyutai 开源 Moshi，一个可以进行实时语音对话的文本语音模型。#ai#
    #                 期待类似的开源中文实时语音模型。
    #                 而且发了技术报告，里面有一些实现细节。
    #                 Moshi 采用多流架构，能够同时处理用户和系统的语音输入，并生成相应的语音输出。
    #                 Moshi 的理论延迟为160ms，实际为200ms，远低于自然对话中的几秒钟延迟。
    #                 Moshi 能够同时处理语音和文本信息，支持复杂的对话动态，包括同时说话和打断。
    #                 Moshi 支持实时流式推理，能够在生成语音的同时进行语音识别和文本到语音的转换。
    #
    #                 你是否曾经想象过，有一个社交平台，上面只有你自己一个人？现在有个应用真的做到了！
    #                 最近有一款新推出的iOS应用叫SocialAI，它是一个纯粹由AI驱动的社交网络。
    #                 SocialAI的界面与Twitter很像，但最大的区别在于：这里没有其他真人用户，只有你和无数AI机器人。
    #                 在这里，你发布的每条动态都会受到热情的回应，你也永远不用担心被其他人打扰心情。
    #                 使用SocialAI时，你还可以选择你想要的"粉丝"类型，比如"喷子"、"段子手"、"知识分子"等。你至少需要选择三种类型，但没有上限。如果你想要体验更多有趣的互动，可以选择所有32种类型！
    #                 虽然AI生成的回复有时会有点机械化，但有时也会遇到一些非常有趣的回答。
    #                 SocialAI的开发者Michael Sayman今年28岁，曾在Facebook工作过。他形容这款应用给人一种"解放"的感觉。在发布后短短几天内，SocialAI就获得了很多关注，Sayman感到非常惊讶、也非常开心。
    #                 Sayman说，开发这个App的灵感主要来自自己的经历，当他感到非常孤独、没有人可以求助时，他非常希望有一个倾听者。“我知道这个App不能解决所有人的问题，但我相信，有一些性格和我相似的人会用它来反思和成长。”
    #                 目前，SocialAI 是免费下载的，也没有内购。Sayman 表示，在找到产品市场契合度之前，他不打算额外筹集资金。
    #                 """,
    #         }
    #      }
    # )

    insert_data_to_mongodb(
        settings.MONGO_DATABASE_HOST,
        "scrabble",
        "documents",
        {
            '_id': str(new_uuid),
            "knowledge_id": "1111",
            "doc_id": "123",
            "path": "/ice/zsk",
            "content": {
                "title": "doc_name",
                "content":
                    """
                    Kyutai 开源 Moshi，一个可以进行实时语音对话的文本语音模型。#ai#
                    期待类似的开源中文实时语音模型。
                    而且发了技术报告，里面有一些实现细节。
                    Moshi 采用多流架构，能够同时处理用户和系统的语音输入，并生成相应的语音输出。
                    Moshi 的理论延迟为160ms，实际为200ms，远低于自然对话中的几秒钟延迟。
                    Moshi 能够同时处理语音和文本信息，支持复杂的对话动态，包括同时说话和打断。
                    Moshi 支持实时流式推理，能够在生成语音的同时进行语音识别和文本到语音的转换。

                    你是否曾经想象过，有一个社交平台，上面只有你自己一个人？现在有个应用真的做到了！
                    最近有一款新推出的iOS应用叫SocialAI，它是一个纯粹由AI驱动的社交网络。
                    SocialAI的界面与Twitter很像，但最大的区别在于：这里没有其他真人用户，只有你和无数AI机器人。
                    在这里，你发布的每条动态都会受到热情的回应，你也永远不用担心被其他人打扰心情。
                    使用SocialAI时，你还可以选择你想要的"粉丝"类型，比如"喷子"、"段子手"、"知识分子"等。你至少需要选择三种类型，但没有上限。如果你想要体验更多有趣的互动，可以选择所有32种类型！
                    虽然AI生成的回复有时会有点机械化，但有时也会遇到一些非常有趣的回答。
                    SocialAI的开发者Michael Sayman今年28岁，曾在Facebook工作过。他形容这款应用给人一种"解放"的感觉。在发布后短短几天内，SocialAI就获得了很多关注，Sayman感到非常惊讶、也非常开心。
                    Sayman说，开发这个App的灵感主要来自自己的经历，当他感到非常孤独、没有人可以求助时，他非常希望有一个倾听者。“我知道这个App不能解决所有人的问题，但我相信，有一些性格和我相似的人会用它来反思和成长。”
                    目前，SocialAI 是免费下载的，也没有内购。Sayman 表示，在找到产品市场契合度之前，他不打算额外筹集资金。
                    """,

            }
        }
    )
