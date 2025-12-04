from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, insert

from infrastructure.db.models.bidding.supply import SupplyModel
from infrastructure.db.models.bidding.bidder import BidderModel
from infrastructure.db.models.bidding.associations import supply_bidder_association


DEFAULT_SUPPLIES = [
    {"id": "supply1", "name": "Supply 1"},
    {"id": "supply2", "name": "Supply 2"},
]

DEFAULT_BIDDERS = [
    {"id": "bidder1", "country": "US", "name": "Bidder 1"},
    {"id": "bidder2", "country": "GB", "name": "Bidder 2"},
    {"id": "bidder3", "country": "US", "name": "Bidder 3"},
]

SUPPLY_BIDDER_ASSOCIATIONS = {
    "supply1": ["bidder1", "bidder2", "bidder3"],
    "supply2": ["bidder2", "bidder3"],
}


async def load_default_supplies(session: AsyncSession) -> None:
    for supply_data in DEFAULT_SUPPLIES:
        result = await session.execute(
            select(SupplyModel).where(SupplyModel.id == supply_data["id"])
        )
        existing_supply = result.scalar_one_or_none()

        if not existing_supply:
            supply = SupplyModel(**supply_data)
            session.add(supply)
            print(f"Created supply: {supply_data['id']}")
        else:
            print(f"Supply already exists: {supply_data['id']}")

    await session.commit()


async def load_default_bidders(session: AsyncSession) -> None:
    for bidder_data in DEFAULT_BIDDERS:
        result = await session.execute(
            select(BidderModel).where(BidderModel.id == bidder_data["id"])
        )
        existing_bidder = result.scalar_one_or_none()

        if not existing_bidder:
            bidder = BidderModel(**bidder_data)
            session.add(bidder)
            print(f"Created bidder: {bidder_data['id']}")
        else:
            print(f"Bidder already exists: {bidder_data['id']}")

    await session.commit()


async def load_supply_bidder_associations(session: AsyncSession) -> None:
    for supply_id, bidder_ids in SUPPLY_BIDDER_ASSOCIATIONS.items():
        result = await session.execute(
            select(SupplyModel.id).where(SupplyModel.id == supply_id)
        )
        if result.scalar_one_or_none() is None:
            print(f"Supply {supply_id} not found, skipping associations")
            continue

        result = await session.execute(
            select(BidderModel.id).where(BidderModel.id.in_(bidder_ids))
        )
        existing_bidder_ids = set(result.scalars().all())

        for bidder_id in existing_bidder_ids:
            result = await session.execute(
                select(supply_bidder_association).where(
                    supply_bidder_association.c.supply_id == supply_id,
                    supply_bidder_association.c.bidder_id == bidder_id,
                )
            )
            existing_association = result.first()

            if not existing_association:
                await session.execute(
                    insert(supply_bidder_association).values(
                        supply_id=supply_id,
                        bidder_id=bidder_id,
                    )
                )
                print(f"Associated {bidder_id} with {supply_id}")
            else:
                print(f"Association {bidder_id} with {supply_id} already exists")

    await session.commit()


async def load_all_fixtures(session: AsyncSession) -> None:
    print("=" * 50)
    print("Loading database fixtures...")
    print("=" * 50)

    await load_default_supplies(session)
    await load_default_bidders(session)
    await load_supply_bidder_associations(session)

    print("=" * 50)
    print("Fixtures loaded successfully!")
    print("=" * 50)
