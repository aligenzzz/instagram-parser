from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium_recaptcha_solver import RecaptchaSolver
from elementium.drivers.se import SeElements
from fake_useragent import UserAgent
from constants import CHROMEDRIVER_PATH
from passlib.pwd import genword
from mailtm import Email
from faker import Faker
import random
import string
import time
import re
    
    
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
                
            
def create_account() -> tuple[bool, tuple[str, str]]:
    ua = UserAgent(platforms='pc')
    userAgent = ua.random
    
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={userAgent}')
    
    driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=options)    
    
    solver = RecaptchaSolver(driver=driver)
    # driver.get('https://www.google.com/recaptcha/api2/demo')
    # recaptcha_iframe = driver.find_element(By.XPATH, '//iframe[@title="reCAPTCHA"]')
    # solver.click_recaptcha_v2(iframe=recaptcha_iframe)
    
    
    driver.get('https://www.instagram.com/accounts/emailsignup/?hl=en')
       
    se = SeElements(driver)
    
    # creating temporary email
    tm = EmailListener()
    tm.start_listening()
    email = tm.email
    
    # generating data
    full_name = generate_full_name()
    username = generate_username()
    password = generate_password()
    year = generate_year()
    
    try:
        # declining cookies
        try:
            se.xpath('//button[contains(text(), "Decline optional cookies")]', wait=True, ttl=2).click()  
        except:
            pass
            
        # filling the main data
        se.xpath('//input[@name="emailOrPhone"]', wait=True, ttl=2).clear().write(email)
        se.xpath('//input[@name="fullName"]', wait=True, ttl=2).clear().write(full_name)
        se.xpath('//input[@name="username"]', wait=True, ttl=2).clear().write(username)
        se.xpath('//input[@name="password"]', wait=True, ttl=2).clear().write(password)
        
        try:
            se.xpath('//button[contains(text(), "Sign up")]', wait=True, ttl=2).click()  
        except:
            se.xpath('//button[contains(text(), "Next")]', wait=True, ttl=2).click()  
        
        time.sleep(5)
        
        # filling the birth date (only year)
        year_select = Select(driver.find_element_by_xpath('//select[@title="Year:"]'))
        year_select.select_by_value(str(year))
        se.xpath('//button[contains(text(), "Next")]', wait=True, ttl=2).click()
        time.sleep(5)
        
        # solving recaptcha
        outer_iframe = driver.find_element_by_xpath('//iframe[@id="recaptcha-iframe"]')
        driver.switch_to.frame(outer_iframe)
        inner_iframe = driver.find_element_by_xpath('//iframe[@title="reCAPTCHA"]')
        solver.click_recaptcha_v2(iframe=inner_iframe)
        driver.switch_to.default_content()
        se.xpath('//button[contains(text(), "Next")]', wait=True, ttl=2).click()
        time.sleep(35)
        
        # filling the email confirmation
        confirmation_code = tm.get_confirmation_code()
        se.xpath('//input[@name="email_confirmation_code"]', wait=True, ttl=2).clear().write(confirmation_code)
        se.xpath('//div[contains(text(), "Next")]', wait=True, ttl=2).click()
        time.sleep(5)
        
        return True, (username, password)
        
    except Exception as e:
        print(e)
        driver.quit()
        return False, (username, password)
        