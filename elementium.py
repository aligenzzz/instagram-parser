# custom elementium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def write(driver: webdriver.Chrome, ttl: int, xpath: str, value: str):
    element = WebDriverWait(driver, ttl).until(
        EC.element_to_be_clickable((By.XPATH, xpath))
    )
    
    if element:
        element.clear()
        element.send_keys(value)
    else:
        raise Exception(f'Element with xpath \'{xpath}\' not found or not clickable within {ttl} seconds')


def click(driver: webdriver.Chrome, ttl: int, xpath: str):
    element = WebDriverWait(driver, ttl).until(
        EC.element_to_be_clickable((By.XPATH, xpath))
    )
    
    if element:
        element.click()
    else:
        raise Exception(f'Element with xpath \'{xpath}\' not found or not clickable within {ttl} seconds')