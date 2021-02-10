import json
import os
import tkinter as tk


def cancelclick():
    exit(0)


class GUI:
    def okclick(self):
        data = {"url": self.urlentry.get(),
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
        self.window.geometry('605x300')

        urllabel = tk.Label(text="url")
        self.urlentry = tk.Entry(width=100, justify=tk.CENTER)

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
                self.urlentry.insert(0, config["url"])
                self.apikeyentry.insert(0, config["telegramAPIKEY"])
                self.chatidentry.insert(0, config["telegramCHATID"])
                self.databaseentry.insert(0, config["databaseFile"])
                self.sleepeentry.insert(0, config["sleep"])
            config_file.close()

        self.window.mainloop()
