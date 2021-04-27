from os import environ
import os
from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets, generics, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Movie
from .serializers import MovieSerializer
import requests
from rest_framework.authtoken.models import Token


tmdb_API_KEY = environ['tmdb_api_key']


def get_popular():
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={tmdb_API_KEY}&language=en-US&page=1"
    result = requests.get(url)
    to_check = result.json()["results"]
    
    movie_id = []
    for i in to_check:
        the_id = f"tmdb_{i['id']}"
        movies = Movie.objects.all()
        for i in movies:
            if the_id in i.movie_id:
                movie_id.append(the_id)
    return movie_id


def get_recommendation(tmdb_id):
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/recommendations?api_key={tmdb_API_KEY}&language=en-US&page=1"
    result = requests.get(url)
    to_check = result.json()['results']
    movie_id = []
    for i in to_check:
        the_id = f"tmdb_{i['id']}"
        movies = Movie.objects.all()
        for i in movies:
            if the_id in i.movie_id:
                movie_id.append(the_id)
    return movie_id


# Create your views here.
class MovieViewSet(viewsets.ViewSet):
    def list(self, request):
        print(tm)

        movies = Movie.objects.order_by('-id')[:10]
        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Movie.objects.all()
        movie = get_object_or_404(queryset, pk=pk)
        serializer = MovieSerializer(movie)
        return Response(serializer.data)


class MovieAPIView(generics.ListCreateAPIView):
    search_fields = ['movie_title', 'original_title', 'release_date']
    filter_backends = (filters.SearchFilter,)
    queryset = Movie.objects.all().order_by('-release_date')
    serializer_class = MovieSerializer


class PopularView(generics.ListCreateAPIView):
    movies = []
    movie_list = get_popular()
    for movie in movie_list:
        m = Movie.objects.filter(movie_id=movie)
        for i in m:
            movies.append(i)

    queryset = movies
    serializer_class = MovieSerializer


class RecommendView(APIView):
    def get(self, request, **kwargs):
        tmdb_id = self.kwargs["tmdb_id"]
        tmdb_id = tmdb_id.split('_')
        tmdb_id = tmdb_id[1]
        movies = []
        movie_list = get_recommendation(tmdb_id)
        for movie in movie_list:
            m = Movie.objects.filter(movie_id=movie)
            for i in m:
                movies.append(i)

        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data)