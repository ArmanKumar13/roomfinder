import os
from dotenv import load_dotenv

load_dotenv()

# ==========================
# Database Configuration
# ==========================

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "4000"))
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB")
MYSQL_SSL_CA = os.getenv("MYSQL_SSL_CA")

# ==========================
# Flask Secret Key
# ==========================

SECRET_KEY = os.getenv("SECRET_KEY")

# ==========================
# Mail Configuration
# ==========================

MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

# ==========================
# Cloudinary Configuration
# ==========================

CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")