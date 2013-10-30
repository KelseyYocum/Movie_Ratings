from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref

ENGINE = create_engine("sqlite:///ratings.db", echo= False)
session = scoped_session(sessionmaker(bind=ENGINE, autocommit = False, autoflush = False))

Base = declarative_base()
Base.query = session.query_property()

### Class declarations go here
class User(Base):
    __tablename__="users"
    id = Column(Integer, primary_key = True)
    email = Column(String(64), nullable= True)
    password = Column(String(64), nullable= True)
    age = Column(Integer, nullable=True)
    zipcode = Column(String(15), nullable = True)

class Movie(Base):
    __tablename__="movies"
    id = Column(Integer, primary_key = True)
    name = Column(String(64), nullable=True)
    release_date = Column(DateTime, nullable=True)
    imdb_url = Column(String(140), nullable = True)

class Rating(Base):
    __tablename__="ratings"
    id = Column(Integer, primary_key = True)
    movie_id = Column(Integer, ForeignKey('movies.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    rating = Column(Integer, nullable=True)

    movie = relationship("Movie", backref=backref("ratings", order_by=id))
    user = relationship("User", backref=backref("ratings", order_by=id))
### End class declarations

def make_new_user(email, password, age, zipcode):
    new_user = User(email=email, password=password, age=age, zipcode=zipcode)
    session.add(new_user)
    session.commit()

def getUserFromId(id):
    user = session.query(User).get(id)
    return user 

#returning a dictionary with list of movies and their ratings for a user id
def get_movie_list(id):
    user = session.query(User).filter_by(id=id).first()
    ratings = user.ratings
    movie_ratings = {}
    for m in ratings:
        movie_ratings[m.movie.name] = m.rating
    return movie_ratings


def get_movieid_from_name(movie_name):
    movie = session.query(Movie).filter_by(name=movie_name).first()
    return movie.id

def add_movie_rating(user_id, movie_id, rating):
    new_rating = Rating(movie_id=movie_id, user_id=user_id, rating=rating)
    session.add(new_rating)
    session.commit()

def user_rated_movie(movie_id, user_id):
    user = session.query(User).filter_by(id=user_id).first()
    ratings = user.ratings
    for m in ratings:
        if m.movie.id == movie_id:
            return True
    return False

def userExists(email):
    user = session.query(User).filter_by(email = email).first()
    if user == None:
        return False
    return True

def movie_does_not_exist(movie_name):
    movie = session.query(Movie).filter_by(name=movie_name).first()
    if movie == None:
        return True
    return False

def authenticate(email, password):
    user = session.query(User).filter_by(email = email, password = password).first()
    if user == None:
        return None
    return user.id

def change_rating(user_id, movie_id, new_rating):
    old_rating = session.query(Rating).filter_by(user_id=user_id, movie_id=movie_id).first()
    old_rating.rating = new_rating
    session.commit()

def get_users_ratings(movie_name):
    movie = session.query(Movie).filter_by(name = movie_name).first()
    ratings = movie.ratings
    user_ratings = {}
    for rating in ratings:
        user_ratings[rating.user_id] = rating.rating
    return user_ratings

def main():
    """In case we need this for something"""
    pass

if __name__ == "__main__":
    main()
