from re import S
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib.parse
from django.core.exceptions import ObjectDoesNotExist
import csv
import PTN
import requests
from typing import List, Union
import json

from moviedl.models import Movie

# The Movie Data Base api key
tmdb_API_KEY = 'TMDb API KEY GOES HERE'

# Chromedriver path
PATH = "C:\Program Files (x86)\chromedriver.exe"
driver = webdriver.Chrome(PATH)

def scrape():
    """Scrapes websites"""

    # links to be scrapped go here
    sites = [
        "http://103.91.144.230/ftpdata/Movies/Hollywood/2000_2005/",
        "http://103.91.144.230/ftpdata/Movies/Hollywood/",
        "http://103.91.144.230/ftpdata/Movies/",
        "https://my.dlactmovie.ir/animation/",
        "https://my.dlactmovie.ir/film/",
        "http://103.222.20.150/ftpdata/Movies",
    ]

    # Scrapes websites based on the number of 
    for i in range(len(sites)):
        driver.get(sites[i])
        links = driver.find_elements_by_tag_name('a')

        link_index = 0
        page_num = 0
        page_el = {}
        videos = [".3g2", ".3gp", ".asf", ".asx", ".avi", ".flv", \
                                ".m2ts", ".mkv", ".mov", ".mp4", ".mpg", ".mpeg", \
                                ".rm", ".swf", ".vob", ".wmv"]
        page_el['page'+str(page_num)] = {
                    'num_el': len(links),
                    'index_clicked': link_index
                }

        while (True):
            try:
                element = WebDriverWait(driver, 1000).until(
                EC.element_to_be_clickable((By.TAG_NAME, "a"))
            )
            finally:

                if page_num < 0:
                        break
                else:
                    index_clicked = page_el['page'+str(page_num)]['index_clicked']
                    num_el = page_el['page'+str(page_num)]['num_el']

                try:
                    if '../' not in links[index_clicked].text:
                        
                        # Clicks on directories to move to next page
                        if links[index_clicked].get_attribute('href').endswith('/'):
                            page_el['page'+str(page_num)]['num_el'] = page_el['page'+str(page_num)]['num_el'] - 1
                            links[index_clicked].click()

                            #updates page number to next page
                            page_num = page_num + 1
                            links = driver.find_elements_by_tag_name('a')

                            # Adds next page data to page elements dictionary
                            page_el['page'+str(page_num)] = {
                                'num_el': len(links),
                                'index_clicked': link_index
                            }
                        
                        # determines whether the link has a video and copies url
                        elif links[index_clicked].get_attribute('href').endswith(tuple(videos)):
                            sort_data(links[index_clicked].get_attribute('href'))
                            page_el['page'+str(page_num)]['index_clicked'] = 0
                            index_clicked = page_el['page'+str(page_num)]['index_clicked']
                            
                            driver.back()
                            page_num = page_num - 1

                            # Returns number of directory left to be scanned.
                            page_el['page'+str(page_num)]['num_el'] = page_el['page'+str(page_num)]['num_el'] - 1
                            links = driver.find_elements_by_tag_name('a')

                            while(True):
                                # Updates the most recently clicked element on the page
                                page_el['page'+str(page_num)]['index_clicked'] = page_el['page'+str(page_num)]['index_clicked'] + 1
                                index_clicked = page_el['page'+str(page_num)]['index_clicked']
                                num_el = page_el['page'+str(page_num)]['num_el']

                                # Continues page if the current WebElement is not a video
                                if not links[index_clicked].get_attribute('href').endswith(tuple(videos)):

                                    # Clicks on WebElement to move to the next page if current WebElement is another directory.
                                    if links[index_clicked].get_attribute('href').endswith('/'):
                                        links[index_clicked].click()
                                        page_el['page'+str(page_num)]['num_el'] = page_el['page'+str(page_num)]['num_el'] - 1
                                        page_num = page_num + 1

                                        page_el['page'+str(page_num)] = {
                                            'num_el': len(links),
                                            'index_clicked': link_index
                                        }

                                        links = driver.find_elements_by_tag_name('a')
                                        index_clicked = page_el['page'+str(page_num)]['index_clicked']


                                    if not page_el['page'+str(page_num)]['num_el'] <= 1:
                                        if '../' not in links[index_clicked].text:
                                            if links[index_clicked].get_attribute('href').endswith('/'):
                                                links[index_clicked].click()
                                                page_el['page'+str(page_num)]['num_el'] = page_el['page'+str(page_num)]['num_el'] - 1
                                                links = driver.find_elements_by_tag_name('a')
                                            elif links[index_clicked].get_attribute('href').endswith(tuple(videos)):
                                                sort_data(links[index_clicked].get_attribute('href'))
                                                driver.back()
                                                page_el['page'+str(page_num)]['num_el'] = page_el['page'+str(page_num)]['num_el'] - 1
                                                page_el['page'+str(page_num)]['index_clicked'] = page_el['page'+str(page_num)]['index_clicked'] + 1
                                                links = driver.find_elements_by_tag_name('a')
                                            else:
                                                page_el['page'+str(page_num)]['index_clicked'] = page_el['page'+str(page_num)]['index_clicked'] + 1
                                        else:
                                            page_el['page'+str(page_num)]['num_el'] = page_el['page'+str(page_num)]['num_el'] - 1
                                    else:
                                        driver.back()
                                        page_num = page_num - 1
                                        links = driver.find_elements_by_tag_name('a')
                                        break

                                # Copies link and data if file is current WelbElement is a link to a video file.
                                else:

                                    # Copies and breaks the video scanning loop if all video files' link have been copied.
                                    if num_el <= 1:
                                        sort_data(links[index_clicked].get_attribute('href'))
                                        driver.back()
                                        page_num = page_num - 1
                                        if page_num < 0:
                                            break
                                        else:
                                            page_el['page'+str(page_num)]['index_clicked'] = page_el['page'+str(page_num)]['index_clicked'] + 1
                                            links = driver.find_elements_by_tag_name('a')
                                        break

                                    # Copies video files' link
                                    else:
                                        sort_data(links[index_clicked].get_attribute('href'))
                                        page_el['page'+str(page_num)]['num_el'] = page_el['page'+str(page_num)]['num_el'] - 1
                                        num_el = page_el['page'+str(page_num)]['num_el']
                                        if num_el < 1:
                                            page_el['page'+str(page_num)]['index_clicked'] = 0
                                            driver.back()
                                            page_num = page_num - 1
                                            page_el['page'+str(page_num)]['index_clicked'] = page_el['page'+str(page_num)]['index_clicked'] + 1
                                            links = driver.find_elements_by_tag_name('a')
                                        
                        else:
                            page_el['page'+str(page_num)]['index_clicked'] = page_el['page'+str(page_num)]['index_clicked'] + 1
                    else:
                        page_el['page'+str(page_num)]['index_clicked'] = page_el['page'+str(page_num)]['index_clicked'] + 1
                    
                except(IndexError):
                    driver.back()
                    page_num = page_num - 1
                    links = driver.find_elements_by_tag_name('a')
                    if page_num < 0:
                        break
                    else:
                        page_el['page'+str(page_num)]['index_clicked'] = page_el['page'+str(page_num)]['index_clicked'] + 1
    driver.close()


