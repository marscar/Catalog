from flask import (Flask, render_template, request, redirect, url_for, jsonify,
                   flash)
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Listing, Room, User

from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

from flask.ext.seasurf import SeaSurf
from dict2xml import dict2xml

app = Flask(__name__)
csrf = SeaSurf(app)

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read()
                       )['web']['client_id']
APPLICATION_NAME = "real estate app"

# Connect to Database and create database session
engine = create_engine('sqlite:///listings.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token+++
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# Autenticate with Facebook
@csrf.exempt
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = (json.loads(open('fb_client_secrets.json', 'r').read())[
                  'web']['app_id'])
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = ('https://graph.facebook.com/oauth/access_token?grant_type='
           'fb_exchange_token&client_id=%s&client_secret=%s&'
           'fb_exchange_token=%s'
           % (app_id, app_secret, access_token))
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    token = result.split("&")[0]

    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    # let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = ('https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height='
           '200&width=200' % token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += (' " style = "width: 300px; height: 300px;border-radius: 150px;'
               '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> ')
    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = ('https://graph.facebook.com/%s/permissions?access_token=%s'
           % (facebook_id, access_token))
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


# Autenticate with Google
@csrf.exempt
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check to see if user is already logged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already '
                                            'connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # See if a user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += (' " style = "width: 300px; height: 300px;border-radius: 150px;'
               '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> ')
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
        'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def loggedUser():
    if 'username' not in login_session:
        return redirect(url_for('/login'))


# Logout Google account
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Shows all listings
@app.route('/')
@app.route('/listings/')
def showListings():
    listings = session.query(Listing).all()
    if 'username' not in login_session:
        return render_template('publiclistings.html',
                               listings=listings)
    else:
        return render_template('listings.html', listings=listings)


# Create new listings
@app.route('/listing/new/', methods=['GET', 'POST'])
def newListing():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newListing = Listing(
            user_id=login_session['user_id'],
            type_=request.form['type'],
            address=request.form['address'],
            zip_=request.form['zip'],
            price=request.form['price'],
            picture=request.form['picture'],
            description=request.form['description'])
        session.add(newListing)
        session.commit()
        flash("New Listing Created")
        return redirect(url_for('showListings'))
    else:
        return render_template('newListing.html')


# Edit listings
@app.route('/listing/<int:listing_id>/edit/', methods=['GET', 'POST'])
def editListing(listing_id):
    selected_listing = (session.query(Listing)
                        .filter_by(id=listing_id).one())
    if 'username' not in login_session:
        return redirect('/login')
    if selected_listing.user_id != login_session['user_id']:
        return ("<script>function myFunction() {alert('You are not authorized "
                "to edit this listing. please create your own listing in "
                "order to delete.'); document.location.href = "
                "'http://localhost:8000/listings/';}"
                "</script><body onload=myFunction()>")
    if request.method == 'POST':
        if request.form['type']:
            selected_listing.type_ = request.form['type']
        if request.form['address']:
            selected_listing.address = request.form['address']
        if request.form['zip']:
            selected_listing.zip_ = request.form['zip']
        if request.form['price']:
            selected_listing.price = request.form['price']
        selected_listing.picture = request.form['picture']
        selected_listing.description = request.form['description']
        session.add(selected_listing)
        session.commit()
        flash("Listing Successfully Edited")
        return redirect(url_for('showListings'))
    else:
        return render_template('editListing.html',
                               listing=selected_listing)


# Delete listings
@app.route('/listing/<int:listing_id>/delete/', methods=['GET', 'POST'])
def deleteListing(listing_id):
    if 'username' not in login_session:
        return redirect('/login')
    selected_listing = (session.query(Listing)
                        .filter_by(id=listing_id).one())
    if selected_listing.user_id != login_session['user_id']:
        return ("<script>function myFunction() {alert('You are not authorized "
                "to delete this listing. please create your own listing in "
                "order to delete.'); document.location.href = "
                "'http://localhost:8000/listings/';}"
                "</script><body onload=myFunction()>")
    if request.method == 'POST':
        session.delete(selected_listing)
        session.commit()
        flash("Listing Successfully Deleted")
        return redirect(url_for('showListings'))
    else:
        return render_template('deleteListing.html',
                               listing=selected_listing)


# Shows listing details
@app.route('/listing/<int:listing_id>/')
@app.route('/listing/<int:listing_id>/room/')
def showRoom(listing_id):
    listing = session.query(Listing).filter_by(id=listing_id).one()
    creator = getUserInfo(listing.user_id)
    rooms = (session.query(Room).filter_by(listing_id=listing_id).
             order_by(Room.floor))
    if not rooms:
        rooms = []
    if ('username' not in login_session or creator.id != login_session[
            'user_id']):
        return render_template('publicroom.html', listing=listing,
                               rooms=rooms, creator=creator)
    else:
        return render_template('room.html', listing=listing,
                               rooms=rooms, creator=creator)

    return render_template('room.html', listing=listing, rooms=rooms)


