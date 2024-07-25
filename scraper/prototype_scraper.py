import requests
from bs4 import BeautifulSoup
import psycopg2
from urllib.parse import urlparse, urljoin
import re

# Database connection details
DB_NAME = 'network_map'
DB_USER = 'dbuser'
DB_PASSWORD = 'PewS$6BB{@e)q#;'
DB_HOST = 'localhost'

# Function to normalize URLs
def normalize_url(url):
    parsed_url = urlparse(url)
    normalized_url = urljoin(url, parsed_url.path).rstrip('/')
    return normalized_url.lower()

# Connect to PostgreSQL
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST)
cursor = conn.cursor()

# Function to add internal page
def add_internal_page(url, title=None, primary_publishing_organisation=None, public_updated_at=None, updated_at=None, first_published_at=None, section=None, description=None):
    normalized_url = normalize_url(url)
    try:
        cursor.execute(
            """INSERT INTO InternalPages (url, title, primary_publishing_organisation, public_updated_at, updated_at, first_published_at, section, description) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
               ON CONFLICT (url) DO NOTHING 
               RETURNING page_id""",
            (normalized_url, title, primary_publishing_organisation, public_updated_at, updated_at, first_published_at, section, description)
        )
        result = cursor.fetchone()
        conn.commit()
        return result[0] if result else None
    except Exception as e:
        conn.rollback()
        print(f"Error adding internal page: {e}")
        return None

# Function to extract metadata from HTML
def extract_metadata(soup):
    metadata = {
        'primary_publishing_organisation': None,
        'public_updated_at': None,
        'updated_at': None,
        'first_published_at': None,
        'section': None,
        'description': None
    }

    meta_tags = soup.find_all('meta')
    for meta in meta_tags:
        if 'name' in meta.attrs:
            name = meta.attrs['name'].lower()
            if name == 'primary_publishing_organisation':
                metadata['primary_publishing_organisation'] = meta.attrs.get('content')
            elif name == 'public_updated_at':
                metadata['public_updated_at'] = meta.attrs.get('content')
            elif name == 'updated_at':
                metadata['updated_at'] = meta.attrs.get('content')
            elif name == 'first_published_at':
                metadata['first_published_at'] = meta.attrs.get('content')
            elif name == 'section':
                metadata['section'] = meta.attrs.get('content')
            elif name == 'description':
                metadata['description'] = meta.attrs.get('content')
    return metadata

# Scrape the http://gov.uk page
response = requests.get('http://gov.uk')
if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    title = soup.title.string if soup.title else None
    metadata = extract_metadata(soup)
    
    # Insert the page and metadata into the InternalPages table
    page_id = add_internal_page(
        url='http://gov.uk',
        title=title,
        primary_publishing_organisation=metadata['primary_publishing_organisation'],
        public_updated_at=metadata['public_updated_at'],
        updated_at=metadata['updated_at'],
        first_published_at=metadata['first_published_at'],
        section=metadata['section'],
        description=metadata['description']
    )

    if page_id:
        print(f"Page added with ID: {page_id}")
    else:
        print("Page was not added or already exists.")
else:
    print(f"Failed to fetch the page. Status code: {response.status_code}")

# Close the database connection
cursor.close()
conn.close()
