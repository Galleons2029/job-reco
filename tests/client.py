import requests

#response = requests.post("http://127.0.0.1:8000/predict", json={"input": 4.0})
#print(f"Status: {response.status_code}\nResponse:\n {response.text}")


from openai import OpenAI

# Set OpenAI's API key and API base to use vLLM's API server.
openai_api_key = "EMPTY"
openai_api_base = "http://192.168.100.111:8002/v1"

client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)


import base64
with open("/home/weyon2/下载/IMG_6539.JPG", "rb") as image_file:
    encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

chat_response = client.chat.completions.create(
    model="Qwen2-VL-7B-Instruct",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://modelscope.oss-cn-beijing.aliyuncs.com/resource/qwen.png"},
                    #"type": "image", "image": "file:///home/weyon2/%E4%B8%8B%E8%BD%BD/IMG_6539.JPG"
                },
                {"type": "text", "text": "1000字详细描述一下图片里写了什么?"},
            ],
        },
    ],
)
print("Chat response:", chat_response)