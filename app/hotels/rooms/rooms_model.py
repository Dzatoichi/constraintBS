import enum

from sqlalchemy import Column, Enum, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.database import Base

class RoomType(enum.Enum):
    STANDART = "standart"
    DELUXE = "deluxe"
    SUITE = "suite"

room_amenity_association = Table(
    "room_amenity",
    Base.metadata,
    Column("room_id", Integer, ForeignKey("rooms.id", ondelete="CASCADE"), primary_key=True),
    Column("amenity_id", Integer, ForeignKey("amenities.id", ondelete="CASCADE"), primary_key=True),
)

class Room(Base):
    __tablename__ = "rooms"
    id: Mapped[int] = mapped_column(primary_key=True,)
    number: Mapped[str] = mapped_column(String(10), nullable=False)
    room_type: Mapped[RoomType] = mapped_column(Enum(RoomType), default=RoomType.STANDART)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    price_per_night: Mapped[int] = mapped_column(Integer, nullable=False)
    floor: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str | None] = mapped_column(String(500))
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"))
    amenities = relationship("Amenity", secondary=room_amenity_association, back_populates="rooms", lazy="selectin",)

class Amenity(Base):
    __tablename__ = "amenities"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)  # Например: "Wi-Fi", "Кондиционер"
    
    rooms = relationship("Room", secondary=room_amenity_association, back_populates="amenities", lazy="selectin",)