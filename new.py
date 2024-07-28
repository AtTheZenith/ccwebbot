from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver, common
from threading import Thread
from math import floor
from time import time, sleep

# firefox is faster
options = webdriver.FirefoxOptions()
options.set_preference('dom.webdriver.enabled', False)
# options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--disable-extensions")
options.page_load_strategy = 'eager'
options.add_argument("--disable-cache")
options.add_argument("--disk-cache-size=1")
options.add_argument("--media-cache-size=1")
driver = webdriver.Firefox(options=options)


# edge is slower
# edge_driver_path = "C:/Windows/msedgedriver.exe"
# edge_options = Options()
# service = Service(executable_path=edge_driver_path)
# driver = webdriver.Edge(service=service, options=edge_options)

driver.get('https://orteil.dashnet.org/experiments/cookie/')
driver.implicitly_wait(1)

cookie = driver.find_element(By.ID, "cookie")
money = driver.find_element(By.ID, "money")

first_tick = time()
last_check = first_tick
ticking = first_tick
current_time = first_tick
returning = False
cash = 0

# ratio is 1.100001x math.ceil

registry = {
    'Cursor': {
        'Price': 15,
        'CPS': 0.2
    },
    'Grandma': {
        'Price': 100,
        'CPS': 0.8
    },
    'Factory': {
        'Price': 500,
        'CPS': 4
    },
    'Mine': {
        'Price': 2000,
        'CPS': 10
    },
    'Shipment': {
        'Price': 7000,
        'CPS': 20
    },
    'Alchemy lab': {
        'Price': 50000,
        'CPS': 100
    },
}

def get_money():
    """
    Gets the current money from the UI.

    Returns:
        int: The current money.
    """
    global cash
    cash = int(''.join(filter(None, str.split(money.text, ","))))
    return cash

def get_name_of_upgrade(element):
    """
    Gets the name of an upgrade from its UI element.

    Args:
        element: The upgrade element.

    Returns:
        str: The name of the upgrade.
    """
    return str.split(str.split(element.text, "\n")[0], " - ")[0]

def get_price_of_upgrade(element):
    """
    Gets the price of an upgrade from its UI element.

    Args:
        element: The upgrade element.

    Returns:
        int: The price of the upgrade.
    """
    return int(''.join(filter(None, str.split(str.split(str.split(element.text, "\n")[0], " - ")[1], ","))))

def refresh_registry():
    """
    Refreshes the registry with the latest prices and efficiencies.

    Returns:
        dict: The updated registry.
    """
    global registry
    
    for name, data in registry.items():
        try:
            registry[name]['Price'] = get_price_of_upgrade(driver.find_element(By.ID, f"buy{name}"))
            efficiency = data['CPS'] / registry[name]['Price'] if registry[name]['Price'] > 0 else 0
            registry[name]['Efficiency'] = efficiency
        except common.exceptions.StaleElementReferenceException:
            registry = refresh_registry()
    
    return registry

def get_most_efficient():
    """
    Finds the most efficient upgrade from the registry.

    Returns:
        tuple: A tuple containing the efficiency and name of the most efficient upgrade.
    """
    global registry
    most_efficient_name = None
    most_efficient_value = float('-inf')

    for name, data in registry.items():
        efficiency = data['Efficiency']
        if efficiency > most_efficient_value:
            most_efficient_value = efficiency
            most_efficient_name = name

    return most_efficient_value, most_efficient_name

def get_most_efficient_affordable():
    """
    Finds the most efficient affordable upgrade from the registry.

    Args:
        cash: The current amount of money.

    Returns:
        tuple: A tuple containing the efficiency and name of the most efficient affordable upgrade.
    """
    global registry
    global cash
    
    most_efficient_name = None
    most_efficient_value = float('-inf')

    for name, data in registry.items():
        if data['Price'] <= cash:
            efficiency = data['Efficiency']
            if efficiency > most_efficient_value:
                most_efficient_value = efficiency
                most_efficient_name = name

    return most_efficient_value, most_efficient_name

def get_cheapest_upgrade():
    """
    Finds the cheapest upgrade from the registry.

    Returns:
        tuple: A tuple containing the price and name of the cheapest upgrade.
    """
    global registry
    
    cheapest_name = None
    cheapest_value = float('inf')

    for name, data in registry.items():
        price = data['Price']
        if price < cheapest_value:
            cheapest_value = price
            cheapest_name = name

    return cheapest_value, cheapest_name

registry = refresh_registry()

is_clicking = True

def clicker():
    global is_clicking
    while is_clicking:
        driver.execute_script("onmouseup=ClickCookie();", cookie)

clicker_threads = []
for _ in range(6):
    clicker_thread = Thread(target=clicker)
    clicker_thread.daemon = True
    clicker_thread.start()
    clicker_threads.append(clicker_thread)

def display_time():
    global ticking, first_tick
    while is_clicking:
        current_time = time()
        if current_time - 1 >= ticking:
            print(f"{floor(current_time - first_tick)} seconds.")
            ticking = current_time
        sleep(0.1)

timer_thread = Thread(target=display_time)
timer_thread.daemon = True
timer_thread.start()

while current_time - first_tick < 300:    
    current_time = time()

    if current_time - last_check > 0.5:
        last_check = current_time
        refresh_registry()
        cash = get_money()
        
        most_efficient_value, most_efficient_name = get_most_efficient()
        most_efficient_upgrade = driver.find_element(By.ID, f"buy{most_efficient_name}")

        print(f"{most_efficient_name} efficiency: {most_efficient_value}e")
        if most_efficient_upgrade:
            if cash >= get_price_of_upgrade(most_efficient_upgrade):
                try:
                    driver.execute_script(f"onclick=Buy('{most_efficient_name}');")
                    cash = get_money()
                except (common.exceptions.StaleElementReferenceException, common.exceptions.NoSuchElementException):
                    refresh_registry()
                    pass

is_clicking = False

while cash > get_cheapest_upgrade()[0]:
    refresh_registry()
    cash = get_money()
    most_efficient_value, most_efficient_name = get_most_efficient_affordable()
    
    if most_efficient_name:
        most_efficient_upgrade = driver.find_element(By.ID, f"buy{most_efficient_name}")
        if most_efficient_upgrade:
            try:
                driver.execute_script(f"onclick=Buy('{most_efficient_name}');")
            except (common.exceptions.StaleElementReferenceException, common.exceptions.NoSuchElementException):
                refresh_registry()
                pass
    else:
        break      

cps = driver.find_element(By.ID, "cps")
newcps = str.split(cps.text, " : ")[1]

print(f"Final clicks per second: {newcps}")
        
quit()