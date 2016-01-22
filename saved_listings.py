from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Listing, Base, Room, User

engine = create_engine('sqlite:///listings.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/'
             '18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

# Menu for UrbanBurger
ref1 = Listing(user_id=1,
               address="28 Rumson Rd",
               type_="Condo",
               picture='http://www.urbancondospaces.com/wp-content/blogs.dir/'
               '1/files/2011/01/640x411xturnure-18977-copy.jpg.pagespeed.ic.'
               'EI6F69oNJ5.jpg',
               description="The Oaks. Large two bedroom condo. Level one, "
               "Foyer with closet, Living/Dining Room. bath, Eat in Kitchen.",
               price=215000, zip_='00042')

session.add(ref1)
session.commit()

ref2 = Listing(user_id=1,
               address="45 Mercury Ln ",
               type_="Single Family",
               picture='https://bakerresidential.files.wordpress.com/2009/12/'
               'single-family-home.jpg',
               description="Large 2 Bedroom end unit. 1st floor has Garage "
               "and Family room with fireplace. 2nd floor has living room/"
               "dining room combo with an eat in kitchen and 1/2 bath. third "
               "floor has 2 large bedrooms and 4 piece bath.",
               price=400000, zip_='10045')

session.add(ref2)
session.commit()

ref3 = Listing(user_id=1,
               address="54 Saturn Ln",
               type_="Condo",
               picture='',
               description="2 bedroom condo in excellent condition, large "
               "galley kitchen, dining/living room combo ",
               price=235000, zip_='00102')

session.add(ref3)
session.commit()

ref4 = Listing(user_id=1,
               address="200 Main St.",
               type_="Townhome",
               picture='http://ladleyandassociates.com/wp-content/uploads/'
               'dallas-townhomes.jpg',
               description="",
               price=175500, zip_='10025')

session.add(ref4)
session.commit()

ref5 = Listing(user_id=1,
               address="75 Essex Dr #1C ",
               type_="Coop",
               picture='http://www.shamrockfinancial.com/wp-content/uploads/'
               'iStock_condo.jpg',
               description="75 Essex Dr #1C Spacious, lovely 1 bedroom condo "
               "on first floor in a great building, features nice listing_id "
               "rooms, full bath, SGD to terrace off LR, many amenities - "
               "outdoor pool, gym, clubhouse, tennis court. Close to shopping "
               "and transportation. ",
               price=217000, zip_='10305')

session.add(ref5)
session.commit()

ref6 = Listing(user_id=1,
               address="1189 Willowbrook Rd ",
               type_="Apartment",
               picture='http://condodnagroup.com/wp-content/uploads/2015/04/'
               'Parkside-at-atria-condo.jpg',
               description="lovely 3 bedroom 2.5 semi for sale in desirable & "
               "convenient location close to all! 2 year old roof, new water "
               "tank, pella casement windows with built-in shades.",
               price=578000, zip_='10025')

session.add(ref6)
session.commit()

ref7 = Listing(user_id=1,
               address="48 Racal Ct ",
               type_="Single Family",
               picture='http://condodscrewednagroup.com/wp-contthe/ent/uplfuck'
               '/oads/2015/04/Parkside-at-atria-condo.jpg',
               description="3 level unit-lower level den or bedroom, .5 bath, "
               "entrance to common area, level 2- eat in kitchen, level 3-"
               "living room, master bedroom and full bath ",
               price=534000, zip_='10045')

session.add(ref7)
session.commit()

ref8 = Listing(user_id=1,
               address="27 Kathy Pl #2B ",
               type_="Single Family",
               picture='http://cdn.freshome.com/wp-content/uploads/2013/11/'
               'View-single-family-house.jpg',
               description="Beautiful! Move in condition 3 bedroom, 2 bath "
               "condo. Gleaming oak floors, renovated kitchen and bathrooms. ",
               price=380000, zip_='00042')

session.add(ref8)
session.commit()

ref9 = Listing(user_id=1,
               address="19 Donna Ct ",
               type_="Condo",
               picture='http://www.gordcollins.com/wp-content/uploads/2014/'
               '09/interior.jpg',
               description="Heartland Village - Beautiful 1 bedroom condo in "
               "excellent condition. Featuring gorgeous balcony views, great "
               "community amenities including large pool, clubhouse, "
               "playground, tennis courts.",
               price=235000, zip_='10305')

session.add(ref9)
session.commit()

ref10 = Listing(user_id=1,
                address="188 Richmond Hill Rd ",
                type_="Townhome",
                picture='http://inside-real-estate.com/martihampton/files/'
                '2011/02/tryonplacetownhomes.jpg',
                description="1st floor 1 bedroom within walking distance of "
                "Mall and amazing amounts of shopping. Transprotation to just "
                "about everywhere of your doorstep. Large Livingroom. "
                "Eat-in Kitchen. Vacant and ready to go.",
                price=458000, zip_='00042')

session.add(ref10)
session.commit()


room = Room(user_id=1,
            type_="Kitchen", floor=1, listing_id=1)

session.add(room)
session.commit()

room = Room(user_id=1,
            type_="livingroom", floor=1, listing_id=1)

session.add(room)
session.commit()

room = Room(user_id=1,
            type_="bedroom", floor=2, listing_id=1)

session.add(room)
session.commit()

room = Room(user_id=1,
            type_="bedroom", floor=2, listing_id=1)

session.add(room)
session.commit()

oom = Room(user_id=1,
           type_="foyer", floor=1, listing_id=1)

session.add(room)
session.commit()

room = Room(user_id=1,
            type_="bathroom", floor=1, listing_id=1)

session.add(room)
session.commit()

room = Room(user_id=1,
            type_="bathroom", floor=2, listing_id=1)

session.add(room)
session.commit()

room = Room(user_id=1,
            type_="garage", floor=1, listing_id=1)

session.add(room)
session.commit()

oom = Room(user_id=1,
           type_="kitchen", floor=1, listing_id=2)

session.add(room)
session.commit()

room = Room(user_id=1,
            type_="laundry", floor=0, listing_id=2)

session.add(room)
session.commit()

room = Room(user_id=1,
            type_="bedroom", floor=1, listing_id=2)

session.add(room)
session.commit()

room = Room(user_id=1,
            type_="bathroom", floor=1, listing_id=2)

session.add(room)
session.commit()

oom = Room(user_id=1,
           type_="half bathroom", floor=2, listing_id=2)

session.add(room)
session.commit()

room = Room(user_id=1,
            type_="bedroom", floor=2, listing_id=2)

session.add(room)
session.commit()

room = Room(user_id=1,
            type_="kitchen", floor=1, listing_id=3)

session.add(room)
session.commit()

room = Room(user_id=1,
            type_="bathroom", floor=1, listing_id=3)

session.add(room)
session.commit()

oom = Room(user_id=1,
           type_="bedroom", floor=1, listing_id=3)

session.add(room)
session.commit()

room = Room(user_id=1,
            type_="kitchen", floor=1, listing_id=4)

session.add(room)
session.commit()

room = Room(user_id=1,
            type_="bathroom", floor=1, listing_id=4)

session.add(room)
session.commit()

room = Room(user_id=1,
            type_="bedroom", floor=1, listing_id=4)

session.add(room)
session.commit()

oom = Room(user_id=1,
           type_="bedroom", floor=1, listing_id=4)

session.add(room)
session.commit()

room = Room(user_id=1,
            type_="livingroom", floor=1, listing_id=4)

session.add(room)
session.commit()

room = Room(user_id=1,
            type_="kitchen", floor=1, listing_id=5)

session.add(room)
session.commit()

room = Room(user_id=1,
            type_="foyer", floor=1, listing_id=5)

session.add(room)
session.commit()

oom = Room(user_id=1,
           type_="laundry", floor=1, listing_id=5)

session.add(room)
session.commit()

room = Room(user_id=1,
            type_="bathroom", floor=1, listing_id=5)

session.add(room)
session.commit()

room = Room(user_id=1,
            type_="garage", floor=1, listing_id=5)

session.add(room)
session.commit()

room = Room(user_id=1,
            type_="bedroom", floor=2, listing_id=5)

session.add(room)
session.commit()

oom = Room(user_id=1,
           type_="bathroom", floor=2, listing_id=5)

session.add(room)
session.commit()

room = Room(user_id=1,
            type_="bedroom", floor=2, listing_id=5)

session.add(room)
session.commit()

room = Room(user_id=1,
            type_="bedroom", floor=3, listing_id=5)

session.add(room)
session.commit()

room = Room(user_id=1,
            type_="kitchen", floor=1, listing_id=6)

session.add(room)
session.commit()

oom = Room(user_id=1,
           type_="livingroom", floor=1, listing_id=6)

session.add(room)
session.commit()

room = Room(user_id=1,
            type_="bathroom", floor=1, listing_id=6)

session.add(room)
session.commit()

room = Room(user_id=1,
            type_="bedroom", floor=1, listing_id=6)

session.add(room)
session.commit()

room = Room(user_id=1,
            type_="bedroom", floor=1, listing_id=6)

session.add(room)
session.commit()

oom = Room(user_id=1,
           type_="kitchen", floor=1, listing_id=7)

session.add(room)
session.commit()

room = Room(user_id=1,
            type_="livingroom", floor=1, listing_id=7)

session.add(room)
session.commit()

room = Room(user_id=1,
            type_="bathroom", floor=1, listing_id=7)

session.add(room)
session.commit()

room = Room(user_id=1,
            type_="bedroom", floor=1, listing_id=7)

session.add(room)
session.commit()

oom = Room(user_id=1,
           type_="kitchen", floor=0, listing_id=8)

session.add(room)
session.commit()

room = Room(user_id=1,
            type_="bathroom", floor=0, listing_id=8)

session.add(room)
session.commit()

room = Room(user_id=1,
            type_="livingroom", floor=1, listing_id=8)

session.add(room)
session.commit()

room = Room(user_id=1,
            type_="bedroom", floor=1, listing_id=8)

session.add(room)
session.commit()

oom = Room(user_id=1,
           type_="bedroom", floor=2, listing_id=8)

session.add(room)
session.commit()

room = Room(user_id=1,
            type_="half bathroom", floor=1, listing_id=8)

session.add(room)
session.commit()

room = Room(user_id=1,
            type_="kitchen", floor=1, listing_id=9)

session.add(room)
session.commit()

room = Room(user_id=1,
            type_="bathroom", floor=1, listing_id=9)

session.add(room)
session.commit()

room = Room(user_id=1,
            type_="bedroom", floor=1, listing_id=9)

session.add(room)
session.commit()

room = Room(user_id=1,
            type_="bedroom", floor=2, listing_id=9)

session.add(room)
session.commit()

room = Room(user_id=1,
            type_="laundry", floor=0, listing_id=10)

session.add(room)
session.commit()

room = Room(user_id=1,
            type_="garage", floor=0, listing_id=10)

session.add(room)
session.commit()

room = Room(user_id=1,
            type_="kitchen", floor=1, listing_id=10)

session.add(room)
session.commit()

room = Room(user_id=1,
            type_="livingroom", floor=1, listing_id=10)

session.add(room)
session.commit()

room = Room(user_id=1,
            type_="bathroom", floor=1, listing_id=10)

session.add(room)
session.commit()

room = Room(user_id=1,
            type_="bedroom", floor=2, listing_id=10)

session.add(room)
session.commit()

room = Room(user_id=1,
            type_="bedroom", floor=2, listing_id=10)

session.add(room)
session.commit()

room = Room(user_id=1,
            type_="bathroom", floor=2, listing_id=10)

session.add(room)
session.commit()


print "added listings!"
