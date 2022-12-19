from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime

import time
from pathlib import Path

import pandas as pd

TIME_OUT = 20

# chrome driver
service_obj = Service("./chromedriver")
driver = webdriver.Chrome(service=service_obj)


def concat_new_data_to_csv(new_data: list):
    df = pd.read_csv('data.csv')
    df2 = pd.DataFrame(new_data)
    df_merged = pd.concat([df, df2], ignore_index=True)
    df_merged.to_csv('data.csv', index=False)


def get_stock_price_to_dict(dictionary: list, stock: str):
    list_date = driver.find_elements(By.CLASS_NAME, "Item_DateItem")
    list_closing_price = driver.find_elements(By.XPATH, "(//tr//td[contains(@class, 'Item_Price10')][2])")
    for index, date in enumerate(list_date):
        dictionary.append(
            {"stock_name": stock, "date": datetime.strptime(date.text.strip(), '%d/%m/%Y').strftime('%m/%d/%Y'),
             "closing_price": list_closing_price[index].text.strip()})


def get_closing_price_of_stock_symbol(stock: str):
    driver.get("https://s.cafef.vn/Lich-su-giao-dich-" + stock + "-1.chn")

    # Input date range from 1/1/2019 to 1/12/2022 and click search to show all history price base on this date range
    date_start = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_ctl03_dpkTradeDate1_txtDatePicker")
    date_start.send_keys('1/1/2019')

    date_end = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_ctl03_dpkTradeDate2_txtDatePicker")
    date_end.send_keys('1/12/2022')

    search_btn = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_ctl03_btSearch")
    search_btn.click()

    time.sleep(1)

    res = list()
    get_stock_price_to_dict(res, stock)

    # Next page to the end
    while True:
        try:
            next_btn = driver.find_element(By.XPATH, "(//a[contains(@title,'Next to Page ')])[1]")
        except NoSuchElementException:
            print("end tasks")
            break
        next_btn.click()
        time.sleep(1.5)
        get_stock_price_to_dict(res, stock)

    print(res)
    return res


driver.get("https://quotes.vcbs.com.vn/a/exchange.html")

time.sleep(1.5)

# Get 100 stock symbols to a list name allSymbols
allSymbolsElement = driver.find_elements(By.XPATH, "//tr[@class='BorderBottom RowHeight']/td[4]")
allSymbols = [symbols.text for symbols in allSymbolsElement]

# Open valid and invalid file then remove its symbols from allSymbols list to reduce time crawling
if Path('valid.txt').is_file():
    with open('valid.txt', 'r') as fr:
        x = fr.read().split('\n')
        print('valid', x)
        allSymbols = list(set(allSymbols) - set(x))

if Path('invalid.txt').is_file():
    with open('invalid.txt', 'r') as fr:
        y = fr.read().split('\n')
        print('invalid', y)
        allSymbols = list(set(allSymbols) - set(y))

print(allSymbols)
invalid_list = list()
valid_list = list()

for i in allSymbols:
    # Re-open the valid.txt file to check the length every single iteration
    if Path('valid.txt').is_file():
        with open('valid.txt', 'r') as fr:
            valid_symbols = fr.read().split('\n')

    # If the length of valid list match 100 symbols. Break the loop.
    if len(valid_symbols) == 100:
        break

    a = get_closing_price_of_stock_symbol(i)

    # If closing price of stock i has more than 970 days
    # then concat that result to csv file and append the symbol to valid.txt
    # else append the symbol to invalid.txt
    if len(a) > 970:
        concat_new_data_to_csv(a)
        valid_list.append(i)
        with open('valid.txt', 'w') as fw:
            op = x + valid_list
            for item in op:
                fw.write("%s\n" % item)
        print("valid: ", a)
    else:
        invalid_list.append(i)
        with open('invalid.txt', 'w') as fw:
            op = y + invalid_list
            for item in op:
                fw.write("%s\n" % item)
        print("invalid: ", a)


def convert_raw_data_to_pivot_table():
    df = pd.read_csv('data.csv')
    df_horizontal_symbols = pd.pivot_table(df,
                                           index='date',
                                           columns='stock_name',
                                           values='closing_price',
                                           aggfunc={
                                               'closing_price': lambda x: set(x).pop()
                                           }
                                           ).fillna(method='bfill')

    df_horizontal_symbols.to_csv('result.csv')
