import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

ANTI_CAPTCHA_KEY = "b3c4983c8116cb89dc546f9d9f78b942"
URL = "https://vipdrive.net"
SITE_KEY = "0x4AAAAAAADnPIDROrmt1Wwj"

# Настройка браузера
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=Service(), options=options)

# Перехват данных с сайта
js_intercept = '''
window.captchaParams = null;
const i = setInterval(() => {
    if (window.turnstile) {
        clearInterval(i);
        window.turnstile.render = (a,b) => {
            window.captchaParams = {
                websiteKey: b.sitekey,
                data: b.cData,
                pagedata: b.chlPageData,
                action: b.action,
                userAgent: navigator.userAgent
            };
            window.tsCallback = b.callback;
            return 'foo';
        };
    }
},10);
'''

options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=Service(), options=options)
driver.get("about:blank")
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": js_intercept})
driver.get("https://vipdrive.net")

captcha_params = None
for _ in range(20):
    captcha_params = driver.execute_script("return window.captchaParams;")
    if captcha_params:
        break
    time.sleep(1)

if not captcha_params:
    print("❌ Не удалось получить параметры капчи.")
    driver.quit()
    exit()

print("✅ Параметры капчи:", captcha_params)

# Создание задачи на 2Captcha
task_payload = {
    "clientKey": ANTI_CAPTCHA_KEY,
    "task": {
        "type": "TurnstileTaskProxyless",
        "websiteURL": "https://vipdrive.net",
        "websiteKey": captcha_params["websiteKey"],
        "action": captcha_params["action"],
        "data": captcha_params["data"],
        "pagedata": captcha_params.get("pagedata")
    }
}

resp = requests.post("https://api.2captcha.com/createTask", json=task_payload).json()

if resp.get("errorId", 1) != 0:
    print("Ошибка создания задачи:", resp)
    driver.quit()
    exit()

task_id = resp["taskId"]
print("Создана задача с ID:", task_id)

# Ожидание решения задачи
solution = None
for _ in range(30):
    time.sleep(5)
    res = requests.post(
        "https://api.2captcha.com/getTaskResult",
        json={"clientKey": ANTI_CAPTCHA_KEY, "taskId": task_id}
    ).json()

    if res["status"] == "ready":
        solution = res["solution"]["token"]
        break
    else:
        print("Ожидание решения...")

if not solution:
    print("Капча не решена.")
    driver.quit()
    exit()

print("✅ Капча решена:", solution)

# Вставляем токен на сайт
driver.execute_script(f'window.tsCallback("{solution}");')

print("✅ Токен отправлен на сайт, браузер открыт.")

while True:
    time.sleep(60)