# Create new rooms of a listing
@app.route('/listing/<int:listing_id>/room/new/', methods=['GET', 'POST'])
def newRoom(listing_id):
    if 'username' not in login_session:
        return redirect('/login')
    listing = session.query(Listing).filter_by(id=listing_id).one()
    if listing.user_id != login_session['user_id']:
        return ("<script>function myFunction() {alert('You are not authorized "
                "to edit this room. please create your own listing in "
                "order to delete.'); document.location.href = "
                "'http://localhost:8000/listing/%d/';}"
                "</script><body onload=myFunction()>") % listing_id
    if request.method == 'POST':
        newRoom = Room(type_=request.form['rtype'], floor=request.form[
            'floor'], listing_id=listing_id, user_id=listing.user_id
                       )
        session.add(newRoom)
        session.commit()
        flash("Room Created")
        return redirect(url_for('showRoom', listing_id=listing_id))
    else:
        return render_template('newRoom.html', listing=listing)


# Edit rooms
@app.route('/listing/<int:listing_id>/room/<int:room_id>/edit/',
           methods=['GET', 'POST'])
def editRoom(listing_id, room_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedRoom = session.query(Room).filter_by(id=room_id).one()
    if editedRoom.user_id != login_session['user_id']:
        return ("<script>function myFunction() {alert('You are not authorized "
                "to edit this room. please create your own listing in "
                "order to delete.'); document.location.href = "
                "'http://localhost:8000/listing/%d/';}</script><body "
                "onload=myFunction()>") % listing_id
    if request.method == 'POST':
        if request.form['rtype']:
            editedRoom.type_ = request.form['rtype']
        if request.form['floor']:
            editedRoom.floor = request.form['floor']
        session.add(editedRoom)
        session.commit()
        flash("Room Successfully Edited")
        return redirect(url_for('showRoom',
                                listing_id=listing_id))
    else:
        return render_template('editRoom.html', room=editedRoom)


# Delete rooms
@app.route('/listing/<int:listing_id>/room/<int:room_id>/delete/',
           methods=['GET', 'POST'])
def deleteRoom(listing_id, room_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedRoom = session.query(Room).filter_by(id=room_id).one()
    if editedRoom.user_id != login_session['user_id']:
        return ("<script>function myFunction() {alert('You are not authorized "
                "to delete this room. please create your own listing in "
                "order to delete.'); document.location.href = "
                "'http://localhost:8000/listing/%d/';}"
                "</script><body onload=myFunction()>") % listing_id
    if request.method == 'POST':
        session.delete(editedRoom)
        session.commit()
        flash("Room Successfully Deleted")
        return redirect(url_for('showRoom',
                                listing_id=listing_id))
    else:
        return render_template('deleteRoom.html', room=editedRoom)


# XML API endpoint for all listings
@app.route('/listings/XML')
def ListingsXML():
    listings = session.query(Listing).all()
    return dict2xml([i.serialize for i in listings],
                    wrap="Listing", indent="  ")


# XML API endpoint for listing page
@app.route('/listing/<int:listing_id>/room/XML')
def listingRoomXML(listing_id):
    listing = session.query(Listing).filter_by(id=listing_id).one()
    rooms = session.query(Room).filter_by(
        listing_id=listing_id).all()
    my_list = {"Listing": listing.serialize, "Rooms": {"Room": [i.serialize for i in rooms]}}
    return dict2xml(my_list, indent="  ")

# JSON API endpoint for all listings
@app.route('/listings/JSON')
def ListingsJSON():
    listings = session.query(Listing).all()
    return jsonify(Listings=[i.serialize for i in listings])


# JSON API endpoint for listing page
@app.route('/listing/<int:listing_id>/room/JSON')
def listingRoomJSON(listing_id):
    listing = session.query(Listing).filter_by(id=listing_id).one()
    rooms = session.query(Room).filter_by(
        listing_id=listing_id).all()
    return jsonify(Listing=listing.serialize,
                   Rooms=[i.serialize for i in rooms])


# RSS API endpoint for all listings
@app.route('/listings/listingsRSS')
def listingsRSSFeed():
    listings = session.query(Listing).all()
    return render_template('listingsRSS.xml', listings=listings)


# RSS API endpoint for listing page
@app.route('/listing/<int:listing_id>/room/roomRSS')
def RoomRSSFeed(listing_id):
    listing = session.query(Listing).filter_by(id=listing_id).one()
    rooms = (session.query(Room).filter_by(listing_id=listing_id).
             order_by(Room.floor))
    return render_template('roomRSS.xml', listing=listing, rooms=rooms)


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showListings'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showListings'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
