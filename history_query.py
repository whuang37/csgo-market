# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% [markdown]
# # Scraping Datasets of the Market History of all Counter Strike: Global Offensive Items
# 
# This notebook includes all the code written to scrape market history from steam json requests. I am still exploring/learning web scraping so the code may not be the best as I tried to experiment with new methods and technologies. Steam has multiple naming irregularities as well as rate limiting that made some manual data cleaning necessary. If you want to rescrape all data, change the values in the third cell of this notebook. Total data scraping time (excluding coding time) was approximately 12 hours. 
# 
# Data is split up into multiple xlsx files to account for potential crashes or errors in data collection (there were many).
# 

# %%
import requests
import json
from datetime import datetime, date
import time
import random
import pandas as pd
import numpy as np
import glob

import logging

logging.basicConfig(filename = "status.log", format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level = logging.INFO)
# %%
# Settings Cell
appid = 730 #CSGO
currency = 1 # USD
country = "US"
cookie = {"steamLoginSecure": "76561198074601257%7C%7C250554B95983A99ABF98690B62A1D39737453316"} # steamloginsecure cookie. Please enter in your own for this to work properly

FN = "Factory New"
MW = "Minimal Wear"
FT = "Field-Tested"
WW = "Well-Worn"
BS = "Battle-Scarred"

starting_date = date(2013, 8, 1) # originally scraped from 8-1-2013 but upon data analysis found the first date of market sales is 8-13-2013
ending_date = date(2020, 9, 14)


# %%
# Creates a list of dates in the date range for comparison to data pulled from the market later
dates_list = pd.date_range(start = starting_date, end = ending_date)

# %% [markdown]
# ## get_history
# 
# get_history() is the primary function used to pull data from the Steam server using a json get request with the item name and symbols formatted to ASCII. Steam servers will return a status indicating whether the request was successful and a list of prices and the volume sold for each particular date. If a date sold nothing, there is no entry and the list simply skips that date. In order to combat this we use date_list, a list of every date in between our given range. Each date in the date list is compared to the date given in the steam data. If the steam data date does not match, we append a None, None to the price/volume list and increase the date_list index up again until the data has another value. 
# 
# This function underwent multiple revisions. Other possible variants include checking the difference between the current date and the previous date and appending Nones based on that value.
# 
# Steam also gives hourly? (unsure if hourly but seems so) price data for more recent dates. This means a date can appear multiple times. In order to address this, data with the same date as the previous data entry is aggregated together (price is averaged and volume is summed).  

# %%
def get_history(name):
    url = "http://steamcommunity.com/market/pricehistory/?country={0}&currency={1}&appid={2}&market_hash_name={3}".format(country, currency, appid, name)

    for x in range(3): # occasionally will hit connection errors
        try:
            item = requests.get(url, cookies = cookie)
        except Exception as e:
            print(e)
            if x == 2:
                return 1
            else:
                time.sleep(60) # waits 60 seconds to allow steam to refresh
                continue
        else:
            break

    item = item.content
    item = json.loads(item)

    if item: # checks if returned anything
        item_prices = item["prices"] 
        success = item["success"]
        if (item_prices == False) | (not item_prices) | (success == False):
            return 1
        else:
            print("{0} CURRENTLY SCRAPING ITEM: {1}, NUMBER {2} OF {3} ITEMS".format(datetime.now(), name, current_num, total_items)) # status check
            logging.info("{0} CURRENTLY SCRAPING ITEM: {1}, NUMBER {2} OF {3} ITEMS".format(datetime.now(), name.replace("★%20", ""), current_num, total_items))
            pricevol = [] # price and volume are combined for multiindexing in the dataframe later
            dates = [] # used to check whether dates repeat
            item_counter = 0 
            date_counter = -1

            while (date_counter < len(dates_list) - 1) & (item_counter < len(item_prices)):
                date_counter += 1
                current_date = datetime.strptime(item_prices[item_counter][0][0:11], "%b %d %Y").date()
                if (current_date == dates_list[date_counter - 1]): # some entries have multiple entries per day
                    pricevol[-2] = np.mean([item_prices[item_counter][1], pricevol[-2]]) # averages the prices in the day and rewrites the previously written one
                    pricevol[-1] = int(item_prices[item_counter][2]) + pricevol[-1] # adds the volumes for the day together
                    date_counter -= 1
                    item_counter += 1
                elif dates_list[date_counter] != current_date:
                    pricevol.extend((None, None))
                else:
                    pricevol.append(item_prices[item_counter][1]) # appending price
                    pricevol.append(int(item_prices[item_counter][2])) # appending volume
                    dates.append(current_date) # appending the date into a list
                    item_counter += 1
        
            if current_date != ending_date: # adds extra nones to end if the present has no sales
                diff = ending_date - current_date
                pricevol.extend([None for x in range(0, diff.days * 2)])
    else:
        print("No contents on {}".format(name))
        logging.warning("No contents on {}".format(name))
        return 1
    return pricevol

