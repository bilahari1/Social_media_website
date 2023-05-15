from selenium import webdriver
import time

print("Login test case started")
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(options=options)
driver.maximize_window()
driver.get("http://127.0.0.1:8000/n/login")
driver.find_element("id", "username").send_keys("bilahari")
time.sleep(2)
driver.find_element("id", "password").send_keys("Bilahari123#")
time.sleep(2)
driver.find_element("xpath", "/html/body/div[1]/div/form/center/input").click()
time.sleep(2)
curl = driver.current_url
url = 'http://127.0.0.1:8000/'
if curl == url:
    print("Login successfull")
else:
    print("Test failed")
driver.quit()
