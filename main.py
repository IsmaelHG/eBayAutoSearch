import sys
import requests
from lxml import html


def scrapper(url):
    r = requests.get(url)
    tree = html.fromstring(r.content)
    productlist = [curr for curr in tree.xpath('//*[@id="ListViewInner"]//li[@listingid]')]
    print(str(len(productlist))+" products found!")
    for product in productlist:
        print(product)


if __name__ == '__main__':
    scrapper(sys.argv[1])
