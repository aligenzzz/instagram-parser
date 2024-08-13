from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium_recaptcha_solver import RecaptchaSolver
from fake_useragent import UserAgent
from elementium import click, write, get
from email_listener import EmailListener
from config import CHROMEDRIVER_PATH
from constants import TTL
from passlib.pwd import genword
from faker import Faker
import logging
import random
import string
import time

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

    
def create_account(full_name: str = None, username: str = None, 
                   password: str = None, year: str = None) -> tuple[bool, tuple[str, str]]:
    try:
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
    
        logging.info(f'Starting account creation for: {username}')
        
        # declining cookies
        try:
            click(driver, int(TTL / 10), '//button[contains(text(), "Decline optional cookies")]')
            logging.info('Cookies declined successfully.')
        except:
            pass
            
        # filling the main data
        logging.info('Filling the main data:')
        try:
            write(driver, TTL, '//input[@name="emailOrPhone"]', email)
            write(driver, TTL, '//input[@name="fullName"]', full_name)
            write(driver, TTL, '//input[@name="username"]', username)
            write(driver, TTL, '//input[@name="password"]', password)
            
            try:
                click(driver, TTL, '//button[contains(text(), "Sign up")]')
            except:
                click(driver, TTL, '//button[contains(text(), "Next")]')
            
            logging.info('The main data filled successfully.')
            
        except Exception as e:
            logging.error(f'Failed to fill the main data: {str(e)}')
            raise Exception('Failed to fill the main data.')
           
        # filling the birth date (only year)
        logging.info('Filling the birth date:')
        try:
            year_select = Select(get(driver, TTL, '//select[@title="Year:"]'))
            year_select.select_by_value(str(year))
            
            click(driver, TTL, '//button[contains(text(), "Next")]')
            
            logging.info('The birth date filled successfully.')
            
        except Exception as e:
            logging.error(f'Failed to fill the birth date: {str(e)}')
            raise Exception('Failed to fill the birth date.')
        
        # solving recaptcha
        logging.info('Solving reCAPTCHA:')
        try:
            outer_iframe = get(driver, TTL, '//iframe[@id="recaptcha-iframe"]')      
            driver.switch_to.frame(outer_iframe)        
            inner_iframe = get(driver, TTL, '//iframe[@title="reCAPTCHA"]')
            solver.click_recaptcha_v2(iframe=inner_iframe)
            
            driver.switch_to.default_content()  
            click(driver, TTL, '//button[contains(text(), "Next")]')
            
            logging.info('reCAPTCHA solved successfully.')
            
        except Exception as e:
            logging.error(f'Failed to solve reCAPTCHA: {str(e)}')
            raise Exception('Failed to solve reCAPTCHA.')
        
        # filling the email confirmation
        logging.info('Confirming email:')
        try:
            confirmation_code = tm.get_confirmation_code(TTL)
            write(driver, TTL, '//input[@name="email_confirmation_code"]', confirmation_code)
            click(driver, TTL, '//div[contains(text(), "Next")]')
            
            logging.info('Email confirmed successfully.')
            
        except Exception as e:
            logging.error(f'Failed to confirm email: {str(e)}')
            raise Exception('Failed to confirm email.')
        
        time.sleep(TTL)
        
        driver.quit()
        logging.info(f'Account created successfully for: {username}')
        
        return True, (username, password)
        
    except Exception as e:
        logging.error(f'Failed to create account: {str(e)}')
        
        driver.quit()
        return False, str(e)
        