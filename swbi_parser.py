import urllib.request
import datetime

from bs4 import BeautifulSoup
from pyopenmensa.feed import LazyBuilder

def parse_mensa_plan(url: str):
    soup = None
    with urllib.request.urlopen(url) as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    if soup is None:
        raise Exception(f'Could not read from url {url}')
    
    menuDays = soup.find_all('div', class_='menuDay')
    
    canteen = LazyBuilder()
    
    for menuDay in menuDays:
        # dates are formatted as YYYYMMDD, eg 20230401 for April 1st 2023
        date_string = menuDay['data-selector']
        date = datetime.datetime.strptime(date_string, '%Y%m%d').date()
        #print(date)
        menuItems = menuDay.find_all('div', class_='menuItem')
        for menuItem in menuItems:
            notes = []
            if 'menuItem--sidedish' in menuItem['class']:
                # Sidedishes dont have their category stated on the page
                category = 'Beilage'
                notes += [ label.string.strip() for label in menuItem.find_all('strong', class_='menuItem__sidedish__label') ]
            else:
                category = menuItem.find('span', class_='menuItem__line').string.strip()
                menuItemText = menuItem.find('p', class_='menuItem__text').string
                if menuItemText is not None:
                    # Some menu items might have an empty text
                    notes += [ menuItemText.strip() ]
            
            name = menuItem.find('h3', class_='menuItem__headline').string.strip()
            
            prices = {}
            price_1 = menuItem.find('p', class_='menuItem__price__one')
            if price_1 is not None:
                prices['student'] = price_1.find('span', type='button').string.strip()
            price_2 = menuItem.find('p', class_='menuItem__price__two')
            if price_2 is not None:
                prices['employee'] = price_2.find('span', type='button').string.strip()
            price_3 = menuItem.find('p', class_='menuItem__price__three')
            if price_3 is not None:
                prices['other'] = price_3.find('span', type='button').string.strip()
            
            canteen.addMeal(date, category, name, prices=prices, notes=notes)
        
    return canteen.toXMLFeed()

if __name__ == '__main__':
    # For debug purposes do parsing for Bielefeld Mensa X
    xml_feed = parse_mensa_plan('https://www.studierendenwerk-bielefeld.de/essen-trinken/speiseplan/bielefeld/mensa-x/')
    print(xml_feed)

