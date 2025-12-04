from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from infrastructure.db.base import Base


class BidModel(Base):
    __tablename__ = 'bids'

    id = Column(Integer, primary_key=True, autoincrement=True)
    auction_id = Column(Integer, ForeignKey(
        'auctions.id'
    ), nullable=False, index=True)
    bidder_id = Column(String, ForeignKey('bidders.id'),
                       nullable=False, index=True)
    price = Column(Float, nullable=True)
    latency_ms = Column(Integer, nullable=True)
    timed_out = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    auction = relationship("AuctionModel", back_populates="bids")
    bidder = relationship("BidderModel", back_populates="bids")

    def __repr__(self):
        return f"<Bid(id={self.id}, bidder_id={self.bidder_id}, price={self.price})>"
