from urllib.request import urlopen
from bs4 import BeautifulSoup

BASE_URL = 'https://www.rottentomatoes.com'
REVIEW_TYPE_URLS = {
    'All Critics': '',
    'Top Critics': '?type=top_critics',
    'All Audience': '?type=user',
    'Verified Audience': '?type=verified_audience'
}


def get_reviews(movie_id, review_type):
    if review_type not in REVIEW_TYPE_URLS.keys():
        raise ValueError('review type is invalid')

    review_url = f'{BASE_URL}/m/{movie_id}/reviews?type={REVIEW_TYPE_URLS[review_type]}'
    soup = BeautifulSoup(urlopen(review_url), 'html.parser')

    # get the rating of the movie
    source = get_source(review_type)
    rating = get_rating(soup, review_type)
    rating_binary = get_binary_rating(rating)
    review_text = get_review_text(soup)

    return source


def get_rating(review_data, review_type):
    pass


def get_source(review_type):
    if review_type in ['All Critics', 'Top Critics']:
        return 'critics'
    return 'audience'


def get_binary_rating(rating):
    pass


def get_review_text(review_data):
    pass


if __name__ == '__main__':
    print(get_reviews('nomadland', 'All Critics'))
