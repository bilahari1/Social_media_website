from selenium import webdriver
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

driver.find_element("xpath", "/html/body/div[2]/div[1]/div/div[1]/div/ul/li[5]/a").click()
time.sleep(2)
driver.find_element("xpath", "/html/body/div[2]/div[2]/div/div/div/div/div/ul/li[1]/div[2]/a[1]/button").click()
time.sleep(2)
wait = WebDriverWait(driver, 2)
modal = wait.until(EC.presence_of_element_located(("xpath", "/html/body/div[2]/div[2]/div/div/div/div/div/ul/div[1]")))
if modal.is_displayed():
    print("Job viewed successfully")
else:
    print("Test failed")
driver.quit()
