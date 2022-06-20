
from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from models import *
from schemas import movies_schema, movie_schema, directors_schema, director_schema


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
app.config['RESTX_JSON'] = {'ensure_ascii': False, 'indent': 2}
db = SQLAlchemy(app)

api = Api(app)
movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')


@movie_ns.route('/')
class MoviesView(Resource):
    def get(self):
        #       all_movies = db.session.query(Movie).all()
        movie_modific = db.session.query(Movie.id, Movie.title, Movie.description, Movie.rating, Movie.year,
                                         Movie.trailer, Genre.name.label('genre'),
                                         Director.name.label('director')).join(Genre).join(Director)

        director_id = request.args.get('director_id')
        genre_id = request.args.get('genre_id')
        if director_id:
            """ представление возвращает только фильмы с определенным режиссером по запросу 
            типа /movies/?director_id=1. """
            movie_modific = movie_modific.filter(Movie.director_id == director_id)

        if genre_id:
            """ представление возвращает только фильмы определенного жанра  по запросу типа /movies/?genre_id=1."""
            movie_modific = movie_modific.filter(Movie.genre_id == genre_id)

        all_movies = movie_modific.all()  # возвращает список всех фильмов с учетом фильтров
        return movies_schema.dump(all_movies), 200

    def post(self):
        """ Создание нового объекта в таблице Movie"""
        reg_json = request.json
        new_movie = Movie(**reg_json)
        with db.session.begin():
            db.session.add(new_movie)
        return f"Новый объект с id {new_movie.id} создан", 201


@movie_ns.route('/<int:uid>')
class MovieView(Resource):
    def get(self, uid):
        """ Вывод информации о фильме по id."""
        #       movie = db.session.query(Movie).get(uid)
        movie = db.session.query(Movie.id, Movie.title, Movie.description, Movie.rating, Movie.trailer,
                                 Genre.name.label('genre'), Movie.year,
                                 Director.name.label('director')).join(Genre).join(Director).filter(
            Movie.id == uid).first()
        if movie is None:
            return "Такой фильм не найден", 404
        return movie_schema.dump(movie), 200

    def patch(self, uid):
        """ Частичное изменение информации о фильме. """
        movie = db.session.query(Movie).get(uid)
        if movie is None:
            return "Такой фильм не найден", 404
        reg_json = request.json
        if 'title' in reg_json:
            movie.title = reg_json['title']
        if 'description' in reg_json:
            movie.description = reg_json['description']
        if 'rating' in reg_json:
            movie.rating = reg_json['rating']
        if 'trailer' in reg_json:
            movie.trailer = reg_json['trailer']
        if 'year' in reg_json:
            movie.year = reg_json['year']
        if 'genre_id' in reg_json:
            movie.genre_id = reg_json['genre_id']
        if 'director_id' in reg_json:
            movie.director_id = reg_json['director_id']
        db.session.add(movie)
        db.session.commit()
        return f"объект с id {movie.id} частично изменен", 204

    def put(self, uid):
        """ Полное изменение информации о фильме. """

        movie = db.session.query(Movie).get(uid)
        if movie is None:
            return "Такой фильм не найден", 404

        reg_json = request.json
        movie.title = reg_json['title']
        movie.description = reg_json['description']
        movie.rating = reg_json['rating']
        movie.trailer = reg_json['trailer']
        movie.year = reg_json['year']
        movie.genre_id = reg_json['genre_id']
        movie.director_id = reg_json['director_id']
        db.session.add(movie)
        db.session.commit()
        return f"объект с id {movie.id} полностью изменен", 204

    def delete(self, uid):
        """ Удаление фильма по id. """
        movie = db.session.query(Movie).get(uid)
        if movie is None:
            return "Такой фильм не найден", 404
        db.session.delete(movie)
        db.session.commit()
        return f"объект с id {movie.id} удален", 204


@director_ns.route('/')
class DirectorsView(Resource):
    def get(self):
        """ Вывод всех режиссеров"""
        all_directors = db.session.query(Director).all()
        return directors_schema.dump(all_directors), 200


@director_ns.route('/<int:uid>')
class DirectorView(Resource):
    def get(self, uid):
        """ Вывод списка фильмов режиссера по id"""
        director = db.session.query(Director).get(uid)
        if director is None:
            return "Такой режиссер не найден", 404
#        return director_schema.dump(director), 200
        movie_by_direc = db.session.query(Movie.title).filter(Movie.director_id == uid).all()
        return f' режиссер {director.name} снял фильмы: {movie_by_direc} ', 200


if __name__ == '__main__':
    app.run(debug=True)
