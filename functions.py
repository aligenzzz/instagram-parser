from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium_recaptcha_solver import RecaptchaSolver
from fake_useragent import UserAgent
from elementium import click, write
from config import CHROMEDRIVER_PATH
from constants import TTL
from passlib.pwd import genword
from mailtm import Email
from faker import Faker
import logging
import random
import string
import time
import re

logger = logging.getLogger(__name__)
    
    
def generate_full_name() -> str:
    fake = Faker()
    return fake.name()
    
def generate_username(k: int = 12) -> str:
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=k))

def generate_password(length: int = 16) -> str:
    return genword(length=length)

def generate_year(start: int = 1960, end: int = 2005) -> int:
    return random.randint(start, end)

    
class EmailListener:
    def __init__(self):
        self.email = None
        self.last_received_message = None

    def start_listening(self):
        tm = Email()
        tm.register()
        self.email = tm.address

        def listener(message):
            self.last_received_message = message
        
        tm.start(listener)
        
    def get_confirmation_code(self):
        for _ in range(30):
            if 'Instagram' in self.last_received_message['subject']:
                return EmailListener.extract_confirmation_code(
                    self.last_received_message['text']
                )
                
    @staticmethod      
    def extract_confirmation_code(message: str) -> str:
        match = re.search(r'(\d{6})', message)
        return match.group(1) if match else None
    
       
def create_account(full_name: str = None, username: str = None, 
                   password: str = None, year: str = None) -> tuple[bool, tuple[str, str]]:
    ua = UserAgent(platforms='pc')
    userAgent = ua.random
    
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={userAgent}')
    
    driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=options)       
    solver = RecaptchaSolver(driver=driver)

    driver.get('https://www.instagram.com/accounts/emailsignup/?hl=en')
    
    # creating temporary email
    tm = EmailListener()
    tm.start_listening()
    email = tm.email
    
    # generating data
    full_name = full_name or generate_full_name()
    username = username or generate_username()
    password = password or generate_password()
    year = year or generate_year()
    
    try:
        logging.info(f'Starting account creation for: {username}')
        
        # declining cookies
        try:
            click(driver, TTL, '//button[contains(text(), "Decline optional cookies")]')
        except:
            pass
            
        # filling the main data
        write(driver, TTL, '//input[@name="emailOrPhone"]', email)
        write(driver, TTL, '//input[@name="fullName"]', full_name)
        write(driver, TTL, '//input[@name="username"]', username)
        write(driver, TTL, '//input[@name="password"]', password)
        
        try:
            click(driver, TTL, '//button[contains(text(), "Sign up")]')
        except:
            click(driver, TTL, '//button[contains(text(), "Next")]')
        
        time.sleep(5)
        
        # filling the birth date (only year)
        year_select = Select(driver.find_element(By.XPATH, '//select[@title="Year:"]'))
        year_select.select_by_value(str(year))
        click(driver, TTL, '//button[contains(text(), "Next")]')
        time.sleep(15)
        
        # solving recaptcha
        outer_iframe = driver.find_element(By.XPATH, '//iframe[@id="recaptcha-iframe"]')
        driver.switch_to.frame(outer_iframe)
        inner_iframe = driver.find_element(By.XPATH, '//iframe[@title="reCAPTCHA"]')
        solver.click_recaptcha_v2(iframe=inner_iframe)
        driver.switch_to.default_content()
        click(driver, TTL, '//button[contains(text(), "Next")]')
        time.sleep(35)
        
        # filling the email confirmation
        confirmation_code = tm.get_confirmation_code()
        write(driver, TTL, '//input[@name="email_confirmation_code"]', confirmation_code)
        click(driver, TTL, '//div[contains(text(), "Next")]')
        time.sleep(60)
        
        driver.quit()
        logging.info(f'Account created successfully for: {username}')
        
        return True, (username, password)
        
    except Exception as e:
        logging.error(f'Error creating account: {str(e)}')
        driver.quit()
        return False, str(e)
        