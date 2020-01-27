# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 00:48:50 2020

@author: salom
"""
import os
import traceback
import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

data_repository = 'your/data/path' 
os.chdir(data_repository)

# Searches to Execute
zones = ['London Zone 1', 'London Zone 2', 'London Zone 3', 'London Zone 4'] 
attributes = ['id', 'title', 'brand', 'type', 'days-old', 'available',
              'status', 'early-bird', 'neighbourhood', 'postcode', 'scp',
              'property-type', 'property-type-more', 'rooms-in-property',
              'advertiser-role', 'price-per-month', 'price-per-week']

lower_bound = np.arange(0, 4800, 30)
higher_bound = np.roll(lower_bound, -1)
lower_bound = lower_bound[:-1] + 1
higher_bound = higher_bound[:-1]


listing_data = pd.DataFrame()

driver = webdriver.Chrome('path/to/chrome/driver.exe') #
driver.get('https://www.spareroom.co.uk/')
driver.find_element_by_class_name('authentication-links__sign-in-link').click()
email = driver.find_element_by_name('email')
password = driver.find_element_by_name('password')
email.send_keys('your@email') # Login for SpareRoom
password.send_keys('yourpassword')
password.send_keys(Keys.RETURN)

try:
    for zone in zones:
        search = driver.find_element_by_name('search')
        search.clear()
        search.send_keys(zone)
        search.send_keys(Keys.RETURN)
        for lb, hb in zip(lower_bound, higher_bound):
            min_rent = driver.find_element_by_name('min_rent')
            min_rent.clear()
            min_rent.send_keys(str(lb))
            max_rent = driver.find_element_by_name('max_rent')
            max_rent.clear()
            max_rent.send_keys(str(hb))
            driver.find_element_by_class_name('search-filter__submit').click()
            results_header = driver.find_element_by_id('results_header').text
            if results_header == 'Sorry, no matching adverts found':
                continue

            clicks = 100
            for _ in range(clicks): 
                listing_results = driver.find_elements_by_class_name('listing-result')
                for result in listing_results:
                    data = {x:np.nan for x in attributes}
                    for attr in attributes:
                        if attr in ['price-per-month', 'price-per-week']:
                            data[attr] = result.get_attribute('data-' + attr)
                        else:    
                            data[attr] = result.get_attribute('data-listing-' + attr)
                    listing_data = listing_data.append(data, ignore_index = True)
                    print(data)
                    
                
                currentnav = driver.find_element_by_class_name('navcurrent').text
                a = currentnav.find('-')
                b = currentnav.find('of')
                c = currentnav.find('results')
                current = int(currentnav[a+1:b])
                results = int(currentnav[b+3:c-1])
                if current != results:
                    next_button = driver.find_element_by_class_name('navnext').click()
                else:
                    break
    listing_data['error'] = False
except Exception:
    listing_data['error'] = True
    traceback.print_exc()
    
finally:
    listing_data['date scraped'] = pd.datetime.today()  
    if not os.path.isfile('spareroom_listings.csv'):
        listing_data.to_csv('spareroom_listings.csv', index = False)
    else:
        old = pd.read_csv('spareroom_listings.csv')
        listing_data = old.append(listing_data)
        listing_data.to_csv('spareroom_listings.csv', index = False)
    
    
