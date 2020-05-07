from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import ButtonBehavior
from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.uix.modalview import ModalView
from kivy.factory import Factory
import kivy.utils
import json
import smtplib, ssl
from email.message import EmailMessage
import re
import os


class ImgButton(ButtonBehavior, Image):
    pass


class CustImage(Image):
    pass


class EnterPasswordPopup(ModalView):
    """
    A Popup to ask for password to send the selected report.

    ...

    Attributes
    ----------
    id_number : int
        To identify the report
    app : App class
        The base of the application

    Methods
    -------
    send_email(pw)
        Send e-mail using the SMTP-protocol
    """
    def __init__(self, id_number, **kwargs):
        """
        Parameters
        ----------
        id_number : int
            To identify the report
        """
        super(EnterPasswordPopup, self).__init__(**kwargs)
        self.id_number = id_number
        self.app = App.get_running_app()

    def send_email(self, pw, *args):
        """Send e-mail using the SMTP-protocol"""
        attachment = \
            (os.path.join(os.getcwd(),
                          'reports',
                          f'berichte-{self.app.year + 1}',
                          f"Nachweis_{self.id_number}.pdf"))
        # Details of Outgoing servers from some providers
        smtp_servers = {"gmail": ["smtp.gmail.com", 465],
                        "gmx": ["mail.gmx.net", 465],
                        "yahoo": ["smtp.mail.yahoo.com", 465],
                        "t-online": ["securesmtp.t-online.de", 465],
                        "1und1": ["smtp.1und1.de", 465],
                        "freenet": ["mx.freenet.de", 465],
                        "aol.com": ["smtp.de.aol.com", 465],
                        "aim": ["smtp.aim.com", 465],
                        "aol.de": ["smtp.aim.com", 465],
                        "arcor": ["mail.arcor.de", 465],
                        "eclipso": ['mail.eclipso.de', 465],
                        "firemail": ['firemail.de', 465],
                        "me": ['smtp.mail.me.com', 465],
                        "mail": ['smtp.mail.de', 465],
                        "mailbox": ['smtp.mailbox.org', 465],
                        "smart-mail": ['smtp.smart-mail.de', 465],
                        "outlook": ['smtp-mail.outlook.com', 587],
                        "netcologne": ['smtp.netcologne.de', 587],
                        "o2online": ['smtp.o2online.de', 587],
                        "web": ["smtp.web.de", 587],
                        "vodafone": ['smtp.vodafonemail.de', 587]}

        with open(os.path.join(os.getcwd(), 'data', 'Bh_data.json'), 'r') as f:
            data = json.load(f)
        # The SMTP-protocol has to be activated by the e-mail provider
        EMAIL_ADDR = data['record_book']['info']['trainee_email']

        EMAIL_PW = pw
        SERVER = ''
        PORT = ''

        pattern = re.compile(
            (r'(?<=[@|\.])(gmx|mail|1und1|freenet|vodafone|aim'
             r'|gmail|t-online|web|yahoo|outlook|aol|arcor|'
             r'|o2online|netcologne|smart-mail|mailbox|firemail|eclipso|me)'),
            re.I)
        match = pattern.search(EMAIL_ADDR)
        try:
            # get the right SERVER and PORT for the specific e-mail
            if match.group(0) == 'aol':
                tld = EMAIL_ADDR.split('.')[1]
                SERVER, PORT = smtp_servers[match.group(1)+'.'+tld]
            if match.group(0) in smtp_servers:
                SERVER, PORT = smtp_servers[match.group(1)]

            # create e-mail
            msg = EmailMessage()
            msg['Subject'] = (f'Nachweis Nr. {self.id_number} - '
                              f'Lehrjahr: {self.app.year+1}')
            msg['From'] = EMAIL_ADDR
            msg['To'] = data['record_book']['info']['trainer_email']

            msg.set_content(f"Sehr geehrter Herr "
                            f"{data['record_book']['info']['trainer_name']},\n"
                            "\nhier - wie gewünscht - der Nachweis"
                            f" Nr. {self.id_number} \n\nFreundliche Grüße "
                            f"\n{data['record_book']['info']['first_name']} "
                            f"{data['record_book']['info']['last_name']} "
                            "\n\n***Bitte speichern Sie die PDF im Dateipfad, "
                            "wo sich Ihre Berichtsheft-APP befindet, im "
                            f"Ordner 'Berichtsheft_Jahr-{self.app.year+1}'. "
                            "Also standard mäßig im Dateipfad "
                            "~/BerichtsHeft_APP/'Berichtsheft_Jahr"
                            f"-{self.app.year+1}***")
            # Create a secure SSL context
            # That means it will load the systems trusted CA certificates
            # and try to choose reasonably secure protocol and cipher settings
            context = ssl.create_default_context()

            # e-mail attachment
            doc = attachment
            try:
                with open(doc, 'rb') as f:
                    file_data = f.read()
                # Add attachment to e-mail
                msg.add_attachment(
                    file_data, maintype='application',
                    subtype='octet-stream',
                    filename=(f'Nachweis_{self.id_number}.pdf'))
            except IOError:
                error = (f"Nachweis Nr. {self.id_number} "
                         "existiert nicht.")
                self.app.update_banner_status(*self.app.temp_var)
                self.app.open_error_popup(error)

            # Use smtplib client to communicate with a remote SMTP server
            # from a specific provider
            try:
                if PORT == 465:
                    # Create a secure connection with the smtp server, using
                    # SMTP_SSL() to initiate a TLS-encrypted coonection.
                    # And the context of ssl validates the hostname and its
                    # certificates and optimizes the security of the
                    # connection.
                    with smtplib.SMTP_SSL(host=SERVER,
                                          port=PORT,
                                          context=context) as server:
                        server.login(EMAIL_ADDR, EMAIL_PW)
                        server.send_message(msg)
                else:
                    with smtplib.SMTP(host=SERVER, port=PORT) as server:
                        server.ehlo()  # to identify yourself to the server
                        server.starttls(context=context)
                        server.ehlo()
                        server.login(EMAIL_ADDR, EMAIL_PW)
                        server.send_message(msg)

            except smtplib.SMTPAuthenticationError:
                error = ("Bitte überprüfen Sie ihre E-Mail-Adresse und Ihr "
                         "dazu gehöriges Passwort bzw. sorgen Sie dafür, "
                         "dass bei ihrem E-Mail Provider das "
                         "SMTP-Protokoll nicht deaktiviert ist.")
                self.app.update_banner_status(*self.app.temp_var)
                self.app.open_error_popup(error)

        except Exception:
            error = "Der Provider Ihrer E-Mail-Adresse wird nicht unterstützt"
            self.app.update_banner_status(*self.app.temp_var)
            self.app.open_error_popup(error)


