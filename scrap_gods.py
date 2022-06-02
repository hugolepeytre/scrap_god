import requests
import regex as re
import csv
from bs4 import BeautifulSoup as bS
from collections import defaultdict

site_url = 'https://www.godchecker.com/'


def main():
    session = requests.Session()
    main_page = session.get(site_url)
    main_soup = bS(main_page.content, 'html.parser')

    # Getting all pantheon pages
    main_page_urls = collect_urls(main_soup)
    pantheon_urls = unique_pantheons(filter(lambda url: '-mythology' in url, main_page_urls))
    # Modern pantheon added by hand because it is not mentioned on the front page
    pantheon_urls.append('https://www.godchecker.com/modern-mythology/pantheon/')
    pantheon_soups = get_soups(session, pantheon_urls)

    # Getting all god pages
    god_lists = [s.find(class_='text-bubble') for s in pantheon_soups]
    found_urls = flatten([collect_urls(g_l) for g_l in god_lists])
    # Filter out some garbage and repetitions
    god_urls = set(filter(lambda url: 'mythology' in url and 'list-of-names' not in url, found_urls))
    print(f"{len(god_urls)} gods found, coherent with site headline")  # Should be 3886

    print("Starting to scrape all god pages. Takes about 10 minutes...")
    god_soups = get_soups(session, list(god_urls))
    print("Done scraping")

    # Making the csv entries
    # Mentions of gods in other gods' descriptions don't always use the right name, so we will rely on a url mapping
    urls_to_names = dict([map_url_to_name(s) for s in god_soups])
    god_entries = [god_soup_to_entry(s, urls_to_names) for s in god_soups]
    # Getting all the entry names to use as columns
    columns = list(set(flatten([entry.keys() for entry in god_entries])))

    # Writing scaped data to disk as csv
    with open('gods.csv', 'w', encoding='utf-8') as file:
        w = csv.DictWriter(file, fieldnames=columns)
        w.writeheader()
        w.writerows(god_entries)


def flatten(l):
    return [item for sublist in l for item in sublist]


def collect_urls(s):
    return [a['href'] for a in s.find_all('a')]


def url_to_pantheon(url):
    return url[len(site_url):].split('-mythology')[0]


def pantheon_to_url(p):
    return site_url + p + '-mythology/pantheon'


def unique_pantheons(urls):
    pantheons = set([url_to_pantheon(url) for url in urls])
    return [pantheon_to_url(p) for p in pantheons]


def get_soups(session, url_list):
    """
    Collects html pages for given list of urls and turns them into bs objects
    """
    pages = list(map(lambda url: session.get(url), url_list))
    assert all(page.status_code == 200 for page in pages)
    soups = [bS(page.content, 'html.parser') for page in pages]
    return soups


def add_fact_to_entry(fact, entry):
    if not fact == '':
        key, value = fact.split(': ')
        if value == '':
            entry[key] = 'unspecified'
        else:
            entry[key] = value


def god_soup_to_entry(soup, mapping):
    """
    Takes a bs object of a god's page and creates its database entry
    """
    repeated_newlines = re.compile('\n+')
    entry = defaultdict(None)

    # Find the element containing all the facts and extract facts to add them to entry
    vitals_box = soup.find(class_='vitalsbox').find_all('p')
    facts = [repeated_newlines.split(s.getText()) for s in vitals_box]
    for fact in flatten(facts):
        add_fact_to_entry(fact, entry)
    if 'Alternative names' in entry:
        entry['Alternative names'] = entry['Alternative names'].split(', ')

    # Add the url for our historian friend to get additional data if needed, and the pantheon name
    entry['url'] = soup.find("link", {"rel": "canonical"})['href']
    pantheon_name = soup.find("div", {"id": "crumbs-bar"}).getText().split('\n')
    entry['Pantheon'] = pantheon_name[2]

    # Find all other gods mentioned in the page
    # URL to god name is used here because the actual written name in the text is not always quite right
    refs = None
    try:
        refs = set([mapping.get(element.get('href'), entry['Name']) for element in soup.find_all(class_='god-name')])
    except Exception as e:
        print(entry)
        print(e)
        print(len(soup.find_all(class_='god-name')))
    refs.discard(entry['Name'])
    entry['Related Gods'] = refs
    return entry


def map_url_to_name(soup):
    """
    Takes a bs object of a god's page and creates its database entry
    """
    name = soup.find(class_='vitalsbox').find('p').getText().split('\n')[1].split(': ')[1]
    url = soup.find("link", {"rel": "canonical"})['href']
    return url, name


main()
