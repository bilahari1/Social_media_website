import signin as signin
from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

print("Login test case started")
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(options=options)
driver.maximize_window()
driver.get("http://127.0.0.1:8000/n/login")
driver.find_element("id", "username").send_keys("bilahari")
time.sleep(3)
driver.find_element("id", "password").send_keys("Bilahari123#")
time.sleep(3)
driver.find_element("xpath", "/html/body/div[1]/div/form/center/input").click()
time.sleep(3)
print("User Logged In")
