import model
import csv
import datetime


def load_users(session):
    f= open('seed_data/u.user')
    lines = f.readlines()
    for line in lines:
        user = line.split("|")
        zipcode = user[4].strip()
        new_user = model.User(id = user[0], age=user[1], zipcode=zipcode)    
        session.add(new_user)
    session.commit()
    f.close()

def load_movies(session):
    f = open('seed_data/u.item')
    lines = f.readlines()
    for line in lines:
        movie = line.split("|")
        title = movie[1]
        title = title.decode("latin-1")
        movie_tokens = title.split()
        movie_title = movie_tokens[:-1]
        final_movie_title = " ".join(movie_title)

        if movie[2] != "":
            release_date = datetime.datetime.strptime(movie[2], '%d-%b-%Y')
        else:
            release_date = None

        new_movie = model.Movie(id=movie[0], name = final_movie_title, release_date=release_date, imdb_url=movie[4])
        session.add(new_movie)
    session.commit()
    f.close()

def load_ratings(session):
    f = open('seed_data/u.data')
    lines = f.readlines()
    for line in lines:
        rating = line.split()

        new_rating = model.Rating(movie_id=rating[1], user_id=rating[0], rating=rating[2].strip())
        session.add(new_rating)
        
    session.commit()
    f.close()

def main(session):
    # You'll call each of the load_* functions with the session as an argument
    session = model.connect()
    # load_users(session)
    # print "loaded users"
    load_movies(session)
    print "loaded movies"
    load_ratings(session)
    print "loaded ratings"

if __name__ == "__main__":
    s= model.connect()
    main(s)
