from django.shortcuts import render
from .models import Movie
from django.http import HttpResponse

# Create your views here.
def index(request):
    print(len(Movie.objects.all()))

    return HttpResponse('Hello there')