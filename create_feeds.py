import os
import json

import swbi_parser

gh_pages_url = 'https://thenaildev.github.io/openmensa-bielefeld/'

swbi_locations = [
    ('bielefeld_mensa-x', 'https://www.studierendenwerk-bielefeld.de/essen-trinken/speiseplan/bielefeld/mensa-x/gggg'),
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
        meta_filename = f'{feed_directory_name}/meta_{location[0]}.xml'
        try:
            feed = swbi_parser.parse_mensa_plan(location[1])
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(feed)
            meta_feed = generate_meta_feed(gh_pages_url + filename, location[1])
            with open(meta_filename, 'w', encoding='utf-8') as f:
                f.write(meta_feed)
            mensa_listing[location[0]] = gh_pages_url + meta_filename
            print(f'Created feed {location[0]}')
        except Exception as e:
            if 'HTTP Error' in str(e):
                print(f'Fatal HTTP error encountered at {location[0]}: {e}')
                raise
            print(f'Exception during generation of feed {location[0]}: {e}')
    # Generate the index.json containing all feeds
    with open(f'{feed_directory_name}/index.json', 'w', encoding='utf-8') as f:
        json.dump(mensa_listing, f)
        print('Created index.json')

def generate_meta_feed(feed_url: str, source_url: str):
    meta_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<openmensa version="2.1"\n'
        '           xmlns="http://openmensa.org/open-mensa-v2"\n'
        '           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n'
        '           xsi:schemaLocation="http://openmensa.org/open-mensa-v2 http://openmensa.org/open-mensa-v2.xsd">\n'
        '  <canteen>\n'
        '    <feed name="full">\n'
        '      <schedule hour="6" retry="60 5 1440" />\n'
        f'      <url>{feed_url}</url>\n'
        f'      <source>{source_url}</source>\n'
        '    </feed>\n'
        '  </canteen>\n'
        '</openmensa>'
    )
    return meta_xml

if __name__ == '__main__':
    create_feeds()
