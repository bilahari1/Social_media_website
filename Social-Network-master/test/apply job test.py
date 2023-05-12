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
print("User Logged In")

driver.find_element("xpath", "/html/body/div[2]/div[1]/div/div[1]/div/ul/li[5]/a").click()
time.sleep(2)
driver.find_element("xpath", "/html/body/div[2]/div[2]/div/div/div/div/div/ul/li[1]/div[2]/a[2]/button").click()
time.sleep(2)
driver.find_element("name", "phone").send_keys("9876787654")
time.sleep(2)
driver.find_element("name", "resume").send_keys("C:/Users/Bilahari Amsu/Downloads/S4A_01_A Bilahari(40).pdf")
time.sleep(2)
driver.find_element("name", "cover_letter").send_keys("Hello")
time.sleep(2)
driver.find_element("xpath", "/html/body/div[2]/div[2]/div/div/div/div/form/input[7]").click()
time.sleep(2)
url = "http://127.0.0.1:8000/n/userjobs"
curl = driver.current_url
if curl == url:
    print("Job applied successfully")
else:
    print("Test failed")
driver.quit()


