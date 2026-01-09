import asyncio
from sqlalchemy import select

from app.billing.enums import TariffCode
from app.billing.models.tariff_plan import TariffPlan
from infrastructure.db.session import async_session_maker


async def seed_tariff_plans() -> None:
    async with async_session_maker() as session:
        # 1. Получаем уже существующие тарифы
        result = await session.execute(select(TariffPlan.code))
        existing_codes = {row[0] for row in result.all()}

        plans_to_create = []

        # 2. FREE
        if TariffCode.FREE.value not in existing_codes:
            plans_to_create.append(
                TariffPlan(**TariffPlan.default_free())
            )

        # 3. PAID_MONTH
        if TariffCode.PAID_MONTH.value not in existing_codes:
            plans_to_create.append(
                TariffPlan(**TariffPlan.default_paid_month())
            )

        if not plans_to_create:
            print("Tariff plans already exist, nothing to seed")
            return

        # 4. Сохраняем
        session.add_all(plans_to_create)
        await session.commit()

        print(f"Seeded {len(plans_to_create)} tariff plans")


if __name__ == "__main__":
    asyncio.run(seed_tariff_plans())