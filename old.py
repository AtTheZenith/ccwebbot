from selenium.webdriver.common.by import By
from selenium import webdriver, common
from threading import Thread
from math import floor
from time import time, sleep

options = webdriver.FirefoxOptions()
options.set_preference('dom.webdriver.enabled', False)
# options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Firefox(options=options)
driver.get('https://orteil.dashnet.org/experiments/cookie/')

cookie = driver.find_element(By.ID, "cookie")
money = driver.find_element(By.ID, "money")
items = driver.find_elements(By.CSS_SELECTOR, '[id*="buy"]')
items.remove(items[-1])

first_tick = time()
last_check = first_tick
ticking = first_tick
current_time = first_tick
returning = False

def get_money():
    return int(''.join(filter(None, str.split(money.text, ","))))

def get_name_of_upgrade(element):
    return str.split(str.split(element.text, "\n")[0], " - ")[0]

def get_price_of_upgrade(element):
    return int(''.join(filter(None, str.split(str.split(str.split(element.text, "\n")[0], " - ")[1], ","))))

def clicker():
    while True:
        driver.execute_script("onmouseup=ClickCookie();", cookie)

for _ in range(6):
    clicker_thread = Thread(target=clicker)
    clicker_thread.daemon = True
    clicker_thread.start()

def display_time():
    global ticking, first_tick
    while True:
        current_time = time()
        if current_time - 1 >= ticking:
            print(f"{floor(current_time - first_tick)} seconds.")
            ticking = current_time
        sleep(0.1)

timer_thread = Thread(target=display_time)
timer_thread.daemon = True
timer_thread.start()

while current_time - first_tick < 300:    
    cash = get_money()
    current_time = time()

    if current_time - last_check > 10:
        last_check = current_time
        items = driver.find_elements(By.CSS_SELECTOR, '[id*="buy"]')[:-1]
        for i in range(len(items) - 1, -1, -1):
            try:
                item = items[i]
                while cash >= get_price_of_upgrade(item):
                    try:
                        driver.execute_script(f"onclick=Buy('{get_name_of_upgrade(item)}');")
                        cash = get_money()
                    except common.exceptions.StaleElementReferenceException:
                        items = driver.find_elements(By.CSS_SELECTOR, '[id*="buy"]')[:-1]
                        if i >= len(items):
                            i = len(items) - 1
                        item = items[i]
                        continue
            except common.exceptions.StaleElementReferenceException:
                items = driver.find_elements(By.CSS_SELECTOR, '[id*="buy"]')[:-1]
                if i >= len(items):
                    i = len(items) - 1
                item = items[i]
            cash = get_money()
        
cps = driver.find_element(By.ID, "cps")
newcps = str.split(cps.text, " : ")[1]

print(f"Final clicks per second: {newcps}")
        
driver.quit()