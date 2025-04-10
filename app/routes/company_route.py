from uuid import UUID
from fastapi import APIRouter, Depends, Path, HTTPException, Body, status
from loguru import logger
from app.handlers.auth_handlers import get_current_user
from app.database.models import Companies, Users
from app.pydantic_models.company_schemas import (
    CompanyCreateSchema,
    CompanyEditSchema,
    CompanySchema,
    CompanyListResponseSchema
)

company_router = APIRouter()


@company_router.post("/add", response_model=CompanySchema, status_code=status.HTTP_201_CREATED, summary="Добавление компании")
async def add_company(
    data: CompanyCreateSchema = Body(...),
    admin: Users = Depends(get_current_user)
):
    logger.info(f"Создание компании: {data.dict()}")
    try:
        company = await Companies.create(
            company_name=data.company_name,
            description=data.description
        )
        logger.success(
            f"Компания {company.company_name} создана ({company.company_id})")
        return company
    except Exception as e:
        logger.exception("Ошибка при создании компании")
        raise HTTPException(status_code=500, detail="Ошибка сервера") from e


@company_router.patch("/{company_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Редактирование компании")
async def edit_company(
    company_id: UUID = Path(..., title="ID компании"),
    data: CompanyEditSchema = Body(...),
    admin: Users = Depends(get_current_user)
):
    logger.info(
        f"Обновление компании {company_id}: {data.dict(exclude_unset=True)}")
    try:
        updated = await Companies.filter(company_id=company_id).update(**data.dict(exclude_unset=True))
        if not updated:
            logger.warning(f"Компания {company_id} не найдена")
            raise HTTPException(status_code=404, detail="Компания не найдена")
        logger.success(f"Компания {company_id} обновлена")
    except Exception as e:
        logger.exception("Ошибка при обновлении компании")
        raise HTTPException(status_code=500, detail="Ошибка сервера") from e


@company_router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удаление компании")
async def delete_company(
    company_id: UUID = Path(..., title="ID компании"),
    admin: Users = Depends(get_current_user)
):
    logger.info(f"Удаление компании {company_id}")
    try:
        deleted = await Companies.filter(company_id=company_id).delete()
        if not deleted:
            logger.warning(f"Компания {company_id} не найдена")
            raise HTTPException(status_code=404, detail="Компания не найдена")
        logger.success(f"Компания {company_id} удалена")
    except Exception as e:
        logger.exception("Ошибка при удалении компании")
        raise HTTPException(status_code=500, detail="Ошибка сервера") from e


@company_router.get("/all", response_model=CompanyListResponseSchema, summary="Список всех компаний")
async def list_companies(admin: Users = Depends(get_current_user)):
    logger.info("Запрос на получение списка компаний")
    try:
        companies = await Companies.all().values(
            "company_id", "company_name", "description"
        )
        return CompanyListResponseSchema(
            total=len(companies),
            companies=[
                CompanySchema(
                    company_id=c["company_id"],
                    company_name=c["company_name"],
                    description=c["description"]
                )
                for c in companies
            ]
        )
    except Exception as e:
        logger.exception("Ошибка при получении списка компаний")
        raise HTTPException(status_code=500, detail="Ошибка сервера") from e


@company_router.get("/{company_id}", response_model=CompanySchema, summary="Просмотр компании")
async def get_company(
    company_id: UUID = Path(..., title="ID компании"),
    admin: Users = Depends(get_current_user)
):
    logger.info(f"Просмотр компании {company_id}")
    try:
        company = await Companies.filter(company_id=company_id).first().values(
            "company_id", "company_name", "description"
        )
        if not company:
            logger.warning("Компания не найдена")
            raise HTTPException(status_code=404, detail="Компания не найдена")

        return CompanySchema(**company)
    except Exception as e:
        logger.exception("Ошибка при просмотре компании")
        raise HTTPException(status_code=500, detail="Ошибка сервера") from e
