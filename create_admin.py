import os
from dotenv import load_dotenv
from database.db import users

# Load environment variables
load_dotenv()

# Get admin credentials from environment variables
admin_email = os.getenv("ADMIN_EMAIL")
admin_password = os.getenv("ADMIN_PASSWORD")

# Validate that credentials are provided
if not admin_email or not admin_password:
    print("❌ ERROR: ADMIN_EMAIL and ADMIN_PASSWORD environment variables must be set in .env file")
    print("   Please copy .env.example to .env and fill in your desired admin credentials")
    exit(1)

admin_user = {
    "name": "Admin",
    "email": admin_email,
    "password": admin_password,
    "role": "admin"
}

existing_admin = users.find_one({"email": admin_user["email"]})
if existing_admin:
    print("⚠️ Admin already exists")
else:
    users.insert_one(admin_user)
    print("✅ Admin created successfully!")
