import os
from dotenv import load_dotenv
from app import create_app
from app.database.models import Users, UserRoles, Companies, UserCompanyRelations
from app.scheduler.scheduler import start_scheduler

load_dotenv()

# Порт и биндинг
PORT = 8000

app = create_app(config_name='Development')

for route in app.routes:
    print("🛣️", route.path, "→", getattr(route, "endpoint", None))


async def create_admin():
    try:
        user = await Users.get_or_none(username="admin")
        if user:
            return
        role = await UserRoles.create(role_name="Администратор")
        company = await Companies.create(company_name="Tiacore")

        password = os.getenv('PASSWORD')
        if not password:
            raise ValueError("PASSWORD not set in environment variables.")

        user = await Users.create_user(
            username="admin",
            password=password,
        )
        print(f"✅ Admin {user.username} created successfully.")
        await UserCompanyRelations.create(
            role=role, company=company, user=user)

        print("✅ Relation created successfully.")

    except Exception as e:
        print("❌ Error during admin creation:", e)


@app.on_event("startup")
async def startup_event():
    # Создаем администратора при запуске
    await create_admin()
    await start_scheduler()

# 📌 Запуск Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(PORT), reload=True)
