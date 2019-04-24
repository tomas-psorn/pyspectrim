import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class SignalPanel():
    def __init__(self, cinema):

        self.cinema = cinema
        self.app = self.cinema.app
        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, self.cinema)
        self.canvas.get_tk_widget().grid(column=1, row=0)
        self.canvas._tkcanvas.grid(column=1, row=0, padx=20)

        self.canvas.draw()

    def draw(self, image=None, dim_order=None):
        """
        This function works in two modes, if image and dim_order is specified, the concrete dimension of the concrete image is drawn
        otherwise, it draws first image
        :param image:
        :param dim_order:
        :return:
        """
        imagesList = self.app.contentTabs.imagesTab.get_visible()

        if not imagesList:
            self.draw_empty()
            return

        image = imagesList[0]

        for i in range(0,image.ndim):
            if image.dim_label[i] == 'temporal':
                x, y, x_label, y_label, legend = image.get_signal(dim_order=i)

        try:
            self.subplot.cla()
        except:
            self.subplot = self.figure.add_subplot(111)

        self.subplot.plot(x,y)
        self.subplot.set_xlabel(x_label)
        self.subplot.legend("HHZ 1", loc="upper right")
        self.canvas.draw()

    def draw_empty(self):

        try:
            self.subplot.cla()
            self.canvas.draw()
        except:
            pass