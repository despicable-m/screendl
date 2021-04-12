from django.db import models
from django.core.validators import URLValidator


class Movie(models.Model):
    """ Movies table"""
    original_title = models.TextField(blank=True)
    movie_title = models.TextField(blank=True)
    release_date = models.DateField()
    FHD_link = models.TextField(validators=[URLValidator()], blank=True)
    UHD_link = models.TextField(validators=[URLValidator()], blank=True)
    HD_link = models.TextField(validators=[URLValidator()], blank=True)
    SD_link = models.TextField(validators=[URLValidator()], blank=True)
    UHD_size = models.BigIntegerField(null=True)
    FHD_size = models.BigIntegerField(null=True)
    HD_size = models.BigIntegerField(null=True)
    SD_size = models.BigIntegerField(null=True)
    poster_path = models.CharField(max_length=255, null=True)
    synopsis = models.TextField(blank=True)
    movie_id = models.CharField(max_length=255, null=True)
    back_drop = models.CharField(max_length=255, null=True)

    def __str__(self) -> str:
        return self.movie_title