from functions import create_account
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


if __name__ == '__main__':
    result = create_account()
    print(result)
    