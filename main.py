import json
import sys
import requests
from lxml import html
import telebot


def scrapper(file_name):
    # Obtain parameters from the json file
    with open(file_name) as config_file:
        config = json.load(config_file)
        url = config["url"]
        apikey = config["telegramAPIKEY"]
        chatid = config["telegramCHATID"]

    # Load and parse the html from the ebay search page
    r = requests.get(url)
    tree = html.fromstring(r.content)

    # Get all the html elements that fulfill this xpath expression: //*[@id="ListViewInner"]//li[@listingid]
    # and also parse the value from the field "listingid" to obtain every product id
    productlist = [curr.attrib["listingid"] for curr in tree.xpath('//*[@id="ListViewInner"]//li[@listingid]')]

    print(str(len(productlist)) + " products found!")
    # Convert the list as a string and print it, every element is separated by a new-line
    idstr = '\n'.join(map(str, productlist))
    print(idstr)

    # If the user specified a telegram bot apikey + chatid, it will send the previously printed list as a text message
    if apikey != "" and chatid != "":
        telebot.TeleBot(apikey).send_message(chatid, idstr)


if __name__ == '__main__':
    # User must specify the file path as the first argument when running this script
    scrapper(sys.argv[1])
