import json
import sys
import requests
from lxml import html
import telebot


def scrapper(file_name):
    with open(file_name) as config_file:
        config = json.load(config_file)
        url = config["url"]
        apikey = config["telegramAPIKEY"]
        chatid = config["telegramCHATID"]
    r = requests.get(url)
    tree = html.fromstring(r.content)
    productlist = [curr.attrib["listingid"] for curr in tree.xpath('//*[@id="ListViewInner"]//li[@listingid]')]
    print(str(len(productlist)) + " products found!")
    idstr = '\n'.join(map(str, productlist))
    print(idstr)
    if apikey != "" and chatid != "":
        telebot.TeleBot(apikey).send_message(chatid, idstr)


if __name__ == '__main__':
    scrapper(sys.argv[1])
