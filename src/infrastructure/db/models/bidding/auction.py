from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from infrastructure.db.base import Base


class AuctionModel(Base):
    __tablename__ = 'auctions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    supply_id = Column(
        String,
        ForeignKey('supplies.id'),
        nullable=False,
        index=True
    )
    ip_address = Column(String, nullable=False)
    country = Column(String(2), nullable=False)
    winner_bidder_id = Column(String, ForeignKey('bidders.id'), nullable=True)
    winning_price = Column(Float, nullable=True)
    tmax = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    supply = relationship("SupplyModel", back_populates="auctions")
    winner = relationship("BidderModel", foreign_keys=[winner_bidder_id])
    bids = relationship("BidModel", back_populates="auction")

    def __repr__(self):
        return (
            f"<Auction(id={self.id}, supply_id={self.supply_id}, winner={self.winner_bidder_id})>"
        )
