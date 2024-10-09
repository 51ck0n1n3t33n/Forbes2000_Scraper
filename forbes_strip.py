import requests
from bs4 import BeautifulSoup
import csv
import time
from urllib.parse import urlparse

###########################################################################################################
#   Improved Forbes 2000 List Web Scraper
#   Purpose:            Improved code to scrape company details from Forbes URLs using modern libraries
#                       like requests and BeautifulSoup for easier and more maintainable parsing.
#   How to use this:    1 - Create a CSV of Forbes 2000 URLs (example below)
#                       2 - Specify the input/output file paths in the ProcessURLs class constructor
#                       3 - Run the script
###########################################################################################################

class ForbesScraper:
    def __init__(self, url):
        self.url = url
        self.values = {
            'ForbesURL': url,
            'MarketCap': '',
            'Industry': '',
            'Founded': '',
            'Country': '',
            'CEO': '',
            'Employees': '',
            'Sales': '',
            'Headquarters': '',
            'Website': '',
            'EmailDomain': ''
        }
        self.soup = None

    def fetch_page(self):
        try:
            response = requests.get(self.url, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
            self.soup = BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            print(f"Error fetching URL {self.url}: {e}")
            return False
        return True

    def parse_data(self):
        if not self.soup:
            return
        
        # Example of parsing Market Cap
        market_cap_element = self.soup.find('li', class_='amount')
        if market_cap_element:
            self.values['MarketCap'] = self.clean_text(market_cap_element.text)
        
        # Example of parsing Industry
        industry_element = self.soup.find('dt', text='Industry')
        if industry_element:
            industry_value = industry_element.find_next('dd')
            if industry_value:
                self.values['Industry'] = self.clean_text(industry_value.text)
        
        # Parsing CEO Name
        ceo_element = self.soup.find('dt', text='Chief Executive Officer')
        if ceo_element:
            ceo_value = ceo_element.find_next('dd')
            if ceo_value:
                self.values['CEO'] = self.clean_text(ceo_value.text)

        # Extract Website and Email Domain
        website_element = self.soup.find('a', href=True, text=True)
        if website_element:
            website_url = website_element['href']
            self.values['Website'] = website_url
            self.values['EmailDomain'] = urlparse(website_url).netloc

    @staticmethod
    def clean_text(text):
        return text.strip().replace('\n', '').replace('\t', '')

    def get_values(self):
        return self.values


class ProcessURLs:
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file
        self.urls = []
        self.load_urls()
        self.scrape_urls()

    def load_urls(self):
        with open(self.input_file, newline='') as csvfile:
            csv_reader = csv.reader(csvfile)
            self.urls = [row[0] for row in csv_reader if row]

    def scrape_urls(self):
        keys = ['ForbesURL', 'MarketCap', 'Industry', 'Founded', 'Country', 'CEO', 'Employees', 'Sales', 'Headquarters', 'Website', 'EmailDomain']
        with open(self.output_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=keys)
            writer.writeheader()
            
            for url in self.urls:
                scraper = ForbesScraper(url)
                if scraper.fetch_page():
                    scraper.parse_data()
                    writer.writerow(scraper.get_values())
                time.sleep(1)  # To prevent getting blocked by the server


# Example usage
input_file_path = 'input_urls.csv'  # Path to your input CSV file containing Forbes URLs
output_file_path = 'output_data.csv'  # Path to your output CSV file
process = ProcessURLs(input_file_path, output_file_path)