from urllib.request import urlopen
from bs4 import BeautifulSoup
from pprint import pprint
from collections import Counter, defaultdict
import re
import pandas as pd
from tqdm import tqdm

BASE_URL = 'https://www.rottentomatoes.com'
REVIEW_TYPE_URLS = {
    'All Critics': '',
    'Top Critics': '?type=top_critics',
    'All Audience': '?type=user',
    'Verified Audience': '?type=verified_audience'
}
BEST_MOVIES = 'https://www.rottentomatoes.com/top/bestofrt'
WORST_MOVIES = 'https://editorial.rottentomatoes.com/guide/worst-movies-of-all-time/'


def get_best_movie_ids(num=20):
    soup = BeautifulSoup(urlopen(BEST_MOVIES), 'html5lib')
    # table = soup.find_all('section', {'id': 'top_movies_main'}, recursive=True)

    movies = soup.find_all('a', {'href': re.compile(r'^/m/*')})
    movie_ids = set()
    for movie in movies:
        if movie['href'].split('/')[-1] != '':
            movie_ids.add(movie['href'].split('/')[-1])
    return list(movie_ids)[:num]


def get_worst_movie_ids(url, num=20):
    soup = BeautifulSoup(urlopen(WORST_MOVIES), 'html5lib')

    movies = soup.find_all('div', {'class', 'article_movie_title'})

    movie_ids = set()
    for movie in movies:
        movie_tag = movie.find('a', {'href': re.compile(r'^https://www.rottentomatoes.com/m/')})
        if movie_tag['href'].split('/')[-1] != '':
            movie_ids.add(movie_tag['href'].split('/')[-1])
    return list(movie_ids)[:num]


def get_movie_reviews(movie_id, review_type):
    if review_type not in REVIEW_TYPE_URLS.keys():
        raise ValueError('review type is invalid')

    review_url = f'{BASE_URL}/m/{movie_id}/reviews{REVIEW_TYPE_URLS[review_type]}'
    soup = BeautifulSoup(urlopen(review_url), 'lxml')

    # get the rating of the movie
    source = get_source(review_type)
    ratings = get_rating(soup, source)
    ratings_binary = get_binary_rating(ratings, source)
    review_texts = get_review_text(soup, source)
    stripped_review_texts = [review_text.strip() for review_text in review_texts]

    movie_info = {
        'movie_ids': [movie_id for _ in range(len(ratings))],
        'source': [source for _ in range(len(ratings))],
        'ratings': ratings,
        'ratings_binary': ratings_binary,
        'review_texts': stripped_review_texts
    }

    return movie_info


def get_rating(review_data, source):
    reviews_movie = review_data.find('div', {'class': 'reviews-movie'})
    if source == 'critics':
        ratings = reviews_movie.find_all('div', {'class': 'review_icon'})
        # extract fresh or rotten
        fresh_or_rottens = [rating['class'][-1] for rating in ratings]
        return fresh_or_rottens

    else:
        star_displays = reviews_movie.find_all('span', {'class': 'star-display'})
        ratings = []
        for star_display in star_displays:
            stars = star_display.find_all()
            stars = [star['class'][0].split('__')[-1] for star in stars]
            star_count = Counter(stars)
            ratings.append(star_count['filled'] + star_count['half'] * 0.5)

        return ratings


def get_source(review_type):
    if review_type in ['All Critics', 'Top Critics']:
        return 'critics'
    return 'audience'


def get_binary_rating(ratings, source):
    if source == 'critics':
        return ['p' if rating == 'fresh' else 'n' for rating in ratings]
    return ['n' if rating < 3.0 else 'p' for rating in ratings]


def get_review_text(review_data, source):
    if source == 'critics':
        reviews = review_data.find_all('div', {'class', 'the_review'})
        return [review.get_text() for review in reviews]
    else:
        reviews = review_data.find_all('p', {'class': 'audience-reviews__review'})
        return [review.get_text() for review in reviews]


def generate_data():
    movie_list = get_best_movie_ids(num=40) + get_worst_movie_ids(num=40)
    data_dict = defaultdict(lambda: [])

    for movie_id in tqdm(movie_list):
        for review_type in ['All Critics', 'All Audience']:
            movie_reviews = get_movie_reviews(movie_id, review_type)
            data_dict['movie_ids'] += movie_reviews['movie_ids']
            data_dict['sources'] += movie_reviews['source']
            data_dict['ratings'] += movie_reviews['ratings']
            data_dict['ratings_binary'] += movie_reviews['ratings_binary']
            data_dict['review_texts'] += movie_reviews['review_texts']

    df = pd.DataFrame(data_dict)
    df.to_csv('../data/dataset.csv', encoding='utf-8')


if __name__ == '__main__':
    # pprint(get_reviews('nomadland', 'All Critics'))

    generate_data()
