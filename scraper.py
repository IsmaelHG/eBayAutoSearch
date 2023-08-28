import argparse
import datetime
import json
import re
import sqlite3
import time
from signal import signal, SIGINT
from sqlite3 import Error
from sys import exit
from urllib.parse import urlparse

import requests
from lxml import html

import config_gui

global con

MAX_RETRIES = 5
RESTART_TIME = 10


def sendTelegram(msg, idchat, token):
    requests.post('https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + idchat + '&text=' + msg,
                  timeout=20)


class TooManyConnectionRetries(Exception):
    pass


def exit_handler(signal_received, frame):
    global con
    print("CTRL-C Pressed, exiting...")
    try:
        # Safely close the database connection and exit the application
        con.close()
    except Exception:
        pass
    exit(0)


def sql_connection(file_name):
    try:
        conbd = sqlite3.connect(file_name)
        return conbd
    except Error:
        print(Error)


def scraper(urls, apikey, chatid, sleep):
    global con
    cursordb = con.cursor()

    # Infinite loop, safe way to close the program is to send a SIGINT signal (CTRL-C)
    while True:
        # Loop over every URL to scrape
        for url_item in urls:
            url = url_item.get("url")
            name = url_item.get("name")

            if name:
                print(f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] Scraping for {name}")

            # Load and parse the html from supplied ebay search page
            # If it raises an connectionerror, it will retry a few times
            for i in range(MAX_RETRIES):
                try:
                    r = requests.get(url)
                except requests.exceptions.ConnectionError:
                    print("Connection Error: Please check your internet connection")
                    print("Retrying in " + sleep + " seconds (" + str(i) + "/" + str(MAX_RETRIES) + ")")
                    time.sleep(int(sleep))
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
                productlist = [
                    (re.findall("\d{12}", curr.xpath('.//*[contains(@class,"s-item__link")]')[0].attrib["href"])[0],
                    curr.xpath('.//*[contains(@class,"s-item__price")]')[0].text_content().replace("\n", "").replace("\t",
                                                                                                                    ""))
                    for curr in tree.xpath('//*[contains(@class,"s-item__info clearfix") and ./a]') if
                    len(re.findall("\d{12}", curr.xpath('.//*[contains(@class,"s-item__link")]')[0].attrib["href"])) > 0]
            else:
                # ListViewInner
                productlist = [(curr.attrib["listingid"],
                                curr.xpath('.//*[contains(@class,"lvprice prc")]//*[contains(@class,"bold")]')[
                                    0].text_content().replace("\n", "").replace("\t", "")) for curr in
                            tree.xpath('//*[contains(@class,"sresult lvresult clearfix li")]')]

            # Insert every id into the database table
            # If the id is already present on the table, cursor.execute() will raise an sqlite3.IntegrityError exception which will skip the process of sending the link
            # as a telegram message
            for prodstr in productlist:
                try:
                    # Insert the id and the timestamp
                    cursordb.execute("INSERT INTO identifiers(id,listingDate) VALUES(?,?)",
                                    (prodstr[0], datetime.datetime.now()))

                    # Print the listing url based on the identifier
                    print("https://" + urlparse(url).netloc + "/itm/" + prodstr[0])
                    print(prodstr[1])

                    # If the user specified a telegram bot apikey + chatid, it will send the previously printed list as a text message (only if the previous line didn't produce an exception)
                    if apikey != "" and chatid != "":
                        try:
                            sendTelegram("https://" + urlparse(
                                url).netloc + "/itm/" + prodstr[
                                            0] + "\n" + prodstr[1], chatid, apikey)
                            # Telegram API limits the number of messages per second so we need to wait a little bit
                            time.sleep(0.5)
                        except Exception:
                            pass
                except sqlite3.IntegrityError:
                    # When this exception rises, the program will just continue to the next element of the for-loop
                    pass
            con.commit()
            # Wait before repeting the process

        time.sleep(int(sleep))


def startup(filename_path):
    global con
    # Obtain parameters from the json file
    # User must specify the file path as an argument when running this script
    with open(filename_path) as config_file:
        config = json.load(config_file)

        # Get array of urls to scrape or fallback to single url
        urls = config.get("urls")
        if not urls:
            url = config["url"]
            urls = [{"url": url}]

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
    scraper(urls, apikey, chatid, sleep)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-nogui", "--nogui", action="store_true")
    parser.add_argument("-path", metavar="--path",
                        type=str,
                        default="config.json",
                        required=False,
                        help="the path to the config file (defaults to config.json)")

    options = parser.parse_args()
    filename = options.path
    if not options.nogui:
        config_gui.GUI(filename)

    # There must be a better way
    while True:
        try:
            startup(filename)
        except Exception as e:
            print(e)
            print("Restarting the application in " + str(RESTART_TIME) + " seconds")
            time.sleep(RESTART_TIME)
            try:
                con.close()
            except Exception:
                pass
