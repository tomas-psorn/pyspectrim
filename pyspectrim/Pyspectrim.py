from pyspectrim.ImagesTab import ImagesTab
from pyspectrim.FilesTab import FilesTab
from pyspectrim.ImagePanel import ImagePanel

import tkinter as tk
from tkinter import ttk
from tkinter import Menu



class PySpectrim():
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PySpectrim")

        self.contentTabs = ttk.Notebook(self.root)
        self.contextTabs = ttk.Notebook(self.root)

        self.contentTabs.grid(column = 0, row = 1)
        self.contextTabs.grid(column = 1, row = 1)

        self.filesTab = FilesTab(self)
        self.imagesTab = ImagesTab(self)

        self.createPositionTab()

        self.imagePanel = ImagePanel(self)

        self.main_menu = Menu(self.root)
        self.root.config(menu=self.main_menu)
        self.file_menu = Menu(self.main_menu, tearoff=0)

        self.file_menu.add_command(label="Mount H5 dir",command= lambda: self.filesTab.mounth5dir(self))
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self._quit)

        self.main_menu.add_cascade(label="File", menu=self.file_menu)

        self.loadIcons()



    def _quit(self):
        self.root.quit()
        self.root.destroy()
        exit()

    def loadIcons(self):
        self.icons = {}
        self.icons['folder'] = tk.PhotoImage("icons/folder.gif").subsample(10,10)


    def createPositionTab(self):
        self.positionTab = tk.Frame(self.contextTabs)
        self.contextTabs.add(self.positionTab, text="Position")



if __name__ == "__main__":
    app = PySpectrim()
    app.root.mainloop()