class ReportBanner(GridLayout):
    """
    Banner for a report from a specific calendar week in a year.

    ...

    Attributes
    ----------
    rows : int
        Number of rows in the GridLayout
    status : str
        File path to the status PNG
    id_number : int
        To identify the report
    c_w_number : int
        The calendar week number of the report
    total_hours : int
        The total number of hours worked
    app : App Class
        The base of the application
    rect : Rectangle
        A Class from the Kivy graphics module
    ScaleBtn : ScaleButton object
        A button that scales with the screen size

    Methods
    -------
    update_rect()
        Update the position and the size of the background
    permission()
        Open popup to ask for the e-mail password to send the report

    """
    def __init__(self, id_number, period, c_w_number,
                 status=os.path.join(os.getcwd(), 'icons',
                                     'notFilledOutSymbol.png'),
                 total_hours='??', **kwargs):
        super(ReportBanner, self).__init__(**kwargs)
        """
        Parameters
        ----------
        id_number : int
            To identify the PDF
        period : str
            Period from monday to the next friday of a specific calendar week
        c_w_number : int
            The calendar week number of the report
        status : str, optional
            File path to the status PNG
        total_hours : int, optional
            The total number of hours worked
        """
        self.rows = 1
        self.status = status
        self.id_number = id_number
        self.c_w_number = c_w_number       # calendar week number
        self.total_hours = total_hours
        self.app = App.get_running_app()
        self.ScaleBtn = Factory.ScaleButton

        with self.canvas.before:
            Color(rgb=(kivy.utils.get_color_from_hex("#4E4E4E")))
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.update_rect, size=self.update_rect)

        # left side of the banner
        banner_left = FloatLayout(size_hint_x=.8)
        cal_week = self.ScaleBtn(background_normal='',
                                 background_color=(0, .6, .2, 1),
                                 text=' KW %d ' % self.c_w_number,
                                 size_hint=(1, .6),
                                 font_size='1cm',
                                 pos_hint={"top": .9, "right": 1})
        cal_week.bind(on_press=lambda x: (self.app.change_screen(
                                                    "template_screen"),
                      self.app.check_report_number(self.id_number,
                                                   period)))
        period_of_time = self.ScaleBtn(
            background_normal='',
            background_down='',
            background_color=kivy.utils.get_color_from_hex("#4E4E4E"),
            text=(f' {period} '
                  f'Std.: {str(self.total_hours)}'),
            font_size='16sp',
            size_hint=(1, .3),
            pos_hint={"top": .3, "right": 1})
        banner_left.add_widget(cal_week)
        banner_left.add_widget(period_of_time)

        # right side of the banner
        banner_right = BoxLayout(padding=[10, 0, 10, 0], spacing=10)
        status_button = CustImage(source=self.status, size_hint=(1, .8),
                                  pos_hint={"top": .9, "right": 1})
        email_button = ImgButton()
        email_button.bind(on_press=lambda x: (self.app.update_banner_status(
                                              self.id_number,
                                              self.c_w_number)))
        banner_right.add_widget(status_button)
        banner_right.add_widget(email_button)

        self.add_widget(banner_left)
        self.add_widget(banner_right)

    def update_rect(self, *args):
        """Update the position and the size of the background."""
        self.rect.pos = self.pos
        self.rect.size = self.size

    def permission(self, *args):
        """Open popup to ask for the e-mail password to send the report."""
        if os.path.isfile(
            os.path.join(os.getcwd(), 'reports',
                         f'berichte-{self.app.year + 1}',
                         f"Nachweis_{self.id_number}.pdf")):
            self.app.valid_status = False
            EnterPasswordPopup(self.id_number).open()
        else:
            error = (f"Nachweis Nr. {self.id_number} "
                     "existiert nicht.")
            self.app.open_error_popup(error)
            self.app.update_banner_status(*self.app.temp_var)
