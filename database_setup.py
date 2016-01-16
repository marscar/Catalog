import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250))
    email = Column(String(250))
    picture = Column(String(250))


class Listing(Base):
    __tablename__ = 'listing'

    id = Column(Integer, primary_key=True)
    address = Column(String(250), nullable=False)
    description = Column(String(250))
    type_ = Column(String(40), nullable=False)
    description = Column(String(250))
    picture = Column(String(250))
    zip_ = Column(String(5), nullable=False)
    price = Column(Integer)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'ref': self.id,
            'address': self.address,
            'type': self.type_,
            'location': self.zip_,
            'picture': self.picture,
            'description': self.description
            }


class Room(Base):
    __tablename__ = 'room'

    id = Column(Integer, primary_key=True)
    type_ = Column(String(40), nullable=False)
    floor = Column(Integer, nullable=False)
    listing_id = Column(Integer, ForeignKey('listing.id'))
    listing = relationship(Listing, single_parent=True, cascade="all, delete-orphan")
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'type': self.type_,
            'floor': self.floor,
            'id': self.id,
            'listing_id': self.listing_id,
            }


engine = create_engine('sqlite:///listings.db')


Base.metadata.create_all(engine)
