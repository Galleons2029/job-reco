import requests

# OpenAI API standard endpoint
SERVER_URL = "http://192.168.100.111:8001/v1/chat/completions"

request_data = {
    "model": "qwen2-pro",
    #"stream": True,
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "你好啊！你是谁？"}
    ]
}

from openai import OpenAI

client = OpenAI(api_key="sk-gxijztovbtakciuwjwwqyaoxarjfvhuargxkoawhuzsanssm", base_url="https://api.siliconflow.cn/v1")

from langchain_openai import ChatOpenAI

if __name__ == "__main__":
    response = requests.post(SERVER_URL, json=request_data)
    print(response.json())

#if __name__ == "__main__":
#    response = requests.post(SERVER_URL, json=request_data, stream=True)
#    for chunk in response.iter_lines():
#        print(chunk.decode("utf-8"))
#     response = client.chat.completions.create(
#         model='alibaba/Qwen1.5-110B-Chat',
#         messages=[
#             {'role': 'user', 'content': "抛砖引玉是什么意思呀"}
#         ],
#         stream=False
#     )
#
#     #for chunk in response:
#     #    print(chunk.choices[0].delta.content, end='')
#     print(type(response))
#     print(response)
#     print(response.choices)
#     print(type(response.choices))
#     print(response.choices[0].message.content)
#
#     model = ChatOpenAI(
#         model='Qwen/Qwen2-72B-Instruct',
#         openai_api_key="sk-gxijztovbtakciuwjwwqyaoxarjfvhuargxkoawhuzsanssm",
#         openai_api_base="https://api.siliconflow.cn/v1",
#         temperature=0
#     )
#
#     ans2 = model.invoke("抛砖引玉是什么意思呀")
#     print(ans2.content)
#     print(type(ans2.content))