from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.uix.colorpicker import ColorPicker
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from custwidgets import ImageButton
from kivy.factory import Factory
import os.path
import kivy.utils


class ColPcker(ColorPicker):
    pass


class ColorPickerPopup(Popup):
    """
    Popup with color picker

    ...

    Attributes
    ----------
    design_num : int
        The selected design
    """
    def __init__(self, design_num, **kwargs):
        super(ColorPickerPopup, self).__init__(**kwargs)
        """
        Parameters
        ----------
        design_num : int
            The selected design
        """
        self.design_num = design_num


class DesignBanner(GridLayout):
    """
    Banner to optionally changing the report design

    ...

    Attributes
    ----------
    rows : int
        Number of rows in the GridLayout
    app : App class
        The base of the application
    design_num : int
        The selected design
    rect : Rectangle
        A class from the Kivy graphics module
    Design0 : Design0 object (inherits from Widget)
        the first design option
    Design1 : Design1 object (inherits from Widget)
        The second design option
    WhiteBox : WhiteBox object (inherits from Widget)
        A white rectangle
    CheckBox : CustCheckBox object (inherits from Widget)
        A check box to choose a design for the reports

    Methods
    -------
    update_rect()
        Update the position and the size of the background
    """
    def __init__(self, design_num, **kwargs):
        """
        Parameters
        ----------
        design_num : int
            The selected design
        """
        self.rows = 1
        self.app = App.get_running_app()
        self.design_num = design_num
        self.Design0 = Factory.Design0
        self.Design1 = Factory.Design1
        self.WhiteBox = Factory.WhiteBox
        self.CheckBox = Factory.CustCheckBox

        super(DesignBanner, self).__init__(**kwargs)

        with self.canvas.before:
            Color(rgb=(kivy.utils.get_color_from_hex("#e4e4e4")))
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.update_rect, size=self.update_rect)
        Img = FloatLayout()
        if design_num == 0:
            design = self.Design0(size_hint=(None, None), size=(200, 62),
                                  pos_hint={"top": .9, "center_x": 0.5})
            wb = self.WhiteBox(size_hint=(None, None), size=(200, 50),
                               pos_hint={"top": .8, "center_x": 0.5})
            Img.add_widget(wb)
        if design_num == 1:
            design = self.Design1(size_hint=(None, None), size=(200, 100),
                                  pos_hint={"top": .9, "center_x": 0.5})

        Design_form = Image(source=os.path.join(os.getcwd(), 'icons', 'Nachweis.png'),
                            pos_hint={"top": .9, "center_x": .5},
                            size_hint=(1, .8), width=200)
        select_design = self.CheckBox(
            pos_hint={"top": .27, "right": .95},
            group='select_design')
        select_design.bind(
            on_press=lambda x: (self.app.apply_design(
                self.design_num,
                select_design.state
                ))
            )

        btn = ImageButton(source=os.path.join(os.getcwd(), 'icons', 'colorRing.png'),
                          size_hint=(.2, .2),
                          pos_hint={"top": .3, "x": 0})
        btn.bind(
            on_release=lambda x: (ColorPickerPopup(self.design_num).open()))
        Img.add_widget(design)
        Img.add_widget(Design_form)
        Img.add_widget(select_design)
        Img.add_widget(btn)

        self.add_widget(Img)

    def update_rect(self, *args):
        """Update the position and the size of the background"""
        self.rect.pos = self.pos
        self.rect.size = self.size
