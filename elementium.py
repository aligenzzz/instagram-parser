# custom elementium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement


def write(driver: webdriver.Chrome, ttl: int, xpath: str, value: str) -> None:
    element = WebDriverWait(driver, ttl).until(
        EC.element_to_be_clickable((By.XPATH, xpath))
    )
    
    if element:
        element.clear()
        element.send_keys(value)
    else:
        raise Exception(f'Element with xpath \'{xpath}\' not found or not clickable within {ttl} seconds')


def click(driver: webdriver.Chrome, ttl: int, xpath: str) -> None:
    element = WebDriverWait(driver, ttl).until(
        EC.element_to_be_clickable((By.XPATH, xpath))
    )
    
    if element:
        element.click()
    else:
        raise Exception(f'Element with xpath \'{xpath}\' not found or not clickable within {ttl} seconds')
    
    
def get(driver: webdriver.Chrome, ttl: int, xpath: str) -> WebElement:
    element = WebDriverWait(driver, ttl).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )
    
    if element:
        return element
    else:
        raise Exception(f'Element with xpath \'{xpath}\' not found within {ttl} seconds')
    