# def to_csv(data):
#     """Adds data scraped to CSV file"""
#     file = data.split("/")

#     default_movie_data = {
#         'year': 'unknown',
#         'resolution': 'HD',
#         'title': '',
#         'url': data
#         }

#     # Picks the name of the file from the url
#     to_name = urllib.parse.unquote(file[-1])

#     # Uses PTN to extract media information from torrent-like filename
#     extracted_data = PTN.parse(to_name)
#     print(extracted_data)

#     # Gets size of file in B

#     response = requests.head(data, allow_redirects=True)
#     size = response.headers.get('content-length', 0)
    
#     # Converts file size to megabytes
#     print(HumanBytes.format(int(size), True, precision=2))

#     # Replaces all default movie data
#     for key, value in extracted_data.items():
#         if key in default_movie_data:
#             default_movie_data[key] = value

#     get_movie_info(default_movie_data["title"], default_movie_data["year"])

#     # Adds relevant data to CSV file
#     with open('movies.csv', 'a+', newline='') as csvfile:
#         fieldnames = ['title', 'year', 'resolution', 'url']
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

#         writer.writerow(
#             {
#                 'title': default_movie_data['title'],
#                 'year': default_movie_data['year'],
#                 'resolution': default_movie_data['resolution'],
#                 'url': data 
#                 }
#             )


