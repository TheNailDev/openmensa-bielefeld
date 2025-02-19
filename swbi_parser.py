import urllib.request
import datetime

from bs4 import BeautifulSoup
from pyopenmensa.feed import LazyBuilder

def _remove_multiple_whitespaces(s: str):
    return ' '.join(s.split()).strip()

def parse_mensa_plan(url: str):
    canteen = LazyBuilder()
    
    # updates canteen with data of current week
    # the data of the current week is necessary
    # thus, if an error occurs, parsing for this mensa is cancelled (by propagating the error)
    canteen = update_canteen(canteen, url)
    
    # try to get canteen data for next week
    # data for the next week is available by appending 'nächste-woche' to the url
    # The 'ä' in this appendix needs to be escaped as '%c3%a4'
    # if an error occurs during parsing, the program will continue without next weeks data
    if url[-1] != '/':
        url += '/'
    next_week_url = url
    next_week_url += 'n%c3%a4chste-woche/'
    try:
        canteen = update_canteen(canteen, next_week_url)
    except Exception as e:
        print(f'Could not load next week data for {url}')
        print(f'Exception: {e}')
    
    return canteen.toXMLFeed()

def update_canteen(canteen, url: str):
    soup = None
    with urllib.request.urlopen(url) as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    if soup is None:
        raise Exception(f'Could not read from url {url}')
    
    menuDays = soup.find_all('div', class_='menuDay')
    
    for menuDay in menuDays:
        # dates are formatted as YYYYMMDD, eg 20230401 for April 1st 2023
        date_string = menuDay['data-selector']
        date = datetime.datetime.strptime(date_string, '%Y%m%d').date()
        menuItems = menuDay.find_all('div', class_='menuItem')
        for menuItem in menuItems:
            # Extract the name of the meal from the menu items headline
            name = menuItem.find('h3', class_='menuItem__headline').string
            name = _remove_multiple_whitespaces(name)
            
            # Extract the prices for the three different groups students, employees, guests (others)
            prices = {}
            price_1 = menuItem.find('p', class_='menuItem__price__one')
            if price_1 is not None:
                prices['student'] = _remove_multiple_whitespaces(price_1.find('span', type='button').string)
            price_2 = menuItem.find('p', class_='menuItem__price__two')
            if price_2 is not None:
                prices['employee'] = _remove_multiple_whitespaces(price_2.find('span', type='button').string)
            price_3 = menuItem.find('p', class_='menuItem__price__three')
            if price_3 is not None:
                prices['other'] = _remove_multiple_whitespaces(price_3.find('span', type='button').string)
            
            # Create an empty list for notes
            notes = []
            
            # Sidedishes use a different structure and need to be handled differently from other menu items
            if 'menuItem--sidedish' in menuItem['class']:
                # The category of a sidedish is stored in the headline, which usually stores the name of main dishes
                category = name
                # Every sidedish is stored in its own list element
                for sidedish in menuItem.find_all('li', class_='menuItem__sidedish'):
                    # The name of each sidedish is stored in each sidedish label
                    name = _remove_multiple_whitespaces(sidedish.find('strong', class_='menuItem__sidedish__label').string)
                    notes = []
                    # Additional info for sidedishes can be extracted from the button "Details"
                    details_a = sidedish.find('a', class_='button-outline')
                    if details_a is not None:
                        details_content = details_a['data-bs-content']
                        details_soup = BeautifulSoup(details_content, 'html.parser')
                        if details_soup is not None:
                            notes += _generate_notes_from_meal_details(details_soup)
                    # In some cases each side dish has its own price. (Mensa Aktionstheke)
                    price_1 = sidedish.find('p', class_='menuItem__price__one')
                    if price_1 is not None:
                        prices['student'] = _remove_multiple_whitespaces(price_1.find('span', type='button').string)
                    price_2 = sidedish.find('p', class_='menuItem__price__two')
                    if price_2 is not None:
                        prices['employee'] = _remove_multiple_whitespaces(price_2.find('span', type='button').string)
                    price_3 = sidedish.find('p', class_='menuItem__price__three')
                    if price_3 is not None:
                        prices['other'] = _remove_multiple_whitespaces(price_3.find('span', type='button').string)
                    canteen.addMeal(date, category, name, prices=prices, notes=notes)
            # Only handle non sidedishes when they have a price. Otherwise they are no real menu items.
            elif prices:
                category = menuItem.find('span', class_='menuItem__line').string.strip()
                menuItemText = menuItem.find('p', class_='menuItem__text').string
                if menuItemText is not None:
                    # Some menu items might have an empty text
                    notes += [ _remove_multiple_whitespaces(menuItemText) ]
                notes += _generate_notes_from_meal_details(menuItem)
                canteen.addMeal(date, category, name, prices=prices, notes=notes)
        
    return canteen

def _generate_notes_from_meal_details(details_soup):
    notes = []
    co2_footprint_span = details_soup.find('span', class_='menuItem__co2__value')
    if co2_footprint_span is not None:
        notes += [ f'CO2: {_remove_multiple_whitespaces(co2_footprint_span.string)}' ]
    additives_div = details_soup.find('div', class_='menuItem__additives')
    if additives_div is not None:
        for custombadge_span in additives_div.find_all('span', class_='custombadge'):
            notes += [ _generate_note_from_custombadge(custombadge_span) ]
    allergens_div = details_soup.find('div', class_='menuItem__allergens')
    if allergens_div is not None:
        for custombadge_span in allergens_div.find_all('span', class_='custombadge'):
            notes += [ _generate_note_from_custombadge(custombadge_span) ]
    return notes

def _generate_note_from_custombadge(custombadge):
    # each custombadge consists of two child elements.
    # the first child is the badge code, the second child is the actual description of the badge
    code = _remove_multiple_whitespaces(custombadge.contents[0].string)
    description = _remove_multiple_whitespaces(custombadge.contents[1])
    return f'{code}) {description}'

if __name__ == '__main__':
    # For debug purposes do parsing for Bielefeld Mensa X
    xml_feed = parse_mensa_plan('https://www.studierendenwerk-bielefeld.de/essen-trinken/speiseplan/bielefeld/mensa-x/')
    print(xml_feed)

