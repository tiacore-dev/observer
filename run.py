import os
from dotenv import load_dotenv
from app import create_app
from metrics.logger import setup_logger
from app.database.models import Users, UserRoles, Companies, UserCompanyRelations


load_dotenv()


# Порт и биндинг
PORT = 8000

CONFIG_NAME = os.getenv('CONFIG_NAME')

setup_logger()


app = create_app(config_name=CONFIG_NAME)


async def create_admin():
    try:
        user = await Users.get_or_none(username="admin")
        if user:
            print("Админ уже существует")
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

    await create_admin()


# 📌 Запуск Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(PORT), reload=True)
