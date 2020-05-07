from kivy.app import App
from kivy.uix.modalview import ModalView
import os.path
import imaplib
import email
import os
import re
import json
import threading
import time
import datetime as dt
from reportbanner import ReportBanner
from kivy.clock import mainthread
from kivy.factory import Factory


class CheckEmailsPopup(ModalView):
    """
    Checks the mailbox and downloads the files in the mails from the trainer.

    ...
    Attributes
    ----------
    app : App Class
        The base of the application
    con : imaplib.IMAP4_SSL object
        This is a subclass derived from IMAP4 that connects over an SSL
        encrypted socket.
    year : int
        The apprenticeship year
    imap_servers : dict
        Contains a bunch of imap server addresses

    Methods
    -------
    connect()
        Create a connection to the imap
    remove_update_button()
        Remove the update button from the home screen
    add_update_button()
        Add a update button to the home screen
    start_checking()
        Check the inbox for new reports
    check_email()
        Iterate over all payloads of the new received emails and downloads
        attached pdf files
    search(c1, c2, val1)
        Search for the specific emails
    report_rejected(num)
        Change status of the specific calendar week
    get_emails()
        Get the specific emails from the trainer
    get_email_body(msg)
        Get the body of the email
    get_attachments(msg, check)
        Get the pdf file of the email
    decode_mime_header(s)
        Decode the encoded chunks (encoded-words)
    """
    def __init__(self, **kwargs):
        super(CheckEmailsPopup, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.con = None
        self.year = 1
        self.imap_servers = {"gmail": "imap.gmail.com",
                             "gmx": "imap.gmx.net",
                             "yahoo": "imap.mail.yahoo.com",
                             "t-online": "secureimap.t-online.de",
                             "freenet": "mx.freenet.de",
                             "1und1": "imap.1und1.de",
                             "mail": "imap.mail.de",
                             "aol.com": "imap.de.aol.com",
                             "aim": "imap.aim.com",
                             "aol.de": "imap.aim.com",
                             "arcor": "imap.arcor.de",
                             "eclipso": 'mail.eclipso.de',
                             "firemail": 'firemail.de',
                             "me": 'imap.mail.me.com',
                             "mailbox": 'imap.mailbox.org',
                             "smart-mail": 'imap.smart-mail.de',
                             "outlook": 'imap-mail.outlook.com',
                             "netcologne": 'imap.netcologne.de',
                             "o2online": 'imap4.o2online.de',
                             "web": "imap.web.de",
                             "vodafone": 'imap.vodafonemail.de'}

    def connect(self, pw):
        """Create a connection to the imap server."""
        incoming_mail_server = ''
        pattern = re.compile(
            (r'(?<=[@|\.])(gmx|mail|1und1|freenet|vodafone|aim'
             r'|gmail|t-online|web|yahoo|outlook|aol|arcor|'
             r'|o2online|netcologne|smart-mail|mailbox|firemail|eclipso|me)'),
            re.I)
        try:
            # get the right SERVER for the specific e-mail
            match = pattern.search(self.app.MY_EMAIL)
            if match.group(0) == 'aol':
                tld = self.app.MY_EMAIL.split('.')[1]
                incoming_mail_server = \
                    self.imap_servers[match.group(1)+'.'+tld]
            if match.group(0) in self.imap_servers:
                incoming_mail_server = self.imap_servers[match.group(1)]
                try:
                    self.con = imaplib.IMAP4_SSL(incoming_mail_server)
                    self.con.login(self.app.MY_EMAIL, pw)
                    # Check if there is a new email
                    threading.Thread(target=self.start_checking,
                                     daemon=True).start()
                except Exception:
                    error = ("Bitte überprüfen Sie ihre E-Mail-Adresse und Ihr"
                             " dazu gehöriges Passwort bzw. sorgen Sie dafür, "
                             "dass bei ihrem E-Mail Provider der Zugriff über "
                             "IMAP und POP3 nicht deaktiviert ist.")
                    self.app.open_error_popup(error)
        except Exception:
            error = "Der Provider Ihrer E-Mail-Adresse wird nicht unterstützt"
            self.app.open_error_popup(error)

    @mainthread
    def remove_update_button(self, *args):
        """Remove the update button from the home screen."""
        for w in self.app.root.ids['home_screen'].ids['home'].children:
            if self.app.fb == w:
                (self.app.root.ids['home_screen'].ids['home']
                 .remove_widget(w))

    @mainthread
    def add_update_button(self, *args):
        """Add a update button to the home screen."""
        self.app.fb = Factory.FloatButton()
        (self.app.root.ids['home_screen'].ids['home']
         .add_widget(self.app.fb))

    def start_checking(self):
        """Check the inbox for new reports."""
        try:
            self.remove_update_button()
            for _ in range(15):
                self.check_email()
                time.sleep(20)
            self.add_update_button()
            self.con.close()
            self.con.logout()
            return
        except Exception:
            error = "Ein Fehler ist aufgetreten"
            self.app.open_error_popup(error)
            self.con.close()
            self.con.logout()

    def check_email(self):
        """Iterate over all payloads of the new received emails and downloads attached pdf files."""
        for msg in self.get_emails():
            payload, file_name = \
                self.get_attachments(msg, (lambda x: x.endswith('.pdf')))
            attachment_dir = os.path.join(os.getcwd(),
                                          'reports',
                                          f'fertige-berichte-{self.year}')
            if payload is not None:
                file_path = os.path.join(attachment_dir, file_name)
                if not os.path.exists(file_path):
                    with open(file_path, 'wb') as f:
                        f.write(payload)

    def search(self, c1, c2, val1):
        """Search for the specific emails."""
        typ, data = \
            self.con.search(None, f'({c1.upper()} "{val1}" {c2.upper()})')
        return (typ, data)

    @mainthread
    def report_rejected(self, num):
        """Change status of the specific calendar week."""
        current_c_w = \
            (dt.date(*list(map(int, reversed(self.app.START_DATES[self.year-1]
                                             .split('.')))))
                .isocalendar()[1])
        total_weeks = \
            (dt.date(int(self.app.START_DATES[self.year-1][-4:]), 12, 28)
             .isocalendar()[1])
        max_calws = 53 if current_c_w == 53 or total_weeks == 53 else 52
        with open(os.path.join(os.getcwd(), 'data', 'Bh_data.json'), 'r') as f:
            d = json.load(f)
        for widget in self.app.banner_grid.children:
            # find the selected banner
            if num == widget.id_number:
                # deletes old banner and replace it with the new
                # banner with the right status
                self.app.banner_grid.remove_widget(widget)
                self.app.banner_grid.add_widget(
                    ReportBanner(num,
                                 self.app.get_period(self.app.START_YEAR, num),
                                 (((current_c_w + num - 2) % max_calws) + 1),
                                 os.path.join(self.app.cwd, 'icons',
                                              'notFilledOutSymbol.png'),
                                 widget.total_hours),
                    len(self.app.banner_grid.children)-(num-1))

        (d['record_book']['content'][self.year-1]
         ['calendar_week'][num-1]['header']['status']) = \
            os.path.join(os.getcwd(),
                         'icons', 'notFilledOutSymbol.png')
        with open(os.path.join(os.getcwd(), 'data', 'Bh_data.json'),
                  'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False, indent=2)

    def get_emails(self):
        """Get the specific emails from the trainer."""
        self.con.select('INBOX')
        trainer_email_addr = self.app.TRAINER_EMAIL
        res, data = self.search('FROM', 'UNSEEN', trainer_email_addr)
        if res == 'OK':
            for id in data[0].split():
                typ, data = self.con.fetch(id, '(RFC822)')
                email_msg = \
                    email.message_from_string(data[0][1].decode("utf-8"))
                msg = email.message_from_bytes(data[0][1])
                try:
                    subject = self.decode_mime_header(email_msg['Subject'])
                except Exception:
                    subject = email_msg['Subject']
                self.year = int(subject[-1])
                if 'ABGELEHNT' in subject:
                    email_body = self.get_email_body(msg).decode("utf-8")
                    num = subject.split(' - ')[0][-1]
                    self.report_rejected(int(num))
                    error = email_body
                    self.app.open_error_popup(error)
                    continue
                yield msg

    def get_email_body(self, msg):
        """Get the body of the email."""
        if msg.is_multipart():
            return self.get_email_body(msg.get_payload(0))
        else:
            return msg.get_payload(None, True)

    def get_attachments(self, msg, check):
        """Get the pdf file of the email."""
        try:
            for part in msg.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Content-Disposition') is None:
                    continue
                file_name = part.get_filename()
                if bool(file_name) and check(file_name):
                    return (part.get_payload(decode=True), file_name)
                else:
                    return None, ''
            return None, ''
        except Exception:
            pass

    def decode_mime_header(self, s):
        """Decode the encoded chunks (encoded-words)."""
        return (''.join(word.decode(encoding or 'utf8')
                for word, encoding in email.header.decode_header(s)))
