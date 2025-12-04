from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from infrastructure.db.base import Base

from .associations import supply_bidder_association


class SupplyModel(Base):
    __tablename__ = 'supplies'

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    bidders = relationship(
        "BidderModel",
        secondary=supply_bidder_association,
        back_populates="supplies",
    )
    auctions = relationship("AuctionModel", back_populates="supply")

    def __repr__(self):
        return f"<Supply(id={self.id})>"
