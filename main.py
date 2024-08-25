import json
import time
import os  # 导入 os 模块以处理文件和目录操作

import dashscope
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
# from pyquery import PyQuery as pq
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
import requests

current_directory = os.path.dirname(os.path.abspath(__file__))

opt = Options()
opt.binary_location = rf'{current_directory}\Chrome\chrome.exe'
opt.add_argument('--no-sandbox')
opt.add_experimental_option('detach', True)
ser = Service()
ser.executable_path = rf'{current_directory}\Chrome\chromedriver.exe'

username = input('请输入超星账号:')
password = input('请输入超星密码:')
url = input('请输入进入考试页面后的网址:')
model = input("答案获取方式：1.本地ollama 2.通义千问（自行配置API）")

modelAi = ""
if model == "1":
    modelAi = "ollama"
elif model == "2":
    tongyiApi = input("请输入通义千问api token：")
    modelAi = "tongyi"
else:
    print("输入有误")
    exit(0)

browser = webdriver.Chrome(service=ser,options=opt)
browser.maximize_window()

browser.get(url)

phone_input = browser.find_element(By.ID, 'phone')
phone_input.send_keys(username)

password_input = browser.find_element(By.ID, 'pwd')
password_input.send_keys(password)

login_button = browser.find_element(By.ID, 'loginBtn')
login_button.click()

time.sleep(3)

if not os.path.exists('result'):
    os.makedirs('result')

def ollama(text):
    url = "http://localhost:11434/api/generate"
    data = {
        "model": "gemma2:27b",
        "prompt": f"这是题目：{text} 直接返回给我答案的对应选项 不要描述其他的",
        "stream": False
    }
    response = requests.post(url, json=data)
    res = response.text
    data = json.loads(res)
    ans = data.get("response")
    return ans

def tongyi(text):
    dashscope.api_key = tongyiApi
    text = f"这是题目：{text} 直接返回给我答案的对应字母 不要描述其他的"
    messages = [{'role': 'user', 'content': text}]
    response = dashscope.Generation.call(dashscope.Generation.Models.qwen_max, messages=messages,
                                         result_format='message')
    content = response['output']['choices'][0]['message']['content']

    return content

def extract_question_and_options():
        # que_ele = browser.find_element(By.XPATH,"//div[@style='overflow:hidden;']")
        num_ele = browser.find_element(By.XPATH,"//h3[@class='mark_name colorDeep']")

        if "单选" in num_ele.text:
            # type_ele = browser.find_element(By.XPATH,"//span[@class='colorShallow']")
            # type_text = type_ele.text.split("(")[1].split(",")[0]

            options = browser.find_elements(By.XPATH, "//div[@class='clearfix answerBg singleoption']")
            choose = ""
            for option in options:
                option_letter = option.find_element(By.XPATH, ".//span").text
                option_content = option.find_element(By.XPATH, ".//div").text
                choose += f"{option_letter}: {option_content} "

            que = f"{num_ele.text} {choose}"
            print(que)

            if (modelAi == "ollama"):
                ans = ollama(que)
            else:
                ans = tongyi(que)
            print("AI参考答案：" + ans)
            if 'A' in ans:
                A = browser.find_element(By.XPATH, "//span[text()='A']")
                A.click()

            if 'B' in ans:
                B = browser.find_element(By.XPATH, "//span[text()='B']")
                B.click()

            if 'C' in ans:
                C = browser.find_element(By.XPATH, "//span[text()='C']")
                C.click()

            if 'D' in ans:
                D = browser.find_element(By.XPATH, "//span[text()='D']")
                D.click()

            if 'A' not in ans and 'B' not in ans and 'C' not in ans and 'D' not in ans:
                print("答案获取失败")
                extract_question_and_options()

            time.sleep(1)
            status = click_next_button()
            if status == False:
                exit(0)
        elif "多选" in num_ele.text:
            options = browser.find_elements(By.XPATH, "//div[@class='clearfix answerBg']")
            choose = ""
            for option in options:
                option_letter = option.find_element(By.XPATH, ".//span").text
                option_content = option.find_element(By.XPATH, ".//div").text
                choose += f"{option_letter}: {option_content} "

            que = f"{num_ele.text} {choose}"
            print(que)

            if (modelAi == "ollama"):
                ans = ollama(que)
            else:
                ans = tongyi(que)

            print("AI参考答案：" + ans)
            if 'A' in ans:
                A = browser.find_element(By.XPATH, "//span[text()='A']")
                A.click()

            if 'B' in ans:
                B = browser.find_element(By.XPATH, "//span[text()='B']")
                B.click()

            if 'C' in ans:
                C = browser.find_element(By.XPATH, "//span[text()='C']")
                C.click()

            if 'D' in ans:
                D = browser.find_element(By.XPATH, "//span[text()='D']")
                D.click()

            if 'A' not in ans and 'B' not in ans and 'C' not in ans and 'D' not in ans:
                print("答案获取失败")
                extract_question_and_options()

            time.sleep(1)
            status = click_next_button()
            if status == False:
                exit(0)
        elif "判断" in num_ele.text:
            que = f"{num_ele.text}"
            print(que)

            if (modelAi == "ollama"):
                ans = ollama(que + "判断题返回对或错")
            else:
                ans = tongyi(que + "判断题返回对或错")

            print("AI参考答案：" + ans)

            if '对' in ans or 'A' in ans:
                A = browser.find_element(By.XPATH, "//span[text()='A']")
                A.click()

            if '错' in ans or 'B' in ans:
                B = browser.find_element(By.XPATH, "//span[text()='B']")
                B.click()

            if '对' not in ans and '错' not in ans and 'A' not in ans and 'B' not in ans :
                print("答案获取失败")
                extract_question_and_options()

            time.sleep(1)
            status = click_next_button()
            if status == False:
                exit(0)
        else:
            print("暂不支持填空")
            status = click_next_button()
            if status == False:
                exit(0)

def click_next_button():
    try:
        next_button = browser.find_element(By.XPATH, '//a[text()="下一题"]')
        next_button.click()
    except NoSuchElementException:
        print("没有找到“下一题”按钮，可能是已经到达最后一题。")
        print("题目填写已结束，请自行检查是否有遗漏，本程序不支持填空等题目，请手动填写")
        return False
    except Exception as e:
        print(f"点击下一题按钮失败: {e}")
        return False
    return True

def getque():
    while True:
        time.sleep(0.5)
        extract_question_and_options()

getque()

# browser.quit()