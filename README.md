# Basic eBay Scraper

This is a pretty basic python script designed for getting every eBay product identifier from a specific search.
The id list will be printed on console and also can be sent to a telegram account as a text message. This scraper only analyzes the first page of an eBay search, so it can only get the id of up to 200 items


To execute this script, just run "python scraper.py config.json"

config.json will be a path to a json file that contains the eBay search url, the telegram bot API Key 
and the telegram chatid that is going to receive the message. This two previous parameters are 
optional so you can just specify them as an empty string (""). Check the [example config](example.json) for reference

    eBay search URL can be get by just making a search with any filter you want (max price, location, only bids, etc)
    and copying the browser URL

    Telegram API Key is retrieved when you create a new telegram bot on @BotFather

    The telegram chatid can be retrieved when you send a message to @userinfobot on telegram

### Pre-requirements 📋

You can quickly install all the requirements (lxml, requests, pyTelegramBotAPI) by using the well known 

```
pip install -r requirements.txt
```

I'm developing this script for learning purposes so the script functionality may vastly change on the following weeks

### TODO
* Make the script search for multiple pages

