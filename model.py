from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
import correlation

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

    def similarity(self, user2):
        paired_ratings = []
        d = {}
        for rating1 in self.ratings:
            d[rating1.movie_id] = rating1
        for rating2 in user2.ratings:
            user_rating = d.get(rating2.movie_id)
            if user_rating:
                paired_ratings.append((user_rating.rating, rating2.rating))
        if paired_ratings:
            return correlation.pearson(paired_ratings)
        else:
            return 0.0

    def predict_rating(self, movie):
        ratings = self.ratings
        other_ratings = movie.ratings
        similarities = [ (self.similarity(r.user), r) \
            for r in other_ratings ]
        similarities.sort(reverse = True)
        similarities = [ sim for sim in similarities if sim[0] > 0 ]
        if not similarities:
            return None
        numerator = sum([ r.rating * similarity for similarity, r in similarities ])
        denominator = sum([ similarity[0] for similarity in similarities ])
        return numerator/denominator


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

def get_movie_prediction(user_id, movie_name):
    movie_id = get_movieid_from_name(movie_name)
    movie = session.query(Movie).get(movie_id)
    ratings = movie.ratings
    rating_nums = []
    user_rating = None
    for r in ratings:
        if user_id:
            if r.user_id == user_id:
                user_rating = r.rating
        else:
            user_rating = None
        rating_nums.append(r.rating)
    avg_rating = float(sum(rating_nums))/len(rating_nums)

    # Prediction code: only predict if the user hasn't rated it.
    prediction = None
    if user_id:
        user = session.query(User).get(user_id)
        if not user_rating:
            prediction = user.predict_rating(movie)
            effective_rating = prediction
        else:
            effective_rating = user_rating

    the_eye = session.query(User).filter_by(email="theeye@ofjudgement.com").one()
    eye_rating = session.query(Rating).filter_by(user_id=the_eye.id, movie_id=movie.id).first()

    if not eye_rating:
        eye_rating = the_eye.predict_rating(movie)
    else:
        eye_rating = eye_rating.rating

    difference = abs(eye_rating - effective_rating)

    messages = [ "I suppose you don't have such bad taste after all.",
             "I regret every decision that I've ever made that has brought me to listen to your opinion.",
             "Words fail me, as your taste in movies has clearly failed you.",
             "That movie is great. For a clown to watch. Idiot."]

    beratement = messages[int(difference)]
    print eye_rating
    print effective_rating
    print difference
    return avg_rating, user_rating, prediction, beratement

def main():
    """In case we need this for something"""
    pass

if __name__ == "__main__":
    main()