# %% [markdown]
# ## Weapon Skins Price History Collection
# 
# Scraping weapon skins involves formatting the skin's name and iterating through all possible conditions, souvenir, and StatTrak variants.
# 

# %%
all_skins = pd.read_excel("items_list/skins_list.xlsx", index_col = 0)

knives = pd.read_excel("items_list/knivesgloves_list.xlsx", index_col = 0)
all_skins = all_skins.append(knives, ignore_index = True)
all_skins = all_skins.drop(all_skins.index[0:889])

# %%
def make_hash_name(weapon, skin, quality, condition, st, sv):
    if skin == "★ (Vanilla)":
        name = "{0}".format(weapon) # vanilla knives have no condition or skin name
    else:
        name = "{0} | {1} ({2})".format(weapon, skin, condition)
        
    if st == True:
        name = "StatTrak™ " + name
    elif sv == True: 
        name = "Souvenir " + name
        
    if quality in ("Extraordinary", "Covert"): # knives and gloves have a star before their name
        name = "★ " + name
        
    formatted_name = name.replace(" ", "%20") 
    formatted_name = formatted_name.replace("&", "%26")
    formatted_name = formatted_name.replace("|", "%7C")
    formatted_name = formatted_name.replace("+", "%2B")
    formatted_name = formatted_name.replace(":", "%3A")
    formatted_name = formatted_name.replace("/", "%2F")
    formatted_name = formatted_name.replace("(", "%28")
    formatted_name = formatted_name.replace(")", "%29")

    return formatted_name


# %%
skin_history = {}
i = 0
current_num = 0
total_items = len(all_skins.index)

for index, row in all_skins.iterrows():
    current_num += 1
    # checks whether to reiterate for stattrak and souvenir
    if (row["StatTrak"] == True) | (row["Souvenir"] == True):
        svst = ((False, False), (row["StatTrak"], row["Souvenir"]))
    else:
        svst = ((False, False),)
    for st, sv in svst:
        if row["Skin"] == "★ (Vanilla)":
            possible_conditions = (None,)
        else:
            possible_conditions = (BS, WW, FT , MW , FN)
        for condition in possible_conditions: # iterates through all possible conditions
            time.sleep(random.uniform(.5, 3)) # avoid steam rate limiting with a random sleep
            name = make_hash_name(row["Weapon"], row["Skin"], row["Quality"], condition, st, sv)
            price_vol_history = get_history(name)
            if price_vol_history == 1:
                print("{0} HAS FAILED".format(name))
                logging.warning("{0} HAS FAILED".format(name.replace("★%20", "")))
                continue
            col_index = "col_" + str(i)
            skin_history[col_index] = [row["Weapon"], row["Collection"], row["Quality"], row["Skin"], condition, st, sv] + price_vol_history
            i += 1
    if current_num % 100 == 0: # saves the data to csv every 100 items to protect against crashes
        print("made a new file!")
        skins_prices = pd.DataFrame.from_dict(skin_history, orient = "index")
        skins_prices.to_excel("skins_query/skins{}.xlsx".format(current_num / 100))
        skin_history.clear()

if skin_history != {}:
    print("finished!")
    logging.info("Skins finished!")
    skins_prices = pd.DataFrame.from_dict(skin_history, orient = "index")
    skins_prices.to_excel("skins_query/skins_final.xlsx")

# %% [markdown]
# ## Stickers Price History Collection
# 
# Sticker history collection works a bit different from skins. Sticker names have many variants depending on the collection or lack thereof. 

# %%
all_stickers = pd.read_excel("items_list/stickers_list.xlsx", index_col = 0)

