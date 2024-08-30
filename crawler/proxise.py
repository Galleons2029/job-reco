import requests
import random

# 假设这是你的代理列表
proxies = [
    'http://192.168.1.1:8080',
    'http://192.168.1.2:8080',
    'http://192.168.1.3:8080',
]

def get_random_proxy():
    """随机从代理列表中获取一个代理"""
    return random.choice(proxies)

def fetch(url):
    """使用随机代理访问给定的URL"""
    proxy = get_random_proxy()
    try:
        response = requests.get(url, proxies={"http": proxy, "https": proxy})
        print(f"Using proxy {proxy}")
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error using proxy {proxy}: {e}")
        return None

# 使用示例
url = 'http://example.com'
result = fetch(url)
if result:
    print("Content fetched successfully")
else:
    print("Failed to fetch content")
