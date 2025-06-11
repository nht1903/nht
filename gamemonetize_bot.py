import requests
from bs4 import BeautifulSoup
import schedule
import time
from typing import List

# Configuration placeholders
WP_API_URL = 'https://your-wordpress-site.com/wp-json/wp/v2/posts'
WP_USERNAME = 'your_wp_username'
WP_APP_PASSWORD = 'your_wp_application_password'

GAME_LIST_URL = 'https://www.gamemonetize.com/'  # Replace with actual list or category page

AUTH = (WP_USERNAME, WP_APP_PASSWORD)


def fetch_game_links(page_url: str) -> List[str]:
    """Return a list of individual game page URLs from GameMonetize."""
    response = requests.get(page_url, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    links = []
    for a in soup.select('a.game-item[href]'):
        link = a['href']
        if not link.startswith('http'):
            link = f'https://www.gamemonetize.com{link}'
        links.append(link)
    return links


def parse_game_page(url: str) -> dict:
    """Parse title, embed code, description and tags from a game page."""
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    title_tag = soup.find('h1') or soup.find('title')
    title = title_tag.get_text(strip=True) if title_tag else 'Untitled Game'

    embed_area = soup.find('textarea', {'id': 'embed-code'})
    if embed_area:
        embed_code = embed_area.get_text(strip=True)
    else:
        iframe = soup.find('iframe')
        embed_code = str(iframe) if iframe else ''

    desc_tag = soup.find('div', class_='game-description')
    if desc_tag:
        description = desc_tag.get_text(strip=True)
    else:
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc['content'] if meta_desc else ''

    tag_nodes = soup.select('.tags a')
    tags = [t.get_text(strip=True) for t in tag_nodes]

    return {
        'title': title,
        'embed_code': embed_code,
        'description': description,
        'tags': tags,
    }


def ensure_wp_tags(tag_names: List[str]) -> List[int]:
    """Ensure WordPress tags exist and return their IDs."""
    tag_ids = []
    for name in tag_names:
        search_url = WP_API_URL.replace('/posts', '/tags') + f'?search={name}'
        r = requests.get(search_url, auth=AUTH, timeout=30)
        r.raise_for_status()
        results = r.json()
        if results:
            tag_ids.append(results[0]['id'])
        else:
            create_url = WP_API_URL.replace('/posts', '/tags')
            cr = requests.post(create_url, json={'name': name}, auth=AUTH, timeout=30)
            cr.raise_for_status()
            tag_ids.append(cr.json()['id'])
    return tag_ids


def post_to_wordpress(game: dict):
    """Post a single game to WordPress."""
    tag_ids = ensure_wp_tags(game['tags']) if game['tags'] else []

    data = {
        'title': game['title'],
        'content': f"{game['embed_code']}<p>{game['description']}</p>",
        'status': 'publish',
    }
    if tag_ids:
        data['tags'] = tag_ids

    r = requests.post(WP_API_URL, json=data, auth=AUTH, timeout=30)
    r.raise_for_status()
    return r.json()


def job():
    links = fetch_game_links(GAME_LIST_URL)
    for link in links:
        try:
            game = parse_game_page(link)
            post_to_wordpress(game)
        except Exception as exc:
            print(f"Failed to process {link}: {exc}")


def main():
    schedule.every().day.at("02:00").do(job)
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == '__main__':
    main()
