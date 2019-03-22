from pyspectrim.ContextTabs import ContextTabs
from pyspectrim.ContentTabs import ContentTabs
from pyspectrim.Cinema import Cinema

import tkinter as tk
from tkinter import ttk
from tkinter import Menu




class PySpectrim():
    def __init__(self):

        self.root = tk.Tk()
        self.root.title("PySpectrim")
        self.root.geometry("%dx%d+0+0" % (self.root.winfo_screenwidth(), self.root.winfo_screenheight()))

        # Init main elements
        self.contentTabs = ContentTabs(self)
        self.contextTabs = ContextTabs(self)
        self.cinema = Cinema(self)

        # Set default layout
        self.setLayout()

        # Menus
        self.main_menu = Menu(self.root)
        self.root.config(menu=self.main_menu)
        self.file_menu = Menu(self.main_menu, tearoff=0)

        self.file_menu.add_command(label="Mount H5 file",command= lambda: self.contentTabs.filesTab.mounth5dir(self))
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self._quit)

        self.main_menu.add_cascade(label="File", menu=self.file_menu)

        self.loadIcons()

    def setLayout(self):
        self.cinema.grid(column=0, row=0, sticky=tk.N+tk.S+tk.E+tk.W)
        self.contentTabs.grid(column = 0, row = 1, sticky=tk.N+tk.S+tk.E+tk.W)
        self.contextTabs.grid(column = 1, row = 1, sticky=tk.N+tk.S+tk.E+tk.W)


    def _quit(self):
        self.root.quit()
        self.root.destroy()
        exit()

    def loadIcons(self):
        self.icons = {}
        self.icons['folder'] = tk.PhotoImage("icons/folder.gif").subsample(10,10)





if __name__ == "__main__":
    app = PySpectrim()
    app.root.mainloop()