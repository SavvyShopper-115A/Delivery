import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
import re
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

def parse_price(string):
    pattern = r'[\d.]+'
    matches = re.findall(pattern, string)
    return matches


def get_newegg_name(soup):

    name_element = soup.find('h1', {'class': 'product-title'})
    if name_element is None:
        print("name element none")
        return None
    
    name_text = name_element.text
    return name_text
    
def get_newegg_price(soup):

    price_element = soup.find('li', {'class': 'price-current'})
    
    if price_element is None:
        return None
    
    price_whole = str(price_element.find('strong').text)
    price_fraction = str(price_element.find('sup').text)
    price = price_whole + price_fraction
    cleaned_text = price.replace("$", "").replace(",", "")
    float_num = float(cleaned_text)
    return float_num

def get_amazon_name(soup):

    name_element = soup.find('h1', {'id': 'title'})
    if name_element is None:
        print("name element none")
        return None
    
    name_text = soup.find('span', {'id': 'productTitle'}).text
    return name_text
    
def get_amazon_price(soup):

    price_element = soup.find('span', {'class': 'a-price'})
    
    if price_element is None:
        return None
    
    price_text = str(price_element.find('span', {'class': 'a-offscreen'}).text)
    price = price_text.replace('$', '').replace(',', '').strip()
    float_num = float(price)
    return float_num

def get_craigslist_name(soup):

    name_element = soup.find('h1', {'class': 'postingtitle'})
    if name_element is None:
        print("name element none")
        return None
    
    name_text = soup.find('span', {'id': 'titletextonly'}).text
    return name_text
    
def get_craigslist_price(soup):

    price_element = soup.find('h1', {'class': 'postingtitle'})
    
    if price_element is None:
        return None
    
    price_text = str(price_element.find('span', {'class': 'price'}).text)
    price = price_text.replace('$', '').replace(',', '').strip()
    float_num = float(price)
    return float_num

def get_ebay_name(soup):

    name_element = soup.find('h1', {'class': 'x-item-title__mainTitle'})
    name_element_alt = soup.find('h1', {'class': 'product-title'})

    if name_element:
        # name_element = soup.find('div', {'class': 'vim x-item-title'})
        name_text = name_element.text
        return name_text
    elif name_element_alt:
        name_text = name_element_alt.text
        return name_text
    else:
        return None


def get_ebay_price(soup):

    price_element = soup.find('div', {'class': 'x-bin-price__content'})
    price_element_alt = soup.find('div', {'class': 'display-price'})
    price_element_auction = soup.find('div', {'class': 'x-bid-price__content'})

    if price_element:
        price_text = price_element.find(
            'div', {'class': 'x-price-primary'}).text
        parsed_price_text = parse_price(price_text)
        return float(parsed_price_text[0])
    elif price_element_alt:
        price_text = price_element_alt.find(
            'div', {'class': 'x-price-primary'}).text
        parsed_price_text = parse_price(price_text)
        return float(parsed_price_text[0])
    elif price_element_auction:
        price_text = price_element_auction.find(
            'div', {'class': 'x-price-primary'}).text
        parsed_price_text = parse_price(price_text)
        cleaned_text = parsed_price_text[0].replace("$", "").replace(",", "")
        return float(cleaned_text)
    else:
        return None


def get_best_buy_name(soup):

    name_element = soup.find('div', {'class': 'sku-title'})
    if name_element is None:
        print("name element none")
        return None

    name_text = name_element.find('h1', {'class': 'heading-5'}).text
    return name_text


def get_best_buy_price(soup):

    price_element = soup.find('div', {'class': 'priceView-hero-price'})

    if price_element is None:
        return None

    price_text = price_element.find(
        'span', {'class': 'sr-only'}).previous_sibling.text

    if price_text is None:
        return None
    try:
        price_text = str(price_text)
        cleaned_text = price_text.replace("$", "").replace(",", "")
        float_num = float(cleaned_text)
        return float_num
    except ValueError:
        return None
    

def get_walmart_name(soup):

    name_element = soup.find('h1', itemprop='name')
    
    if name_element is None:
        print("name element none")
        return None

    name_text = name_element.text
    return name_text


def get_walmart_price(soup):
    pattern = r'[\d.]+'
    price_element = soup.find('span', {'data-testid': 'price-wrap'})

    if price_element is None:
        return None
    

    price_text = price_element.find('span', {'itemprop': 'price'}).text

    if price_text is None:
        return None
    try:
        price_text = str(price_text)
        matches = re.findall(pattern, price_text)
        cleaned_text = matches[0].replace("$", "").replace(",", "")
        float_num = float(cleaned_text)
        return float_num
    except ValueError:
        return None


@app.route('/user_agent', methods=['GET'])
def get_user_agent():
    user_agent = request.headers.get('User-Agent')
    return f"User Agent: {user_agent}"

