import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_API_TOKEN = os.environ.get("TELEGRAM_API_TOKEN")
#PAYMENT_PROVIDER_TOKEN = os.environ.get("PAYMENT_PROVIDER_TOKEN")
OVPN_FILE_PATH = os.environ.get("OVPN_FILE_PATH")
WG_FILE_PATH = os.environ.get("WG_FILE_PATH")
QR_CODE_PATH = os.environ.get("QR_CODE_PATH")
LINKS_PATH = os.environ.get("LINKS_PATH")

# Настройки Юкассы
YOOKASSA_SHOP_ID = os.getenv('YOOKASSA_SHOP_ID', 'test_shop_id')
YOOKASSA_SECRET_KEY = os.getenv('YOOKASSA_SECRET_KEY', 'test_secret_key')

TARIFFS = {
    "product_a": {"price": 300, "name": "1 Month", "days": 30, "description": "1 месяц доступа"},
    "product_b": {"price": 900, "name": "3 Months", "days": 90, "description": "3 месяца доступа"},
    "product_c": {"price": 1500, "name": "6 Months", "days": 180, "description": "6 месяцев доступа"},
    "product_d": {"price": 2500, "name": "1 Year", "days": 365, "description": "1 год доступа"}
}