# %%
def make_sticker_hash(collection, skin):
    if collection == None:
        name = "Sticker | {0}".format(skin)
    elif ("201" in collection) & (("community" not in collection) | ("winter" not in collection)): # if there is a year in the name and is tourney capsule
        name = "Sticker | {0} | {1}".format(skin, collection)
    else:
        name = "Sticker | {0}".format(skin)

    formatted_name = name.replace(" ", "%20") 
    formatted_name = formatted_name.replace("&", "%26")
    formatted_name = formatted_name.replace("|", "%7C")
    formatted_name = formatted_name.replace("+", "%2B")
    formatted_name = formatted_name.replace(":", "%3A")
    formatted_name = formatted_name.replace("/", "%2F")
    formatted_name = formatted_name.replace("(", "%28")
    formatted_name = formatted_name.replace(")", "%29")

    return formatted_name


# %%
sticker_history = {}
i = 0
current_num = 0
total_items = len(all_stickers.index)

for index, row in all_stickers.iterrows():
    current_num += 1
    time.sleep(random.uniform(.5, 3)) # avoid steam rate limiting with a random sleep
    name = make_sticker_hash(row["Collection"], row["Skin"])
    price_vol_history = get_history(name)
    if price_vol_history == 1:
        print("{0} HAS FAILED".format(name))
        logging.warning("{0} HAS FAILED".format(name))
        continue
    col_index = "col_" + str(i)
    sticker_history[col_index] = ["Sticker", row["Collection"], row["Quality"], row["Skin"], None, None, None] + price_vol_history
    i += 1
    if current_num % 300 == 0: # saves the data to csv every 100 items to protect against crashes
        print("made a new file!")
        skins_prices = pd.DataFrame.from_dict(sticker_history, orient = "index")
        skins_prices.to_excel("stickers_query/stickers{}.xlsx".format(current_num / 300))
        sticker_history.clear()

if sticker_history != {}:
    print("finished!")
    logging.info("Stickers Finished!")
    skins_prices = pd.DataFrame.from_dict(sticker_history, orient = "index")
    skins_prices.to_excel("stickers_query/stickers_final.xlsx")

# %% [markdown]
# ## Cases Price History Collection
# 
# Cases work with a simple query. Very little changes to name needed.

# %%
all_cases = pd.read_excel("items_list/cases_list.xlsx", index_col = 0)

# %%
def make_case_hash(skin):
    name = skin

    formatted_name = name.replace(" ", "%20") 
    formatted_name = formatted_name.replace("&", "%26")
    formatted_name = formatted_name.replace("|", "%7C")
    formatted_name = formatted_name.replace("+", "%2B")
    formatted_name = formatted_name.replace(":", "%3A")
    formatted_name = formatted_name.replace("/", "-")
    formatted_name = formatted_name.replace("(", "%28")
    formatted_name = formatted_name.replace(")", "%29")

    return formatted_name


# %%
case_history = {}
i = 0
current_num = 0
total_items = len(all_cases.index)

for index, row in all_cases.iterrows():
    current_num += 1
    time.sleep(random.uniform(.5, 3)) # avoid steam rate limiting with a random sleep
    name = make_case_hash(row["Skin"])
    price_vol_history = get_history(name)
    if price_vol_history == 1:
        print("{0} HAS FAILED".format(name))
        logging.warning("{0} HAS FAILED".format(name))
        continue
    col_index = "col_" + str(i)
    case_history[col_index] = [row["Weapon"], row["Collection"], None, row["Skin"], None, None, None] + price_vol_history
    i += 1
    if current_num % 300 == 0: # saves the data to csv every 100 items to protect against crashes
        print("made a new file!")
        skins_prices = pd.DataFrame.from_dict(case_history, orient = "index")
        skins_prices.to_excel("others_query/cases{}.xlsx".format(current_num / 300))
        case_history.clear()

if case_history != {}:
    print("finished!")
    logging.info("cases finished!")
    skins_prices = pd.DataFrame.from_dict(case_history, orient = "index")
    skins_prices.to_excel("others_query/cases_final.xlsx")

# %% [markdown]
# ## Others Price History Collection
# 
# Others are a bit more finnicky. Music Kits do have a StatTrak variant which much be accounted for by iterating through StatTraks. The various items are also formatted in wildly different ways ways which also must be accounted for.

# %%
all_others = pd.read_excel("items_list/others_list.xlsx", index_col = 0)

