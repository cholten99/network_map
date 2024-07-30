import psycopg2
import random

def read_params(file_path):
    params = {}
    with open(file_path, 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            if value.lower() in ['true', 'false']:
                value = value.lower() == 'true'
            elif '.' in value:
                value = float(value)
            else:
                value = int(value)
            params[key] = value
    return params

def validate_params(params):
    if params['num_internal_pages'] <= 0:
        raise ValueError("Number of internal pages must be greater than 0")
    if params['avg_links_per_internal_page'] < 0:
        raise ValueError("Average links per internal page must be 0 or greater")
    if not (0 <= params['percent_internal_to_external'] <= 100):
        raise ValueError("Percentage likelihood must be between 0 and 100")

def connect_to_db():
    return psycopg2.connect(
        dbname="network_map",
        user="dbuser",
        password="PewS$6BB{@e)q#;",
        host="localhost"
    )

def empty_tables_if_required(conn, empty_tables):
    if empty_tables:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE links, externalpages, internalpages RESTART IDENTITY CASCADE;")
        conn.commit()

def generate_internal_pages(num_pages):
    internal_pages = []
    for i in range(num_pages):
        page = {
            'url': f'http://internal.page/{i}',
            'title': f'Internal Page {i}',
            'primary_publishing_organisation': f'Org {i % 10}',
            'public_updated_at': None,
            'updated_at': None,
            'first_published_at': None,
            'section': f'Section {i % 5}',
            'description': f'Description for internal page {i}',
            'last_scanned': None
        }
        internal_pages.append(page)
    return internal_pages

def generate_external_pages(num_pages):
    external_pages = []
    for i in range(num_pages):
        page = {
            'url': f'http://external.page/{i}',
            'domain': f'domain{i % 10}.com',
            'title': f'External Page {i}'
        }
        external_pages.append(page)
    return external_pages

def generate_links(num_pages, avg_links, percent_external):
    links = []
    for i in range(num_pages):
        num_links = max(0, int(random.gauss(avg_links, 1)))  # Gaussian distribution for average links
        for _ in range(num_links):
            is_external = random.random() < (percent_external / 100)
            link = {
                'source_page_id': i + 1,
                'target_internal_page_id': None,
                'target_external_page_id': None
            }
            if is_external:
                link['target_external_page_id'] = random.randint(1, 100)  # Assuming 100 external pages
            else:
                link['target_internal_page_id'] = random.randint(1, num_pages)
            links.append(link)
    return links

def insert_data(conn, internal_pages, external_pages, links):
    try:
        with conn.cursor() as cur:
            # Insert internal pages
            for page in internal_pages:
                cur.execute("""
                    INSERT INTO internalpages (url, title, primary_publishing_organisation, public_updated_at, updated_at,
                                               first_published_at, section, description, last_scanned)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING page_id;
                """, (page['url'], page['title'], page['primary_publishing_organisation'], page['public_updated_at'],
                      page['updated_at'], page['first_published_at'], page['section'], page['description'],
                      page['last_scanned']))
                page_id = cur.fetchone()[0]
                page['page_id'] = page_id

            # Insert external pages
            for page in external_pages:
                cur.execute("""
                    INSERT INTO externalpages (url, domain, title)
                    VALUES (%s, %s, %s)
                    RETURNING page_id;
                """, (page['url'], page['domain'], page['title']))
                page_id = cur.fetchone()[0]
                page['page_id'] = page_id

            # Insert links
            for link in links:
                cur.execute("""
                    INSERT INTO links (source_page_id, target_internal_page_id, target_external_page_id)
                    VALUES (%s, %s, %s);
                """, (link['source_page_id'], link['target_internal_page_id'], link['target_external_page_id']))

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e

# Main function to orchestrate the steps
def main():
    params = read_params('params.txt')
    validate_params(params)
    conn = connect_to_db()

    try:
        empty_tables_if_required(conn, params['empty_tables'])
        internal_pages = generate_internal_pages(params['num_internal_pages'])
        external_pages = generate_external_pages(100)  # Assuming 100 external pages for the example
        links = generate_links(params['num_internal_pages'], params['avg_links_per_internal_page'], params['percent_internal_to_external'])
        insert_data(conn, internal_pages, external_pages, links)
    finally:
        conn.close()

if __name__ == "__main__":
    main()