def get_movie_info(movie_name, movie_year):
    """Searches movie databases for movies"""
    if movie_year != 'unknown':
        url = f"https://api.themoviedb.org/3/search/movie?api_key={tmdb_API_KEY}&query={movie_name}&page=1&year={movie_year}"
    else:
        url = f"https://api.themoviedb.org/3/search/movie?api_key={tmdb_API_KEY}&query={movie_name}&page=1"
    response = requests.get(url)
    result = response.json()

    # Return received data from movie database
    return result


def sort_data(data):
    """ Cleans movie data to be save to database """
    file = data.split("/")

    default_movie_data = {
        'year': 'unknown',
        'resolution': 'HD',
        'title': '',
        'url': data,
        'size_in_bytes': 3
        }

    # Picks the name of the file from the url
    to_name = urllib.parse.unquote(file[-1])

    # Uses PTN to extract media information from torrent-like filename
    extracted_data = PTN.parse(to_name)

    # Gets size of file in B
    response = requests.head(data, allow_redirects=True)
    size = response.headers.get('content-length', 0)
    default_movie_data["size_in_bytes"] = size

    # Replaces all default movie data
    for key, value in extracted_data.items():
        if key in default_movie_data:
            default_movie_data[key] = value

    # Gets movie info from a movie database
    movie_detail = get_movie_info(default_movie_data["title"], default_movie_data["year"])
    
    
    save_to_database(movie_detail['results'][0], default_movie_data)

def save_to_database(data, file):
    """ Saves movie data to database """

    RESOLUTION = {
        '1080p': 'FHD',
        '720p': 'HD',
        '480p': 'SD',
        'HD': 'HD',
        '2160p': 'UHD'
    }
    
    resolution = file['resolution']

    try:
        movie_info = {
            "original_title": data["original_title"],
            "movie_title": data['title'],
            "release_date": data["release_date"],
            "poster_path": data["poster_path"],
            "back_drop": data["backdrop_path"],
            "synopsis": data["overview"],
            "movie_id": "tmdb_"+str(data["id"]),
            str(RESOLUTION[resolution])+'_link': file['url'],
            str(RESOLUTION[resolution])+'_size': file['size_in_bytes']
        }

    except KeyError:
        movie_info = {
            "original_title": data["original_title"],
            "movie_title": data['title'],
            "release_date": data["release_date"],
            "poster_path": data["poster_path"],
            "back_drop": data["backdrop_path"],
            "synopsis": data["overview"],
            "movie_id": "tmdb_"+str(data["id"]),
            "HD_link": file['url'],
            "HD_size": file['size_in_bytes']
        }
    # print('DEFAULT:   ', movie_info['original_title'])

    try:
        movie = Movie.objects.filter(movie_id=movie_info["movie_id"]).values()
        if len(movie) == 0:
            try:
                data_to_save = Movie.objects.create(**{
                    "movie_title":movie_info["movie_title"],
                    "original_title":movie_info["original_title"],
                    "release_date":movie_info["release_date"],
                    str(RESOLUTION[resolution])+'_link': file['url'],
                    str(RESOLUTION[resolution])+'_size': file['size_in_bytes'],
                    "back_drop":movie_info["back_drop"],
                    "synopsis":movie_info["synopsis"],
                    "movie_id":movie_info["movie_id"],
                    "poster_path":movie_info["poster_path"]
                })
                data_to_save.save()
            except KeyError:
                data_to_save = Movie.objects.create(**{
                    "movie_title":movie_info["movie_title"],
                    "original_title":movie_info["original_title"],
                    "release_date":movie_info["release_date"],
                    'HD_link': file['url'],
                    'HD_size': file['size_in_bytes'],
                    "back_drop":movie_info["back_drop"],
                    "synopsis":movie_info["synopsis"],
                    "movie_id":movie_info["movie_id"],
                    "poster_path":movie_info["poster_path"]
                })
                data_to_save.save()
        else:              
            for key, value in movie[0].items():
                if movie[0][key] == None or movie[0][key] == '':
                    if key in movie_info:
                        Movie.objects.filter(pk=movie[0]["id"]).update(**{key:movie_info[key]})

    except ObjectDoesNotExist as DoesNotExist:
        data_to_save = Movie.objects.create(**{
            "movie_title":movie_info["movie_title"],
            "original_title":movie_info["original_title"],
            "release_date":movie_info["release_date"],
            str(RESOLUTION[resolution])+'_link': file['url'],
            str(RESOLUTION[resolution])+'_size': file['size_in_bytes'],
            "back_drop":movie_info["back_drop"],
            "synopsis":movie_info["synopsis"],
            "movie_id":movie_info["movie_id"],
            "poster_path":movie_info["poster_path"]
        })     
        data_to_save.save()   


