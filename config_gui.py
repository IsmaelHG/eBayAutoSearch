import json
import os
import sys
import tkinter as tk


def cancelclick():
    sys.exit(0)


class GUI:
    def okclick(self):

        urls = []
        urls_text = self.urlentry.get("1.0", "end-1c")
        urls_lines = urls_text.split("\n")

        for url_line in urls_lines:
            if not url_line or len(url_line) < 2:
                break

            url_line = url_line.strip().split(" ")

            url_name = url_line[0] if len(url_line) > 1 else None
            url_url = url_line[1] if url_name else url_line[0]

            urls.append({"name": url_name, "url": url_url})

        data = {"urls": urls,
                "telegramAPIKEY": self.apikeyentry.get(),
                "telegramCHATID": self.chatidentry.get(),
                "databaseFile": self.databaseentry.get(),
                "sleep": self.sleepeentry.get()
                }
        with open(self.file_name, 'w') as config_file:
            json.dump(data, config_file)
        config_file.close()
        self.window.destroy()
        pass

    def __init__(self, file_name):
        self.file_name = file_name
        self.window = tk.Tk()
        self.window.geometry('706x550')

        urllabel = tk.Label(text="urls (one per line)")
        urlscroll = tk.Scrollbar(self.window, orient=tk.VERTICAL)
        self.urlentry = tk.Text(width=100, height=16)
        self.urlentry.configure(yscrollcommand=urlscroll.set)

        databaselabel = tk.Label(text="databaseFile")
        self.databaseentry = tk.Entry(width=100, justify="center")

        apikeylabel = tk.Label(text="telegramAPIKEY")
        self.apikeyentry = tk.Entry(width=100, justify="center")

        chatidlabel = tk.Label(text="telegramCHATID")
        self.chatidentry = tk.Entry(width=100, justify="center")

        sleeplabel = tk.Label(text="sleep")
        self.sleepeentry = tk.Entry(width=100, justify="center")

        okbutton = tk.Button(self.window, text="OK", command=self.okclick)
        cancelbutton = tk.Button(self.window, text="Cancel", command=cancelclick)

        urllabel.grid(column=0, row=0)
        self.urlentry.grid(column=0, row=1)

        databaselabel.grid(column=0, row=2)
        self.databaseentry.grid(column=0, row=3)

        apikeylabel.grid(column=0, row=4)
        self.apikeyentry.grid(column=0, row=5)

        chatidlabel.grid(column=0, row=6)
        self.chatidentry.grid(column=0, row=7)

        sleeplabel.grid(column=0, row=8)
        self.sleepeentry.grid(column=0, row=9)

        okbutton.grid(column=0, row=10)
        cancelbutton.grid(column=0, row=11)

        if os.path.isfile(file_name):
            with open(file_name) as config_file:
                config = json.load(config_file)

                # Get array of urls to scrape or fallback to single url
                urls = config.get("urls")
                if not urls:
                    url = config["url"]
                    urls = [{"url": url}]
                
                url_text = ""
                for url in urls:
                    url_text += f'{(url["name"] + " ") if "name" in url else ""}{url["url"]}' + "\n"
                self.urlentry.insert(tk.END, url_text)

                self.apikeyentry.insert(0, config["telegramAPIKEY"])
                self.chatidentry.insert(0, config["telegramCHATID"])
                self.databaseentry.insert(0, config["databaseFile"])
                self.sleepeentry.insert(0, config["sleep"])
            config_file.close()
        else:
            self.databaseentry.insert(0, "database.db")
            self.sleepeentry.insert(0, "10")

        self.window.mainloop()
        try:
            self.window.update()
        except Exception:
            pass
