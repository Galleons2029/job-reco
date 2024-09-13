import requests

# OpenAI API standard endpoint
SERVER_URL = "http://192.168.100.111:8001/v1/chat/completions"

request_data = {
    "model": "qwen2-pro",
    #"stream": True,
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "你好啊！"}
    ]
}

if __name__ == "__main__":
    response = requests.post(SERVER_URL, json=request_data)
    print(response.json())

#if __name__ == "__main__":
#    response = requests.post(SERVER_URL, json=request_data, stream=True)
#    for chunk in response.iter_lines():
#        print(chunk.decode("utf-8"))