# Handles conversion of file size from bytes
# Got it from https://stackoverflow.com/a/63839503/13821926
class HumanBytes:
    METRIC_LABELS: List[str] = ["B", "kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
    BINARY_LABELS: List[str] = ["B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"]
    PRECISION_OFFSETS: List[float] = [0.5, 0.05, 0.005, 0.0005] # PREDEFINED FOR SPEED.
    PRECISION_FORMATS: List[str] = ["{}{:.0f} {}", "{}{:.1f} {}", "{}{:.2f} {}", "{}{:.3f} {}"] # PREDEFINED FOR SPEED.

    @staticmethod
    def format(num: Union[int, float], metric: bool=False, precision: int=1) -> str:
        """
        Human-readable formatting of bytes, using binary (powers of 1024)
        or metric (powers of 1000) representation.
        """

        assert isinstance(num, (int, float)), "num must be an int or float"
        assert isinstance(metric, bool), "metric must be a bool"
        assert isinstance(precision, int) and precision >= 0 and precision <= 3, "precision must be an int (range 0-3)"

        unit_labels = HumanBytes.METRIC_LABELS if metric else HumanBytes.BINARY_LABELS
        last_label = unit_labels[-1]
        unit_step = 1000 if metric else 1024
        unit_step_thresh = unit_step - HumanBytes.PRECISION_OFFSETS[precision]

        is_negative = num < 0
        if is_negative: # Faster than ternary assignment or always running abs().
            num = abs(num)

        for unit in unit_labels:
            if num < unit_step_thresh:
                # VERY IMPORTANT:
                # Only accepts the CURRENT unit if we're BELOW the threshold where
                # float rounding behavior would place us into the NEXT unit: F.ex.
                # when rounding a float to 1 decimal, any number ">= 1023.95" will
                # be rounded to "1024.0". Obviously we don't want ugly output such
                # as "1024.0 KiB", since the proper term for that is "1.0 MiB".
                break
            if unit != last_label:
                # We only shrink the number if we HAVEN'T reached the last unit.
                # NOTE: These looped divisions accumulate floating point rounding
                # errors, but each new division pushes the rounding errors further
                # and further down in the decimals, so it doesn't matter at all.
                num /= unit_step

        return HumanBytes.PRECISION_FORMATS[precision].format("-" if is_negative else "", num, unit)

# if __name__ == '__main__':
    scrape()