import os
import json

import swbi_parser

gh_pages_url = 'https://thenaildev.github.io/openmensa-bielefeld/'

swbi_locations = [
    ('bielefeld_mensa-x', 'https://www.studierendenwerk-bielefeld.de/essen-trinken/speiseplan/bielefeld/mensa-x/'),
    ('detmold_mensa-hfm', 'https://www.studierendenwerk-bielefeld.de/essen-trinken/speiseplan/detmold/mensa-hfm/'),
    ('detmold_mensa-th-owl', 'https://www.studierendenwerk-bielefeld.de/essen-trinken/speiseplan/mensa-th-owl/'),
    ('hoexter_mensa-th-owl', 'https://www.studierendenwerk-bielefeld.de/essen-trinken/speiseplan/hoexter/mensa-th-owl/'),
    ('lemgo_mensa-th-owl', 'https://www.studierendenwerk-bielefeld.de/essen-trinken/speiseplan/lemgo/mensa-th-owl/'),
    ('minden_mensa-hsbi', 'https://www.studierendenwerk-bielefeld.de/essen-trinken/speiseplan/minden/mensa-hsbi/')
]

def create_feeds():
    mensa_listing = {}
    feed_directory_name = 'feeds'
    if not os.path.isdir(feed_directory_name):
        os.mkdir(feed_directory_name)
    # Generate xml feeds using the swbi_parser
    for location in swbi_locations:
        filename = f'{feed_directory_name}/{location[0]}.xml'
        try:
            feed = swbi_parser.parse_mensa_plan(location[1])
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(feed)
            mensa_listing[location[0]] = gh_pages_url + filename
            print(f'Created feed {location[0]}')
        except Exception as e:
            print(f'Exception during generation of feed {location[0]}: {e}')
    # Generate the index.json containing all feeds
    with open(f'{feed_directory_name}/index.json', 'w', encoding='utf-8') as f:
        json.dump(mensa_listing, f)
        print('Created index.json')

if __name__ == '__main__':
    create_feeds()
