from sqlalchemy import Column, String, ForeignKey, Table

from infrastructure.db.base import Base


supply_bidder_association = Table(
    'supply_bidder',
    Base.metadata,
    Column('supply_id', String, ForeignKey('supplies.id'), primary_key=True),
    Column('bidder_id', String, ForeignKey('bidders.id'), primary_key=True),
)
