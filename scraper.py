import json
import sys
import time

import requests
from lxml import html
import telebot
import sqlite3
from sqlite3 import Error


def sql_connection(file_name):
    try:
        con = sqlite3.connect(file_name)
        return con
    except Error:
        print(Error)


def scrapper(url, apikey, chatid, con, sleep):
    cursor = con.cursor()

    while True:
        # Load and parse the html from the ebay search page
        r = requests.get(url)
        tree = html.fromstring(r.content)

        # Get all the html elements that fulfill this xpath expression: //*[@id="ListViewInner"]//li[@listingid]
        # and also parse the value from the field "listingid" to obtain every product id
        productlist = [curr.attrib["listingid"] for curr in tree.xpath('//*[@id="ListViewInner"]//li[@listingid]')]

        # Convert the list as a string and print it, every element is separated by a new-line
        # save to database
        for prodstr in productlist:
            try:
                cursor.execute("INSERT INTO identifiers(id) VALUES(?)", (prodstr,))
                print(prodstr)
                # If the user specified a telegram bot apikey + chatid, it will send the previously printed list as a text message
                if apikey != "" and chatid != "":
                    try:
                        telebot.TeleBot(apikey).send_message(chatid, "https://ebay.es/itm/" + prodstr)
                        time.sleep(0.3)
                    except telebot.apihelper.ApiTelegramException:
                        pass
            except sqlite3.IntegrityError:
                pass
        con.commit()
        time.sleep(int(sleep))
    con.close()


if __name__ == '__main__':
    # Obtain parameters from the json file
    # User must specify the file path as the first argument when running this script
    with open(sys.argv[1]) as config_file:
        config = json.load(config_file)
        url = config["url"]
        apikey = config["telegramAPIKEY"]
        chatid = config["telegramCHATID"]
        dbname = config["databaseFile"]
        sleep = config["sleep"]

    # Connect to db
    con = sql_connection(dbname)
    cursor = con.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS identifiers(id VARCHAR(12) PRIMARY KEY)")
    con.commit()

    scrapper(url, apikey, chatid, con, sleep)
