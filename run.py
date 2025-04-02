import os
from dotenv import load_dotenv
from app import create_app
from app.database.models import AdminUser, UserRole, Company

load_dotenv()

# Порт и биндинг
PORT = 8000

# 📌 Автоматическое создание супер-админа


app = create_app()


async def create_admin():
    try:
        role = await UserRole.create(role_id="admin", role_name="Администратор")
        company = await Company.create(company_name="Tiacore")

        password = os.getenv('PASSWORD')
        if not password:
            raise ValueError("PASSWORD not set in environment variables.")

        admin = await AdminUser.create_admin(
            username="admin",
            role=role,
            company=company,
            password=password,
        )
        print(f"✅ Admin {admin.username} created successfully.")

    except Exception as e:
        print("❌ Error during admin creation:", e)


@app.on_event("startup")
async def startup_event():
    # Создаем администратора при запуске
    await create_admin()

# 📌 Запуск Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(PORT), reload=True)
