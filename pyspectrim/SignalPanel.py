import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class SignalPanel():
    def __init__(self, cinema):

        self.cinema = cinema
        self.app = self.cinema.app
        self.f = Figure(figsize=(5, 5), dpi=100)
        self.a = self.f.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.f, self.cinema)
        self.canvas.get_tk_widget().grid(column=0, row=0)
        self.canvas._tkcanvas.grid(column=0, row=0)

        self.canvas.draw()