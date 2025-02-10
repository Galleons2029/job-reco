from llama_index.llms.openai_like import OpenAILike

llm = OpenAILike(model="qwen2-pro", api_base="http://192.168.100.111:8001/v1/", api_key="dummy")

response = llm.complete("Hello World!")
print(str(response))

