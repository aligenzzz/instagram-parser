from mailtm import Email
import time
import re


class EmailListener:
    def __init__(self):
        self.email = None
        self.last_received_message = None

    def start_listening(self) -> None:
        tm = Email()
        tm.register()
        self.email = tm.address

        def listener(message):
            self.last_received_message = message
        
        tm.start(listener)
        
    def get_confirmation_code(self, ttl: int = 30) -> str:
        for _ in ttl:
            if 'Instagram' in self.last_received_message['subject']:
                return EmailListener.extract_confirmation_code(
                    self.last_received_message['text']
                )
            time.sleep(1)
                
    @staticmethod      
    def extract_confirmation_code(message: str) -> str:
        match = re.search(r'(\d{6})', message)
        return match.group(1) if match else None
    