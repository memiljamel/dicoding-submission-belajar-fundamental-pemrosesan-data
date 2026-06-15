import time

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    )
}


def fetching_content(url):
    """Mengambil konten HTML dari URL yang diberikan."""
    session = requests.Session()
    response = session.get(url, headers=HEADERS)
    try:
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Terjadi kesalahan ketika melakukan requests terhadap {url}: {e}")
        return None


def extract_product_data(card):
    """Mengambil data produk berupa title, price, rating, colors, size, dan gender dari card (element html)."""
    title = card.find('h3', class_='product-title')
    price = card.find('span', class_='price')
    rating = card.find('p', string=lambda t: t and 'Rating' in t)
    colors = card.find('p', string=lambda t: t and 'Colors' in t)
    size = card.find('p', string=lambda t: t and 'Size' in t)
    gender = card.find('p', string=lambda t: t and 'Gender' in t)

    products = {
        'title': title.text.strip() if title else 'Unknown Title',
        'price': price.text.strip() if price else 'Price Not Available',
        'rating': rating.text.strip() if rating else 'No Rating',
        'colors': colors.text.strip() if colors else 'No Color Info',
        'size': size.text.strip() if size else 'No Size Info',
        'gender': gender.text.strip() if gender else 'No Gender Info',
    }

    return products


def scrape_product(base_url, start_page=1, delay=2):
    """Fungsi utama untuk mengambil keseluruhan data, mulai dari requests hingga menyimpannya dalam variabel data."""
    data = []
    page_number = start_page

    while True:
        url = base_url if page_number == 1 else f"{base_url}/page{page_number}"
        print(f"Scraping halaman: {url}")

        content = fetching_content(url)
        if content:
            soup = BeautifulSoup(content, "html.parser")
            cards_element = soup.find_all('div', class_='collection-card')
            for card in cards_element:
                product = extract_product_data(card)
                data.append(product)

            next_button = soup.select_one('li.next a')
            if next_button:
                page_number += 1
                time.sleep(delay)  # Delay sebelum halaman berikutnya
            else:
                break  # Berhenti jika sudah tidak ada next button
        else:
            break  # Berhenti jika ada kesalahan

    return data
