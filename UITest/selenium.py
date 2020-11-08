from selenium import webdriver
import time
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.keys import Keys

driver = webdriver.Firefox()
driver.get("http://google.com")
driver.maximize_window()
time.sleep(5)
inputElement = driver.find_element_by_name("q")
inputElement.send_keys("Techbeamers")
inputElement.submit()
time.sleep(20)

driver.close()
