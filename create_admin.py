from database.db import users

admin_user = {
    "name": "Admin",
    "email": "sharmashiviom@gmail.com",
    "password": "admin@123",
    "role": "admin"
}
existing_admin = users.find_one({"email": admin_user["email"]})
if existing_admin:
    print("⚠️ Admin already exists")
else:
    users.insert_one(admin_user)
    print("✅ Admin created successfully!")