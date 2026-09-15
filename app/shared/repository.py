from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository[
    ModelType,
    CreateSchemaType: BaseModel,
    UpdateSchemaType: BaseModel,
    ]:

    def __init__(
            self, 
            model: type[ModelType],
        ) -> None:
        self.model = model

    async def create(
            self,
            session: AsyncSession,
            data: CreateSchemaType
    ) -> ModelType | None:
        """
        Создание записи
        """
        obj = self.model(**data.model_dump())

        session.add(obj)
        await session.flush()

        return obj

    async def get_by_id(
            self,
            session: AsyncSession,
            obj_id: int,
    ) -> ModelType | None:

        obj = await session.get(
            self.model,
            obj_id
            )

        return obj


    async def get_all(
            self,
            session: AsyncSession,
    ) -> list[ModelType] | None:

        stmt = select(self.model)

        objs = await session.execute(stmt)

        return list(objs.scalars().all())


    async def delete(
            self,
            session: AsyncSession,
            obj: ModelType,
    ) -> None:
        await session.delete(obj)
        await session.flush()


    async def update(
            self,
            session: AsyncSession,
            obj: ModelType,
            data: UpdateSchemaType,
    ) -> ModelType:
        update_data = data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(obj, field, value)

        await session.flush()

        return obj