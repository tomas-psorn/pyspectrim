import time
import threading
import logging

import tkinter as tk  # Python 3.x
import tkinter.scrolledtext as ScrolledText

# taken from https://gist.github.com/bitsgalore/901d0abe4b874b483df3ddc4168754aa

class TextHandler(logging.Handler):
    # This class allows you to log to a Tkinter Text or ScrolledText widget
    # Adapted from Moshe Kaplan: https://gist.github.com/moshekaplan/c425f861de7bbf28ef06

    def __init__(self, text):
        # run the regular Handler __init__
        logging.Handler.__init__(self)
        # Store a reference to the Text it will log to

        self.text = text

    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text.configure(state='normal')
            self.text.insert(tk.END, msg + '\n')
            self.text.configure(state='disabled')
            # Autoscroll to the bottom
            self.text.yview(tk.END)
        # This is necessary because we can't modify the Text from other threads
        self.text.after(0, append)

class LoggerTab(tk.Frame):
    def __init__(self, contextTabs, *args, **kwargs):
        self.contextTabs = contextTabs

        super().__init__(self.contextTabs)

        self.contextTabs.add(self, text="Log")
        self.layout = tk.LabelFrame(self, text='Log')

        self.layout.grid(column=0, row=0, sticky='ew')
        self.layout.grid_columnconfigure(0, weight=1, uniform='a')
        self.layout.grid_columnconfigure(1, weight=1, uniform='a')
        self.layout.grid_columnconfigure(2, weight=1, uniform='a')
        self.layout.grid_columnconfigure(3, weight=1, uniform='a')

        # Add text widget to display logging info
        st = ScrolledText.ScrolledText(self.layout, state='disabled')
        st.configure(font='TkFixedFont')
        st.grid(column=0, row=1, sticky='w', columnspan=4)

        # Create textLogger
        text_handler = TextHandler(st)

        logging.basicConfig(filename='test.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s')

        # Add the handler to logger
        logger = logging.getLogger()
        logger.addHandler(text_handler)