# %%
def make_others_hash(weapon, skin, st):
    if (weapon in ("Agents", "Items", "Collectible Pins")) | ("StatTrak" in skin): # certain items are formatted properly in list and dont need their weapon added to again
        name = skin
    else: 
        name = "{0} | {1}".format(weapon, skin)
    if st:
        name = "StatTrak™ " + name

    formatted_name = name.replace(" ", "%20") 
    formatted_name = formatted_name.replace("&", "%26")
    formatted_name = formatted_name.replace("|", "%7C")
    formatted_name = formatted_name.replace("+", "%2B")
    formatted_name = formatted_name.replace(":", "%3A")
    formatted_name = formatted_name.replace("/", "-")
    formatted_name = formatted_name.replace(",", "%2C")
    formatted_name = formatted_name.replace("(", "%28")
    formatted_name = formatted_name.replace(")", "%29")

    return formatted_name


# %%
other_history = {}
i = 0
current_num = 0
total_items = len(all_others.index)

for index, row in all_others.iterrows():
    current_num += 1
    if row["StatTrak"]:
        st_opt = (False, True)
    else:
        st_opt = (False,)
    
    for st in st_opt:
        time.sleep(random.uniform(.5, 3)) # avoid steam rate limiting with a random sleep
        name = make_others_hash(row["Weapon"], row["Skin"], st)
        price_vol_history = get_history(name)
        if price_vol_history == 1:
            print("{0} HAS FAILED".format(name))
            logging.warning("{0} HAS FAILED".format(name))
            continue
        col_index = "col_" + str(i)
        other_history[col_index] = [row["Weapon"], row["Collection"], row["Quality"], row["Skin"], None, st, None] + price_vol_history
        i += 1
    if current_num % 300 == 0: # saves the data to csv every 100 items to protect against crashes
        print("made a new file!")
        skins_prices = pd.DataFrame.from_dict(other_history, orient = "index")
        skins_prices.to_excel("others_query/others{}.xlsx".format(current_num / 300))
        other_history.clear()

if other_history != {}:
    print("finished!")
    logging.info("others finished!")
    skins_prices = pd.DataFrame.from_dict(other_history, orient = "index")
    skins_prices.to_excel("others_query/others_final2.xlsx")

# %% [markdown]
# ## Quick Data Cleaning
# 
# A majority of the data cleaning occurs during analysis but before then a multilevel index is added to help organize all the dates. The following cells iterate through each file of chunked up files to create one big dataframe where an index is added and saved as an overarching xlsx file.

# %%
# create a multilevel index for organizing the days
f = np.repeat([d.strftime("%Y-%m-%d") for d in dates_list], 2)
first_tier = ["Weapon", "Collection", "Quality", "Skin","Condition", "StatTrak", "Souvenir"]
second_tier = ["" for x in range(len(first_tier))] + [y for x in range(2602) for y in ["Price", "Volume"]]
first_tier.extend(f)
index = pd.MultiIndex.from_arrays([first_tier, second_tier])


# %%
# turns all skin files into one big data frame
path = r"D:\Code\steam_market_tracker\skins_query"
all_files = glob.glob(path + "/*.xlsx")

li = []

for filename in all_files:
    df = pd.read_excel(filename,index_col = 0, header = 0)
    li.append(df)

skins_history = pd.concat(li, axis = 0, ignore_index = True)

# %%
skins_history = skins_history.drop_duplicates()
skins_history.columns = index
skins_history.to_excel("datasets/all_skins.xlsx")
logging.info("skins concatenated!")

# %%
# turns all sticker files into one big data frame
path = r"D:\Code\steam_market_tracker\stickers_query"
all_files = glob.glob(path + "/*.xlsx")

li = []

for filename in all_files:
    df = pd.read_excel(filename, index_col = 0, header = 0)
    li.append(df)

stickers_history = pd.concat(li, axis = 0, ignore_index = True)
logging.info("stickers concatenated!")
# %%
stickers_history = stickers_history.drop_duplicates()
stickers_history.columns = index
stickers_history.to_excel("datasets/all_stickers.xlsx")

# %%
# turns all other files into one big data frame
path = r"D:\Code\steam_market_tracker\others_query"
all_files = glob.glob(path + "/*.xlsx")

li = []

for filename in all_files:
    df = pd.read_excel(filename, index_col = 0, header = 0)
    li.append(df)

others_history = pd.concat(li, axis = 0, ignore_index = True)

# %%
others_history = others_history.drop_duplicates()
others_history.columns = index
others_history.to_excel("datasets/all_others.xlsx")
logging.info("others concatenated!")
