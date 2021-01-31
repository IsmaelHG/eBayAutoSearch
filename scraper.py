import json
import sys
import time
import requests
import telebot
import sqlite3
import re
import datetime
import config_gui
from urllib.parse import urlparse
from lxml import html
from sqlite3 import Error
from signal import signal, SIGINT
from sys import exit

global con

MAX_RETRIES = 5


class TooManyConnectionRetries(Exception):
    pass


def exit_handler(signal_received, frame):
    print("CTRL-C Pressed, exiting...")
    try:
        # Safely close the database connection and exit the application
        con.close()
    except Exception:
        pass
    exit(0)


def sql_connection(file_name):
    try:
        con = sqlite3.connect(file_name)
        return con
    except Error:
        print(Error)


def scraper(url, apikey, chatid, sleep):
    cursordb = con.cursor()

    # Infinite loop, safe way to close the program is to send a SIGINT signal (CTRL-C)
    while True:
        # Load and parse the html from supplied ebay search page
        # If it raises an connectionerror, it will retry a few times
        for i in range(MAX_RETRIES):
            try:
                r = requests.get(url)
            except requests.exceptions.ConnectionError:
                print("Connection Error: Please check your internet connection")
                print("Retrying in " + sleep + " seconds (" + str(i) + "/" + str(MAX_RETRIES) + ")")
                continue
            else:
                break
        else:
            # The scraper will raise an exception if it exceeds the max number of connection retries (MAX_RETRIES)
            raise TooManyConnectionRetries

        tree = html.fromstring(r.content)

        # Obtain every listing id
        # eBay has two ways showing the listings, one is to show the listing with a "srp-results" class
        # and another is by using "ListViewInner" class
        if "srp-results" in r.text:
            # srp-results
            productlist = [re.findall("\d{12}", curr.attrib["href"])[0] for curr in
                           tree.xpath('//*[contains(@class,"s-item__link")]')]
        else:
            # ListViewInner
            productlist = [curr.attrib["listingid"] for curr in tree.xpath('//*[@id="ListViewInner"]//li[@listingid]')]

        # Insert every id into the database table
        # If the id is already present on the table, cursor.execute() will raise an sqlite3.IntegrityError exception which will skip the process of sending the link
        # as a telegram message
        for prodstr in productlist:
            try:
                # Insert the id and the timestamp
                cursordb.execute("INSERT INTO identifiers(id,listingDate) VALUES(?,?)",
                               (prodstr, datetime.datetime.now()))

                # Print the listing url based on the identifier
                print("https://" + urlparse(url).netloc + "/itm/" + prodstr)

                # If the user specified a telegram bot apikey + chatid, it will send the previously printed list as a text message (only if the previous line didn't produce an exception)
                if apikey != "" and chatid != "":
                    try:
                        telebot.TeleBot(apikey).send_message(chatid,
                                                             "https://" + urlparse(url).netloc + "/itm/" + prodstr)
                        # Telegram API limits the number of messages per second so we need to wait a little bit
                        time.sleep(0.5)
                    except telebot.apihelper.ApiTelegramException:
                        pass
            except sqlite3.IntegrityError:
                # When this exception rises, the program will just continue to the next element of the for-loop
                pass
        con.commit()
        # Wait before repeting the process
        time.sleep(int(sleep))


if __name__ == '__main__':
    config_gui.GUI(sys.argv[1])

    # Obtain parameters from the json file
    # User must specify the file path as an argument when running this script
    with open(sys.argv[1]) as config_file:
        config = json.load(config_file)
        url = config["url"]
        apikey = config["telegramAPIKEY"]
        chatid = config["telegramCHATID"]
        dbname = config["databaseFile"]
        sleep = config["sleep"]

    config_file.close()
    # Connect to db and create the table (if not exists)
    con = sql_connection(dbname)
    cursor = con.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS identifiers(id VARCHAR(12) PRIMARY KEY, listingDate timestamp)")
    con.commit()

    # Start the exit handler
    signal(SIGINT, exit_handler)

    # Start the scraper
    scraper(url, apikey, chatid, sleep)
