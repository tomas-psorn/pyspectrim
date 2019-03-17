import tkinter as tk
from tkinter import ttk



class ImagesTab():
    def __init__(self, pyspectrim):
        self.frame = tk.Frame(pyspectrim.contentTabs)
        pyspectrim.contentTabs.add(self.frame, text="Images")

        self.imagesTree = ttk.Treeview(self.frame)
        self.imagesTree.config(columns=('size'))

        self.imagesTree.column('#0', width=150)
        self.imagesTree.column('size', width=150)

        self.imagesTree.heading('#0', text='Name')
        self.imagesTree.heading('size', text='Size')

        self.imagesTree.pack()

    def insertImage(self):
        self.imagesTree.insert('','0','item1', text='Image1')
        self.imagesTree.set('item1','size','128x128x25')