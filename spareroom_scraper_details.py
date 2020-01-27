# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 02:55:00 2020

@author: salom
"""
import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm

data_repository = 'your/data/path' #YOUR_DATA_PATH
os.chdir(data_repository)

listing_data = pd.read_csv('spareroom_listings.csv')
features = ['type', 'neighbourhood', 'postal code', 'nearest station']

rich_data = pd.DataFrame()
for id_num in tqdm(listing_data['id'].sort_values().unique()):
    try:
        data = {'id':id_num}
        web_page = requests.get('https://www.spareroom.co.uk/flatshare/' + str(id_num))
        listing = BeautifulSoup(web_page.text.replace('ISO-8859-1', 'utf-8'), 'html.parser')
        intro = listing.find('div', class_='property-intro').text
        data.update({'intro': intro})
        details = listing.find('div', class_='property-details')
        key_features = details('li', class_='key-features__feature')
        for i, feature in enumerate(key_features[:-1]):
            data.update({features[i]:feature.text})
        try:
            time_to_station = details.find('small', class_='key-features__station-distance').text
        except: 
            time_to_station = 'none'
        finally:  
            data.update({'time to station':time_to_station})
        try:
            rooms = details.find('ul', class_='room-list')
            room_price = rooms('strong')
            room_type = rooms('small')
            for i in range(len(room_price)):
                data.update({'Room {} price'.format(i+1):room_price[i].text})
                data.update({'Room {} type'.format(i+1):room_type[i].text})
        except:
            pass
        keys = listing('dt')
        values = listing('dd')
        for key, value in zip(keys[1:], values[1:]):
            data.update({key.text:value.text})
        
        data_formatted = {}
        for key in data.keys():
            key_form = re.sub(' +', ' ', key.replace('\n', '').lower())
            value_form = re.sub(' +', ' ', str(data[key]).replace('\n', '').lower())
            data_formatted.update({key_form: value_form})
    except:
        data_formatted = {'id':id_num, 'error': True}
    
    rich_data = rich_data.append(data_formatted, ignore_index = True)

rich_data['date scraped'] = pd.datetime.today() 
if not os.path.isfile('spareroom_listings.csv'):
    rich_data.to_csv('spareroom_listings_rich.csv', index = False)
else:
    old = pd.read_csv('spareroom_listings_rich.csv')
    rich_data = old.append(rich_data)
    rich_data.to_csv('spareroom_listings_rich.csv', index = False)

# add get image