from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from infrastructure.db.base import Base
from .associations import supply_bidder_association


class BidderModel(Base):
    __tablename__ = 'bidders'

    id = Column(String, primary_key=True, index=True)
    country = Column(String(2), nullable=False, index=True)
    name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    supplies = relationship(
        "SupplyModel",
        secondary=supply_bidder_association,
        back_populates="bidders",
    )
    bids = relationship("BidModel", back_populates="bidder")

    def __repr__(self):
        return f"<Bidder(id={self.id}, country={self.country})>"