@app.route('/walmart', methods=['GET'])
def walmart():
    url = request.args.get('url')
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}
    if not url:
        return jsonify({'error': 'url missing'}), 400
        
    try:
        api_endpoint = f'https://api.scraperapi.com/?api_key={os.getenv("SCRAPER_API_KEY")}&url={url}'
        response = requests.get(api_endpoint, headers = headers)
        if response.status_code != 200:
            return jsonify({"error": "could not process url"}), 400
        
        soup = BeautifulSoup(response.content, 'html.parser')

        name = get_walmart_name(soup)
        price = get_walmart_price(soup)

        if (name is None or price is None):
            response = {
                'error': 'website of retailer not supported',
            }
            return jsonify(response), 400

        data = {
            "name": name,
            "price": price
        }
        return jsonify(data), 200

    except requests.exceptions.RequestException as e:

        return jsonify({'error': 'An unexpected error occurred on our end. Please try again later.'}), 500

@app.route('/newegg', methods=['GET'])
def newegg():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'url missing'}), 400
        
    try:
        api_endpoint = f'https://api.scraperapi.com/?api_key={os.getenv("SCRAPER_API_KEY")}&url={url}'
        response = requests.get(api_endpoint)
        if response.status_code != 200:
            return jsonify({"error": "could not process url"}), 400
        
        soup = BeautifulSoup(response.content, 'html.parser')

        name = get_newegg_name(soup)
        price = get_newegg_price(soup)

        if (name is None or price is None):
            response = {
                'error': 'website of retailer not supported',
            }
            return jsonify(response), 400

        data = {
            "name": name,
            "price": price
        }
        return jsonify(data), 200

    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'An unexpected error occurred on our end. Please try again later.'}), 500


@app.route('/amazon', methods=['GET'])
def amazon():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'url missing'}), 400
        
    try:
        api_endpoint = f'https://api.scraperapi.com/?api_key={os.getenv("SCRAPER_API_KEY")}&url={url}'
        response = requests.get(api_endpoint)
        if response.status_code != 200:
            return jsonify({"error": "could not process url"}), 400
        
        soup = BeautifulSoup(response.content, 'html.parser')

        name = get_amazon_name(soup)
        price = get_amazon_price(soup)

        if (name is None or price is None):
            response = {
                'error': 'website of retailer not supported',
            }
            return jsonify(response), 400

        data = {
            "name": name,
            "price": price
        }
        return jsonify(data), 200

    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'An unexpected error occurred on our end. Please try again later.'}), 500

@app.route('/craigslist', methods=['GET'])
def craigslist():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'url missing'}), 400
        
    try:
        api_endpoint = f'https://api.scraperapi.com/?api_key={os.getenv("SCRAPER_API_KEY")}&url={url}'
        response = requests.get(api_endpoint)
        if response.status_code != 200:
            return jsonify({"error": "could not process url"}), 400
        
        soup = BeautifulSoup(response.content, 'html.parser')

        name = get_craigslist_name(soup)
        price = get_craigslist_price(soup)

        if (name is None or price is None):
            response = {
                'error': 'website of retailer not supported',
            }
            return jsonify(response), 400

        data = {
            "name": name,
            "price": price
        }
        return jsonify(data), 200

    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'An unexpected error occurred on our end. Please try again later.'}), 500


api_params = {
    'country_code': 'us',
    'device_type': 'desktop',
    'follow_redirect': 'true',
    'retry_404': 'false',
    'api_key': os.getenv("SCRAPER_API_KEY"),
    'url': ''
}


@app.route('/ebay', methods=['GET'])
def ebay():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'url missing'}), 400

    try:
        api_endpoint = f'https://api.scraperapi.com/?api_key={os.getenv("SCRAPER_API_KEY")}&url={url}'
        response = requests.get(api_endpoint)
        if response.status_code != 200:
            return jsonify({"error": "could not process url"}), 400

        soup = BeautifulSoup(response.content, 'html.parser')

        name = get_ebay_name(soup)
        price = get_ebay_price(soup)

        if (name is None or price is None):
            response = {
                'error': 'website of retailer not supported',
            }
            return jsonify(response), 400

        data = {
            "name": name,
            "price": price
        }
        return jsonify(data), 200

    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'An unexpected error occurred on our end. Please try again later.'}), 500


@app.route('/bestbuy')
def bestbuy():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'url missing'}), 400

    try:
        api_params['url'] = url
        response = requests.get('http://api.scraperapi.com', params=api_params)
        if response.status_code != 200:
            return jsonify({"error": "could not process url"}), 400

        soup = BeautifulSoup(response.content, 'html.parser')

        name = get_best_buy_name(soup)
        price = get_best_buy_price(soup)

        # print("Name: {}, Price: {}".format(name, price))
        if (name is None or price is None):
            response = {
                'error': 'website of retailer not supported',
            }
            return jsonify(response), 400

        data = {
            "name": name,
            "price": price
        }
        return jsonify(data), 200

    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'An unexpected error occurred on our end. Please try again later.'}), 500