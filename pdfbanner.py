from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.factory import Factory
import os.path
import webbrowser as wb
import kivy.utils


class PdfBanner(GridLayout):
    """
    Creates a banner for a PDF

    ...

    Attributes
    ----------
    rows : int
        Number of rows in the GridLayout
    id_number : int
        To identify the PDF
    year : int
        The apprenticeship year
    c_w_number : int
        The calendar week number of the report
    app : App class
        The base of the application
    rect : Rectangle
        A class from the Kivy graphics module
    ShowReport : ScaleButton object
        A button to open the selected report

    Methods
    -------
    update_rect()
        Updates the position and the size of the background
    open_finalized_pdf()
        Opens the selected PDF file
    """
    def __init__(self, id_number, year, c_w_number, **kwargs):
        super(PdfBanner, self).__init__(**kwargs)
        """
        Parameters
        ----------
        id_number : int
            To identify the PDF
        year : int
            The apprenticeship year
        c_w_number : int
            The calendar week number of the report
        ShowReport : ScaleButton
            A button to open the selected report
        """
        self.rows = 1
        self.id_number = id_number
        self.c_w_number = c_w_number     # calendar week number
        self.year = year
        self.app = App.get_running_app()
        self.ShowReport = Factory.ScaleButton
        with self.canvas.before:
            Color(rgb=(kivy.utils.get_color_from_hex("#e4e4e4")))
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.update_rect, size=self.update_rect)

        banner = FloatLayout()
        cw = self.ShowReport(background_normal='',
                             background_color=(0, 0.6, 0.2, 1),
                             text=' Öffne KW %d ' % self.c_w_number,
                             size_hint=(.7, .6), font_size='1cm',
                             pos_hint={"top": 0.8, "x": .15},
                             on_press=self.open_finalized_pdf)
        banner.add_widget(cw)
        self.add_widget(banner)

    def update_rect(self, *args):
        """Update the position and the size of the background."""
        self.rect.pos = self.pos
        self.rect.size = self.size

    def open_finalized_pdf(self, *args):
        """Open the selected PDF file."""
        pdf = 'test%d.pdf' % self.id_number
        b = 'fertige-berichte-%d' % self.year
        if os.path.isfile(os.path.join(os.getcwd(), 'reports', b, pdf)):
            try:
                wb.get()
                wb.open_new(rf"{os.path.join('.', b, pdf)}")
            except Exception:
                self.app.open_error_popup("Es konnte kein ausführbarer Browser"
                                          " gefunden werden.")
        else:
            self.app.open_error_popup(f"PDF mit dem namen '{pdf}' konnte nicht"
                                      f" im Ordner '{b}' gefunden werden.")
