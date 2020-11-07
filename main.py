import requests
from bs4 import BeautifulSoup as bs
from datetime import date
import pandas as pd


def scraping_amazon(link, df_raw, category):
    '''
    This function takes data from the best sellers section in Amazon.
        link: the Amazon url where take the data.
        df_raw: a dictionari where store the data.
        category: the category corresponding the url.
    '''

    # Changing the url to achieve the same structure like the others.
    if 'dmusic' in link and not('pg=2' in link):
        link = link.split('/')
        link = link[:(link.index('dmusic')+1)]
        link.append('digital-music-track')
        link = '/'.join(link)
    
    # Searching all the product boxes in the link, and taking the data from all this boxes to the dictionary.
    page = requests.get(link, headers=headers)
    soup = bs(page.content)
    names = soup.find_all(class_='zg-item-immersion')
    for n in names:
        df_raw['Date'].append(today) # Storing the date of the scraping for the product.
        df_raw['Category'].append(category) # Storing the category of the product.
        try:
            # Storing the rank position of the product.
            df_raw['Rank'].append(n.find(class_='zg-badge-text').text[1:])
        except:
            df_raw['Rank'].append('')
        try:
            # Storing the name/description of the product.
            df_raw['Product'].append(n.find(class_='p13n-sc-truncate-desktop-type2').text.strip())
        except:
            df_raw['Product'].append('')
        try:
            # Storing the valuation over 5 stars of the product.
            df_raw['Stars'].append(n.find(class_='a-icon-alt').text[:3].replace(',','.'))
        except:
            df_raw['Stars'].append('')
        try:
            # Storing the number of opinions of the product.
            df_raw['N_Opinions'].append(n.find(class_='a-size-small a-link-normal').text.replace('.',''))
        except:
            df_raw['N_Opinions'].append('')
        try:
            # Storing the price in € of the product.
            df_raw['Price'].append(n.find(class_='p13n-sc-price').text.replace(' €','').replace(',','.'))
        except:
            df_raw['Price'].append('')

    # Making sure that the request success by executing this function again in case not.
    if len(names) == 0:
        scraping_amazon(link, df_raw, category)

    # Scraping the second (and last) page of the url by executing this function to the new link.
    elif not 'pg=2' in link:
        next_link = link + '/ref=zg_bs_pg_2?ie=UTF8&pg=2'
        scraping_amazon(next_link, df_raw, category)
        print(category) # Control to check the progress of this function in the terminal.


# Defining the headers which will be used to do the requests.
headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,\
        */*;q=0.8",
        "Accept-Encoding": "gzip, deflate, sdch, br",
        "Accept-Language": "en-US,en;q=0.8",
        "Cache-Control": "no-cache",
        "dnt": "1",
        "Pragma": "no-cache",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/5\
        37.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
        }

main_link = 'https://www.amazon.es/gp/bestsellers/' # Defining the url od best sellers in Amazon.

# Making sure the request success checking the list of urls found.
links = []
while len(links)==0:
    page = requests.get(main_link, headers=headers)
    soup = bs(page.content)
    links = soup.find_all(id='zg_browseRoot')[0].find_all('a')

# Defining the current day and the dictionary where the data will be stored.
today = date.today().strftime("%d/%m/%Y")
df_raw = {'Date':[], 'Category':[], 'Rank':[], 'Product':[], 'Stars':[], 'N_Opinions':[], 'Price':[]}

# Scraping all the categories in the Amazon best sellers with the function defined.
for l in links:
    category = l.text # Defining the category name that will be stored.
    link = l.get('href')
    scraping_amazon(link, df_raw, category)

# Converting the data from the dictionary in a dataframe.
df = pd.DataFrame()
for k,v in df_raw.items():
    df[k] = v

# Exporting the data in the dataframe in a csv file.
df.to_csv('data.csv', index=False)