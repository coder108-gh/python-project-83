from dotenv import load_dotenv
import os


def main():
    print("Hello from python-project-83!")
    load_dotenv()
    print(os.getenv('DOMAIN'))
    print(os.getenv('ROOT_URL'))


if __name__ == "__main__":
    main()
