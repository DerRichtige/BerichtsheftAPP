from kivy.app import App
from kivy.lang import Builder
from reportbanner import ReportBanner
from pdfbanner import PdfBanner
from designbanner import DesignBanner
from create import CreateReport
from kivy.uix.screenmanager import SlideTransition, NoTransition
from kivy.properties import ListProperty
from kivy.clock import Clock  # mainthread
import calendar as cal
import datetime as dt
from os import listdir
import screens
import os.path
import re
import json
import subprocess
from custwidgets import *
import time
import threading
from functools import partial
from kivy.factory import Factory


class BerichtsheftApp(App):
    """
    Is a subclass of the App class, which is the base of the application and
    it's the main entry point into the Kivy run loop.

    ...

    Attributes
    ----------
    cwd : str
        The current working directory
    week_num : int
        to keep track of the selected calendar week
    weekday_activities : string
        to load the entered activities in the json file of a specific weekday
    selected_color : ListProperty object
        store selected colors to show color for the diffrent design options
    selected_hex_color : list
        store colors for the diffenrent design options
    first_row_color : string
        the color of the first row
    first_column_color : string
        the color of the first column
    activities : string
        the activities of the selected weekday to store it in the database
    department : string
        the department of the selected weekday to store it in the database
    hours : dictionary
        all hours of a selected calendar week to calculate the total number
        of hours
    weekday : string
        to update the selected weekday
    START_DATES : list
        all starting dates of a new apprenticeship year
    year : int
        current apprenticeship year
    total_hours : int
        stores the total number of hours of a calendar week
    banner_grid : GridLayout Object
        used to add Reportbanner, which is a GridLayout, inside a GridLayout
        (is a child of the ScrollView Class)
    temp_var : tuple
        used to hold temporary data to change the status of a cal. week back
    stop_it : threading.Event
        manages an internal flag that can be set to true
    START_DAY : int
        starting day of the apprenticeship year
    START_MONTH : int
        starting month of the apprenticeship year
    START_YEAR : int
        starting year of the apprenticeship year
    MY_FIRST_NAME : string
        the first name of the user
    MY_LAST_NAME : string
        the last name of the user
    MY_EMAIL : string
        the email of the user
    TRAINER_EMAIL : string
        the email of the training manager
    TRAINER_NAME : string
        the name of the training manager
    sent_finished_pdf_files1 : list
        list of the calendar week number of the reports,
        which are sent in the first year
    sent_finished_pdf_files2 : list
        list of the calendar week number of the reports,
        which are sent in the second year
    sent_finished_pdf_files3 : list
        list of the calendar week number of the reports,
        which are sent in the third year
    checked_pdf_1 : list
        list of the calendar week number of the reports,
        which are completed in the first year
    checked_pdf_2 : list
        list of the calendar week number of the reports,
        which are completed in the first year
    checked_pdf_3 : list
        list of the calendar week number of the reports,
        which are completed in the first year
    number_of_reports : int
        the max number of reports in the apprenticeship
    db_path : string
        the path to the json datei "Bh_data.json"
    valid_status : bool
        indicates if the json file is valid

    Methods
    -------
    completed_pdf_banners(*args)
        Searches for completed PDF files
    add_completed_pdf_files(start, completed_pdf_folder, pdfbanner_grid)
        Adds completed PDF files to a scroll view
    update_overview_screen( *args)
        Updates the numbers in the overview
    apply_design(design_num, active, *args)
        Updates colors for the choosen design
    week_activities(weekday, *args)
        Tracks passed weekday to update in the databank and
        open Popup to enter data
    create(weekday, create_pdf, *args)
        Calculates total number of hours and create report
    open_error_popup(self, message, *args)
        Opens a popup to show the error message.
    progress_bar_start(*args)
        Initiates the progresss bar with a starting value and
        open popup to show progress bar
    progression(*args)
        Increments the progress bar value and check if it has
        reached the end value.
    popup_open(*args)
        Executes the progression method every 10 microseconds
        until it returns False.
    enter_activities(sick_active, vacation_active, *args)
        Passes the activities and the department into the database.
    get_period(y, w, *args)
        Returns the period from monday to the next friday
        from the given number of weeks after the start date.
    search_completed_pdf(start, completed_pdf_files, checked_pdf_files)
        Checks a folder with finalized reports from the passed year
    check_completed_reports(*args)
        Checks if a new finalized pdf appeared and check if a
        year is completed to change the status
    update_banner_status(id_number, c_w_number, year=0, finalized=False)
        Changes the status symbol of a calender week on the homescreen
    update_banner_total_hours(id_number, c_w_number)
        Sets the total number of hours from the calendar week
    update_calw_banners(first_time=False , clear=False)
        Adds updated new banners for each calender week of a specific
        year to the homescreen scrollview
    is_filled_out()
        Checks if user data input is valid and completely
    start_checking_completed_pdfs(*args)
        Checks every 10 seconds if a new completed report appeared.
    change_screen(screen_name, transition='slide', direction='left')
        Changes current screen to a passed screen
    check_report_number(num, date_period, *args)
        Changes the from...to period in the header of the template(form)
        screen according to the calendar week
    save_infos(popup=True, *args)
        Analyze the entered user data for validity and update user data
    set_up_start_dates(first_time)
        Set up all dates where a new apprenticeship year begins
    change_year(year, *args)
        Change the appenticeship year to the passed year
    on_start()
        Get everything ready to start the app correctly
    on_stop()
        The Kivy event loop is about to stop, set a stop signal
    max_num_of_reports()
        Calculate the max number of reports
    check_emails()
        Open a popup that asks for the email password to check the Inbox
    """

    cwd = os.getcwd()
    week_num = 1
    weekday_activities = ''
    selected_color = ListProperty([[1, 1, 1, 1], [1, 0, 0, 1]])
    selected_hex_color = ['#FFFFFF', '#FF0000']
    first_row_color = 'D4D4D4'
    first_column_color = 'D4D4D4'
    activities = ''
    department = ''
    hours = {'monday': 0, 'tuesday': 0, 'wednesday': 0,
             'thursday': 0, 'friday': 0}
    weekday = ''
    START_DATES = ["01.08.2020", "01.08.2021", "01.08.2022"]
    year = 0
    total_hours = 0
    banner_grid = ''
    temp_var = ''
    stop_it = threading.Event()  # default is False
    number_of_reports = 0
    db_path = os.path.join(cwd, 'data', 'Bh_data.json')
    valid_status = True

    # check if the json file 'Bh_data' already exist
    if not os.path.isfile(db_path):
        START_DAY = 25
        START_MONTH = 12
        START_YEAR = 2014
        end_day = 25
        end_month = 12
        end_year = 2017
        MY_FIRST_NAME = ''
        MY_LAST_NAME = ''
        MY_EMAIL = ''
        checked_pdf_1 = []
        checked_pdf_2 = []
        checked_pdf_3 = []
        sent_finished_pdf_files1 = []
        sent_finished_pdf_files2 = []
        sent_finished_pdf_files3 = []
        TRAINER_EMAIL = ''
        TRAINER_NAME = ''

    else:
        # initiate variables with data in the json file
        with open(db_path, 'r') as f:
            data = json.load(f)
        creation_date = data['record_book']['info']['creation_date'].split('.')
        START_DAY, START_MONTH, START_YEAR = [int(d) for d in creation_date]
        end_date = data['record_book']['info']['end_date'].split('.')
        end_day, end_month, end_year = [int(d) for d in end_date]
        MY_FIRST_NAME = data['record_book']['info']['first_name']
        MY_LAST_NAME = data['record_book']['info']['last_name']
        MY_EMAIL = data['record_book']['info']['trainee_email']
        TRAINER_EMAIL = data['record_book']['info']['trainer_email']
        TRAINER_NAME = data['record_book']['info']['trainer_name']
        checked_pdf_1 = data['record_book']['info']['completed_pdf_1y']
        checked_pdf_2 = data['record_book']['info']['completed_pdf_2y']
        checked_pdf_3 = data['record_book']['info']['completed_pdf_3y']
        sent_finished_pdf_files1 = \
            data['record_book']['info']['sent_finished_pdf_files1']
        sent_finished_pdf_files2 = \
            data['record_book']['info']['sent_finished_pdf_files2']
        sent_finished_pdf_files3 = \
            data['record_book']['info']['sent_finished_pdf_files3']

    with open(os.path.join(cwd, 'data', 'template.json'), 'r') as f:
        data = json.load(f)
    (data['record_book']['content'][year]
     ['calendar_week'][0]['header']['status']) = \
        os.path.join(cwd, 'icons', 'notFilledOutSymbol.png')
    with open(os.path.join(cwd, 'data', 'template.json'), 'w',
              encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    new_Week = data['record_book']['content'][year]['calendar_week'][0]

    def check_emails(self):
        """Open a popup that asks for the email password to check the Inbox."""
        CheckEmailsPopup().open()

    def build(self):
        """
        Initializes the application

        Override the default build method.
        Returns the constructed widget tree and this will be used as the root
        widget and added to the window.
        """

        # is not loaded by name convention
        GUI = Builder.load_file(os.path.join(self.cwd, 'kv', "main.kv"))
        return GUI

    def search_completed_pdf(self, start, completed_pdf_files,
                             checked_pdf_files,
                             sent_finished_pdf):
        """Check a folder with finalized reports from the passed year.

        Parameters
        ----------
        start : int
            Stands for a apprenticeship year
        completed_pdf_files : list
            All files from a folder which contains completed pdf files
        checked_pdf_files : list
            Contains numbers of completed pdf files which are already processed
        sent_finished_pdf : list
            Contains numbers of the pdf files that were sent
        """

        current_c_w = \
            (dt.date(
             *list(map(int, reversed(self.START_DATES[start].split('.')))))
                .isocalendar()[1])
        total_weeks = (dt.date(int(self.START_DATES[start][-4:]), 12, 28)
                       .isocalendar()[1])
        max_calws = 53 if current_c_w == 53 or total_weeks == 53 else 52
        if self.year == start:
            for doc in completed_pdf_files:
                # verify if there is a new completed pdf file
                try:
                    f_num = doc[-6:-4] if doc[-6].isdigit() else doc[-5]
                    if (f_num not in checked_pdf_files and
                            f_num in sent_finished_pdf):
                        # Change status of the respective calendar week
                        # that was accepted use Clock to run OpenGL
                        # related operations in the main thread
                        Clock.schedule_once(partial(self.update_banner_status,
                                            int(f_num),
                                            (((current_c_w + int(f_num)-2) %
                                             max_calws)+1),
                                            start,
                                            True), 0)
                except (IndexError, ValueError):
                    self.open_error_popup(f"OOPS, die Datei '{doc}' gehört "
                                          "nicht in den Ordner "
                                          f"'fertige-berichte-{start+1}'. "
                                          "Bitte dort entfernen.")

    def check_completed_reports(self, *args):
        """Check if a new finalized pdf appeared."""
        while True:
            # Is True only if the internal flag is True
            if self.stop_it.is_set():
                # Stop running this thread (main Python process can exit).
                return

            self.search_completed_pdf(
                0,
                listdir(os.path.join(self.cwd, 'reports',
                                     'fertige-berichte-1')),
                self.checked_pdf_1,
                self.sent_finished_pdf_files1)
            self.search_completed_pdf(
                1,
                listdir(os.path.join(self.cwd, 'reports',
                                     'fertige-berichte-2')),
                self.checked_pdf_2,
                self.sent_finished_pdf_files2)
            self.search_completed_pdf(
                2,
                listdir(os.path.join(self.cwd, 'reports',
                                     'fertige-berichte-3')),
                self.checked_pdf_3,
                self.sent_finished_pdf_files3)
            time.sleep(10)  # blocking thread for 10 sec

    def completed_pdf_banners(self, year, *args):
        """
        Search for completed PDF files

        Search for completed PDF files and add for
        every completion a specific banner, sorted
        to a scroll view. And this for each apprenticeship year.

        Parameters
        ----------
        year : int
            the apprenticeship year
        """

        try:
            completed_pdf_folder = \
                sorted(
                    listdir(os.path.join(self.cwd,
                                         'reports',
                                         f'fertige-berichte-{year}')),
                    key=lambda pdf: int(pdf[-6:-4]) if pdf[-6].isdigit()
                    else int(pdf[-5]))
            pdfbanner_grid = \
                (self.root.ids['finalizedbanner_screen']
                 .ids['pdfbanner_grid'])
            pdfbanner_grid.clear_widgets()
        except (IndexError, ValueError):
            self.open_error_popup("OOPS, eine Datei im Ordner "
                                  "gehört "
                                  "dort nicht hin. "
                                  "Bitte Dort entfernen.")
        except Exception:
            self.open_error_popup("OOPS, ein Fehler ist aufgetreten.")
        self.add_completed_pdf_files(year,
                                     completed_pdf_folder,
                                     pdfbanner_grid)

    def add_completed_pdf_files(self, year,
                                completed_pdf_folder,
                                pdfbanner_grid):
        """
        Add completed PDF files to a scroll view.

        Search every passed folder for completed PDF files of a given year
        and add for every completion a specific banner to the
        pdfbanner_grid.

        Parameters
        ----------
        start : int
            The apprenticeship year
        completed_pdf_folder : list
            All files from a folder which contains completed pdf files
        pdfbanner_grid : GridLayout Object
            Used to add Pdfbanner, which is a GridLayout,
            inside the pdfbanner_grid
            (is a child of the ScrollView Class)
        """
        self.root.ids['finalizedbanner_screen'].ids['title'].text = \
            f"Abgezeichnete Berichte - {year}. Lehrjahr"
        current_c_w = \
            (dt.date(
                *list(map(int, reversed(self.START_DATES[year-1].split('.')))))
                .isocalendar()[1])
        total_weeks = \
            (dt.date(int(self.START_DATES[year-1][-4:]), 12, 28)
                .isocalendar()[1])
        max_calws = 53 if current_c_w == 53 or total_weeks == 53 else 52
        for pdf in completed_pdf_folder:
            f_num = pdf[-6:-4] if pdf[-6].isdigit() else pdf[-5]
            b = (PdfBanner(
                    int(f_num),
                    year,
                    c_w_number=(((current_c_w + int(f_num) - 2) %
                                 max_calws) + 1)))
            pdfbanner_grid.add_widget(b)

    def max_num_of_reports(self):
        """Calculate the max number of reports."""
        number_of_reports = 0
        end_cal_w = \
            (dt.date(self.end_year, self.end_month, self.end_day)
                .isocalendar()[1])
        start_cal_w = \
            (dt.date(*list(map(int, reversed(self.START_DATES[0].split('.')))))
                .isocalendar()[1])
        if end_cal_w == 53 and self.end_month == 1:
            end_year = self.end_year-1
        elif end_cal_w == 1 and self.end_month == 12:
            end_year = self.end_year+1
        else:
            end_year = self.end_year
        dif = end_year - (self.START_YEAR-self.year)
        if dif == 0:
            number_of_reports = end_cal_w - (start_cal_w-1)
        else:
            number_of_reports = \
                (dt.date((self.START_YEAR-self.year), 12, 28)
                    .isocalendar()[1] - (start_cal_w-1))
            number_of_reports += end_cal_w
            if dif > 1:
                for i in range(1, dif):
                    number_of_reports += \
                        (dt.date((self.START_YEAR-self.year)+i, 12, 28)
                            .isocalendar()[1])
        return number_of_reports

    def update_overview_screen(self, *args):
        """Updates the numbers in the overview."""
        self.number_of_reports = self.max_num_of_reports()
        approved_reports = 0
        reports = 0
        for num in range(1, 4):
            reports += \
                (len([f for f in
                      listdir(os.path.join(self.cwd,
                                           'reports',
                                           f'berichte-{num}'))
                      if f.endswith(".pdf")]))
            approved_reports += \
                len(listdir(os.path.join(self.cwd,
                                         'reports',
                                         f'fertige-berichte-{num}')))
        with open(self.db_path, 'r') as f:
            data = json.load(f)
        vacation_days = data['record_book']['info']['vacation_days']
        absent_days = data['record_book']['info']['absent_days']
        self.root.ids['overview_screen'].ids['submitted'].text = \
            f'{reports}/{str(self.number_of_reports)}'
        self.root.ids['overview_screen'].ids['approved'].text = \
            f'{str(approved_reports)}/{str(self.number_of_reports)}'
        self.root.ids['overview_screen'].ids['vacation'].text = \
            str(vacation_days)
        self.root.ids['overview_screen'].ids['absent'].text = str(absent_days)

    def apply_design(self, design_num, active, *args):
        """Update colors for the choosen design.

        Parameters
        ----------
        design_num : int
            The choosen design
        active : bool
            Indicates if a design is choosen
        """
        if design_num == 0 and active == 'down':
            self.first_column_color = 'FFFFFF'
            self.first_row_color = self.selected_hex_color[0][1:7]
        elif design_num == 1 and active == 'down':
            self.first_column_color = self.selected_hex_color[1][1:7]
            self.first_row_color = self.selected_hex_color[1][1:7]
        else:  # normal design
            self.first_column_color = 'FFFFFF'
            self.first_row_color = self.selected_hex_color[0][1:7]

    def week_activities(self, weekday, *args):
        """Track passed weekday and open Popup to enter data.

        Parameters
        ----------
        weekday : string
            The selected weekday
        """
        self.weekday = weekday
        with open(self.db_path, 'r') as f:
            data = json.load(f)
        self.weekday_activities = (data['record_book']['content'][self.year]
                                   ['calendar_week'][self.week_num-1]
                                   [weekday]['activities'])
        with open(self.db_path, 'w', encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        # opens the popup to enter working activities and the department
        ActivitiesPopup().open()

    def create(self, weekday, create_pdf, *args):
        """
        Calculate total number of hours and create report.

        Execute pytotex.py to create a pdf and calculates
        the total number of hours in the selected week,
        if the second passed argument is True.
        If not it just stores the number of hours of the
        passed weekday in the database.

        Parameters
        ----------
        weekday : string
            The selected weekday
        create_pdf : bool
            Start creating the pdf file and adds up the hours worked
            if this value is true, else not.

        Raises
        ------
        exception subprocess.CalledProcessError
            If in the current directory is no file "create_report.py"
        """
        # Store first passed argument, which is a string
        self.weekday = weekday
        # Store number of hours of a day in the database
        with open(self.db_path, 'r') as f:
            data = json.load(f)

        (data['record_book']['content'][self.year]['calendar_week']
         [self.week_num-1][self.weekday]['hours']) = self.hours[self.weekday]
        with open(self.db_path, 'w', encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # Check if all hours a set
        if create_pdf is True:
            # Check if signature
            if os.path.isfile(os.path.join(self.cwd,
                                           'signature',
                                           'signature.png')) is True:
                sick_week = (self.root.ids['template_screen']
                             .ids['sick_week'].state)
                vacation_week = (self.root.ids['template_screen']
                                 .ids['vacation_week'].state)
                if sick_week == 'down':
                    week_days = ['monday', 'tuesday', 'wednesday',
                                 'thursday', 'friday']
                    for weekday in week_days:
                        (data['record_book']['content'][self.year]
                            ['calendar_week'][self.week_num-1][weekday]
                            ['activities']) = "Abwesend"
                        (data['record_book']['content'][self.year]
                            ['calendar_week'][self.week_num-1][weekday]
                            ['department']) = ""
                        (self.root.ids['template_screen']
                            .ids[f'{weekday[:3]}_text'].text) = "ABWESEND"
                        data['record_book']['info']['absent_days'] = \
                            data['record_book']['info']['absent_days'] + 1
                        with open(self.db_path, 'w', encoding="utf-8") as f:
                            json.dump(data, f, ensure_ascii=False, indent=2)
                elif vacation_week == 'down':
                    for weekday in ['monday', 'tuesday',
                                    'wednesday', 'thursday', 'friday']:
                        (data['record_book']['content'][self.year]
                            ['calendar_week'][self.week_num-1][weekday]
                            ['activities']) = "Urlaub"
                        (data['record_book']['content'][self.year]
                            ['calendar_week'][self.week_num-1][weekday]
                            ['department']) = ""
                        (self.root.ids['template_screen']
                            .ids[f'{weekday[:3]}_text'].text) = "URLAUB"
                        data['record_book']['info']['vacation_days'] = \
                            data['record_book']['info']['vacation_days'] + 1
                        with open(self.db_path, 'w', encoding="utf-8") as f:
                            json.dump(data, f, ensure_ascii=False, indent=2)
                try:
                    # create pdf
                    self.number_of_reports = self.max_num_of_reports()
                    start_c_w = dt.date(self.START_YEAR,
                                        self.START_MONTH,
                                        self.START_DAY).isocalendar()[1]
                    cal_w = \
                        ((start_c_w + self.week_num - 2) % self.max_calws) + 1
                    report = CreateReport(
                        self.week_num-1,
                        self.year,
                        'Nachweis_%d' % (self.week_num),
                        self.first_row_color,
                        self.first_column_color,
                        cal_w,
                        self.number_of_reports)
                    report.create()

                    # calculate total number of hours
                    self.total_hours = \
                        sum(map(
                            int, [i for i in self.hours.values() if i != '']))
                    # show total number of hours on the home screen
                    start_c_w = dt.date(self.START_YEAR,
                                        self.START_MONTH,
                                        self.START_DAY).isocalendar()[1]
                    self.update_banner_total_hours(
                        self.week_num,
                        (((start_c_w + self.week_num - 2) %
                            self.max_calws) + 1))
                except subprocess.CalledProcessError:
                    self.open_error_popup('Die gewünschte PDF konnte nicht '
                                          'erstellt werden, da die Datei '
                                          '"./create_report.py" nicht '
                                          'gefunden wurde.')
            else:
                self.open_error_popup('Keine Unterschrift wurde gefunden. '
                                      '\nBitte erstellen Sie eine in der App.')

    def open_error_popup(self, message, *args):
        """Open a popup to show the error message.

        Parameters
        ----------
        message : str
            The error message
        """
        ErrorPopup(message).open()

    def enter_activities(self, sick_active, vacation_active, *args):
        """Pass the activities and the department into the database.

        Parameters
        ----------
        sick_active : string
            Indicates if day of absence is selected
        vacation_active : string
            Indicates day of vacation
        """
        with open(self.db_path, 'r') as f:
            data = json.load(f)
        pattern = re.compile(r'[\n\r]+')
        self.activities = pattern.sub(r'\\newline ', self.activities)
        t = "ERLEDIGT"
        if sick_active == 'down':
            (data['record_book']['content'][self.year]['calendar_week']
                [self.week_num-1][self.weekday]['activities']) = "Abwesend"
            (data['record_book']['content'][self.year]['calendar_week']
                [self.week_num-1][self.weekday]['department']) = ""
            t = "ABWESEND"
            data['record_book']['info']['absent_days'] = \
                data['record_book']['info']['absent_days'] + 1
        elif vacation_active == 'down':
            (data['record_book']['content'][self.year]['calendar_week']
                [self.week_num-1][self.weekday]['activities']) = "Urlaub"
            (data['record_book']['content'][self.year]['calendar_week']
                [self.week_num-1][self.weekday]['department']) = ""
            t = "URLAUB"
            data['record_book']['info']['vacation_days'] = \
                data['record_book']['info']['vacation_days'] + 1
        else:
            (data['record_book']['content'][self.year]['calendar_week']
                [self.week_num-1][self.weekday]
                ['activities']) = self.activities
            (data['record_book']['content'][self.year]['calendar_week']
                [self.week_num-1][self.weekday]
                ['department']) = self.department
        with open(self.db_path, 'w', encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        (self.root.ids['template_screen']
            .ids[f'{self.weekday[:3]}_text'].text) = t

    def get_period(self, y, w, *args):
        """Return the working period.

        The period from monday to the next friday from
        the given number of weeks after the start date.

        Parameters
        ----------
        y : string
            Start year of the apprenticeship year
        w : string
            The calender week of the peroid to be found

        Returns
        -------
        string
            The period from monday to the next friday of the given
            calender week
        """
        day = cal.weekday(y, self.START_MONTH, self.START_DAY)
        start_date = dt.date(y, self.START_MONTH, self.START_DAY)
        # check if day is a monday
        if day != 0:
            # correct the start date to a monday
            start_date -= dt.timedelta(days=day)

        # +1 after modulo to start with 1 and -2 to begin with the start date,
        # also it loops 370 times to correct the shift sometimes
        date = [start_date + dt.timedelta(days=i)
                for i in range(370)
                if (start_date + dt.timedelta(days=i)).isocalendar()[1] ==
                ((start_date.isocalendar()[1]+(w-2)) % self.max_calws)+1]

        return (f"{date[0].strftime('%d.%m.%Y')} - "
                f"{date[4].strftime('%d.%m.%Y')}") if len(date) > 4 \
            else (f"{date[0].strftime('%d.%m.%Y')} - "
                  f"{date[-1].strftime('%d.%m.%Y')}")

    def update_banner_status(self, id_number, c_w_number,
                             year=0, finalized=False, *args):
        """Change the status symbol of a calender week on the homescreen.

        Parameters
        ----------
        id_number : int
            to identify the right calendar week
        c_w_number : int
            the calendar week number
        year : int
            stands for the apprenticeship year
        finalized : bool
            indicates if the cal. week is finalized
        """
        with open(self.db_path, 'r') as infile:
            data = json.load(infile)
        for widget in self.banner_grid.children:
            # Find the selected banner
            if id_number == widget.id_number:
                # Changes nothing if status is already "accepcted"
                if widget.status == os.path.join(self.cwd, 'icons',
                                                 'acceptedSymbol.png'):
                    break

                # Changes status of a finalized calendar week
                if (widget.status ==
                        os.path.join(self.cwd, 'icons',
                                     'inProgressSymbol.png') and
                        finalized is True and self.year == year):
                    # deletes old status symbol and changes it to
                    # the new status symbol
                    self.banner_grid.remove_widget(widget)
                    self.banner_grid.add_widget(
                        ReportBanner(id_number,
                                     self.get_period(
                                         int(self.START_DATES[year][-4:]),
                                         id_number),
                                     c_w_number,
                                     os.path.join(self.cwd, 'icons',
                                                  'acceptedSymbol.png'),
                                     widget.total_hours),
                        len(self.banner_grid.children) - (id_number-1))
                    if year == 0:
                        self.checked_pdf_1.append(str(id_number))
                        data['record_book']['info']['completed_pdf_1y'] = \
                            self.checked_pdf_1
                        self.sent_finished_pdf_files1.remove(str(id_number))
                        (data['record_book']['info']
                            ['sent_finished_pdf_files1']) = \
                            self.sent_finished_pdf_files1
                    elif year == 1:
                        self.checked_pdf_2.append(str(id_number))
                        data['record_book']['info']['completed_pdf_2y'] = \
                            self.checked_pdf_2
                        self.sent_finished_pdf_files2.remove(str(id_number))
                        (data['record_book']['info']
                            ['sent_finished_pdf_files2']) = \
                            self.sent_finished_PDF_files2
                    elif year == 2:
                        self.checked_pdf_3.append(str(id_number))
                        data['record_book']['info']['completed_pdf_3y'] = \
                            self.checked_pdf_3
                        self.sent_finished_pdf_files3.remove(str(id_number))
                        (data['record_book']['info']
                            ['sent_finished_pdf_files3']) = \
                            self.sent_finished_pdf_files3

                    (data['record_book']['content'][year]['calendar_week']
                        [id_number-1]['header']['status']) = \
                        os.path.join(self.cwd, 'icons', 'acceptedSymbol.png')
                    with open(self.db_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    break
                # Changes status to "in progress"
                if (widget.status ==
                    os.path.join(self.cwd, 'icons',
                                 'notFilledOutSymbol.png') and
                        finalized is False):

                    # Deletes the old status symbol and changes it to the
                    # new status symbol
                    self.banner_grid.remove_widget(widget)
                    self.banner_grid.add_widget(
                        ReportBanner(id_number,
                                     self.get_period(self.START_YEAR,
                                                     id_number),
                                     c_w_number,
                                     os.path.join(self.cwd, 'icons',
                                                  'inProgressSymbol.png'),
                                     widget.total_hours),
                        len(self.banner_grid.children)-(id_number-1))
                    (data['record_book']['content'][self.year]['calendar_week']
                        [id_number-1]['header']['status']) = \
                        os.path.join(self.cwd, 'icons', 'inProgressSymbol.png')

                    # temp_var is used to update the status of a
                    # calendar week to "not filled out" back
                    self.temp_var = (id_number, c_w_number)
                    with open(self.db_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    if (str(id_number) not in
                            self.sent_finished_pdf_files1 and
                            self.year == 0):
                        self.sent_finished_pdf_files1.append(str(id_number))
                        (data['record_book']['info']
                            ['sent_finished_pdf_files1']) = \
                            self.sent_finished_pdf_files1
                    elif (str(id_number) not in
                            self.sent_finished_pdf_files2 and
                            self.year == 1):
                        self.sent_finished_pdf_files2.append(str(id_number))
                        (data['record_book']['info']
                            ['sent_finished_pdf_files2']) = \
                            self.sent_finished_pdf_files2
                    elif (str(id_number) not in
                            self.sent_finished_pdf_files3 and
                            self.year == 2):
                        self.sent_finished_pdf_files3.append(str(id_number))
                        (data['record_book']['info']
                            ['sent_finished_pdf_files3']) = \
                            self.sent_finished_pdf_files3
                    with open(self.db_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    ReportBanner(id_number,
                                 self.get_period(self.START_YEAR, id_number),
                                 c_w_number,
                                 widget.status,
                                 widget.total_hours).permission()
                    break
                # Changes status back to "not filled out"
                if (widget.status ==
                    os.path.join(self.cwd, 'icons', 'inProgressSymbol.png') and
                        finalized is False):
                    # switches back to the "not filled out" status symbol
                    self.banner_grid.remove_widget(widget)
                    self.banner_grid.add_widget(
                        ReportBanner(
                            id_number,
                            self.get_period(self.START_YEAR,
                                            id_number),
                            c_w_number,
                            os.path.join(self.cwd, 'icons',
                                         'notFilledOutSymbol.png'),
                            widget.total_hours),
                        len(self.banner_grid.children)-(id_number-1))
                    (data['record_book']['content'][self.year]
                        ['calendar_week'][id_number-1]['header']['status']) = \
                        os.path.join(self.cwd, 'icons',
                                     'notFilledOutSymbol.png')
                    if (str(id_number) in self.sent_finished_pdf_files1 and
                            self.year == 0):
                        self.sent_finished_pdf_files1.remove(str(id_number))
                        (data['record_book']['info']
                            ['sent_finished_pdf_files1']) = \
                            self.sent_finished_pdf_files1
                    elif (str(id_number) in self.sent_finished_pdf_files2 and
                            self.year == 1):
                        self.sent_finished_pdf_files2.remove(str(id_number))
                        (data['record_book']['info']
                            ['sent_finished_pdf_files2']) = \
                            self.sent_finished_pdf_files2
                    elif (str(id_number) in self.sent_finished_pdf_files3 and
                            self.year == 2):
                        self.sent_finished_pdf_files3.remove(str(id_number))
                        (data['record_book']['info']
                            ['sent_finished_pdf_files3']) = \
                            self.sent_finished_pdf_files3
                    with open(self.db_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    break

    def update_banner_total_hours(self, id_number, c_w_number):
        """Set the total number of hours from the calendar week.

        Parameters
        ----------
        id_number : int
            To identify the right calendar week
        c_w_number : int
            The calendar week number
        """

        for widget in self.banner_grid.children:
            # find the selected banner
            if id_number == widget.id_number:
                # deletes old banner and replace it with the new
                # banner with the right total number of hours from the week
                self.banner_grid.remove_widget(widget)
                self.banner_grid.add_widget(
                    ReportBanner(id_number,
                                 self.get_period(self.START_YEAR, id_number),
                                 c_w_number,
                                 widget.status,
                                 self.total_hours),
                    len(self.banner_grid.children)-(id_number-1))
                with open(self.db_path, 'r') as f:
                    data = json.load(f)
                (data['record_book']['content'][self.year]['calendar_week']
                    [id_number-1]['header']['total_hours']) = self.total_hours
                with open(self.db_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                break

    def update_calw_banners(self, first_time=False, clear=False):
        """Add updated new banners for each cal. w. of a specific year.

        Parameters
        ----------
        first_time : bool, optional
            indicates if it's the first time starting the app (default is False)
        clear : bool, optional
            indicates whether data needs to be updated (default is False)
        """

        # total number of calendar weeks of the current year
        self.max_calws_current = \
            dt.date(self.START_YEAR, 12, 28).isocalendar()[1]
        # Clear all widgets on the homescreen scrollview if its not
        # the first time of starting the app
        if first_time is False:
            self.banner_grid.clear_widgets()
        # Make sure that a year in the homescreen scrollview has
        # all calendar weeks of the apprenticeship year
        start_c_w = dt.date(self.START_YEAR,
                            self.START_MONTH,
                            self.START_DAY).isocalendar()[1]
        self.max_calws = (53 if start_c_w == 53 or
                          self.max_calws_current == 53 else 52)
        with open(self.db_path, 'r') as f:
            data = json.load(f)
        # Check if there is a difference between the number of calendar
        # weeks of the current year and the new year
        diff = (True if len(data['record_book']['content']
                [self.year]['calendar_week']) != self.max_calws else False)
        e = dt.date(self.end_year,
                    self.end_month,
                    self.end_day).isocalendar()[1]
        special_case = False

        if (e == dt.date(self.end_year, 12, 28).isocalendar()[1] and
                self.end_month == 1):
            special_case = True
        s = (dt.date(
             *list(map(int, reversed(self.START_DATES[self.year].split('.')))))
             .isocalendar()[1])

        if e == 53 and self.end_month == 1:
            end_year = self.end_year-1
        elif e == 1 and self.end_month == 12:
            end_year = self.end_year+1
        else:
            end_year = self.end_year

        if clear is False:
            for i in range(1, self.max_calws+1):
                # Build database for a specific year
                with open(self.db_path, 'r') as f:
                    data = json.load(f)
                self.new_Week['header']['from_to_date'] = \
                    self.get_period(self.START_YEAR, i)
                self.new_Week['header']["report_num"] = i
                (data['record_book']['content']
                    [self.year]['calendar_week']).append(self.new_Week.copy())
                status_symbol = os.path.join(self.cwd, 'icons',
                                             'notFilledOutSymbol.png')
                total_hours = '??'
                with open(self.db_path, 'w', encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
        week_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
        for i in range(1, self.max_calws+1):
            # Update database of a year
            if clear is True:
                with open(self.db_path, 'r') as f:
                    data = json.load(f)
                self.new_Week['header']['from_to_date'] = \
                    self.get_period(self.START_YEAR, i)
                self.new_Week['header']["report_num"] = i
                self.new_Week['header']["status"] = \
                    (data['record_book']['content'][self.year]
                        ['calendar_week'][0]['header']['status'])
                self.new_Week['header']['total_hours'] = \
                    (data['record_book']['content'][self.year]
                        ['calendar_week'][0]['header']['total_hours'])

                for day in week_days:
                    self.new_Week[day]['department'] = \
                        (data['record_book']['content'][self.year]
                            ['calendar_week'][0][day]['department'])
                    self.new_Week[day]['activities'] = \
                        (data['record_book']['content'][self.year]
                            ['calendar_week'][0][day]['activities'])
                    self.new_Week[day]['hours'] = \
                        (data['record_book']['content'][self.year]
                            ['calendar_week'][0][day]['hours'])
                (data['record_book']['content'][self.year]
                    ['calendar_week']).append(self.new_Week.copy())

                # Check if the old amount of data is less than the new amount
                # of data, if so give new data standard data
                if diff and self.max_calws == 53 and i == self.max_calws:
                    status_symbol = os.path.join(self.cwd, 'icons',
                                                 'notFilledOutSymbol.png')
                    total_hours = '??'
                # Check if the old amount of data is more than the new amount
                # of data, if so delete last element of the old data
                elif diff and self.max_calws == 52 and i == self.max_calws:
                    status_symbol = (data['record_book']['content'][self.year]
                                     ['calendar_week'][0]['header']['status'])
                    total_hours = (data['record_book']['content'][self.year]
                                   ['calendar_week'][0]['header']
                                   ['total_hours'])
                    del (data['record_book']['content'][self.year]
                         ['calendar_week'][0])  # no need to store any more
                else:
                    status_symbol = (data['record_book']['content'][self.year]
                                     ['calendar_week'][0]['header']['status'])
                    total_hours = (data['record_book']['content'][self.year]
                                   ['calendar_week'][0]['header']
                                   ['total_hours'])

                if diff and self.max_calws == 53 and i == self.max_calws:
                    pass  # the old data has already been completely deleted
                else:
                    del (data['record_book']['content'][self.year]
                         ['calendar_week'][0])  # delete old data

                with open(self.db_path, 'w', encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

                if special_case and end_year == self.START_YEAR:
                    continue

                if e < s:
                    if end_year-1 == self.START_YEAR:
                        m = ((s + i-2) % self.max_calws) + 1
                        if e < m and m < s:
                            continue

                    if end_year <= self.START_YEAR:
                        continue
                else:
                    if end_year == self.START_YEAR:
                        if ((s + i - 2) % self.max_calws)+1 > e:
                            continue
                        if s > ((s + i - 2) % self.max_calws)+1:
                            continue
                    if end_year < self.START_YEAR:
                        continue
            c = ReportBanner(
                i,
                self.get_period(self.START_YEAR, i),
                c_w_number=(((dt.date(self.START_YEAR,
                                      self.START_MONTH,
                                      self.START_DAY).isocalendar()[1]+i-2) %
                             self.max_calws)+1),
                status=status_symbol,
                total_hours=total_hours)
            # add new banner to the homescreen scroll view
            self.banner_grid.add_widget(c)

    def is_filled_out(self):
        """Check if user data input is valid and completely.

        Returns
        -------
        bool
            is True if the entered data is valid else False
        """

        new_input = all(i != '' for i in [self.START_DAY,
                                          self.START_MONTH,
                                          self.START_YEAR,
                                          self.end_day,
                                          self.end_month,
                                          self.end_year,
                                          self.MY_FIRST_NAME,
                                          self.MY_LAST_NAME,
                                          self.MY_EMAIL,
                                          self.TRAINER_EMAIL,
                                          self.TRAINER_NAME])
        if new_input is True:
            valid_s_year = (len(str(self.START_YEAR)) == 4)
            valid_e_year = (len(str(self.end_year)) == 4)
            valid_s_month = (self.START_MONTH <= 12)
            valid_e_month = (self.end_month <= 12)
            email = all([re.match(
                r'^[_a-z0-9-]+(\.[_a-z0-9-)]+)*@[a-z0-9-]+(\.[a-z]{2,4})$', e)
                        for e in (self.MY_EMAIL, self.TRAINER_EMAIL)])
            if all([valid_s_year, valid_e_year,
                    valid_s_month, valid_e_month, email]):
                valid_s_day = (self.START_DAY <=
                               cal.monthrange(self.START_YEAR,
                                              self.START_MONTH)[1])
                valid_e_day = self.end_day <= cal.monthrange(self.end_year,
                                                             self.end_month)[1]
                if valid_s_day and valid_e_day:
                    return True
        return False

    def start_checking_completed_pdfs(self, *args):
        """Check every 10 seconds if a new completed report appeared."""
        threading.Thread(target=self.check_completed_reports,
                         daemon=True).start()

    def on_stop(self):
        """The Kivy event loop is about to stop, set a stop signal."""
        # Set the internal flag to True, which will stop
        # hanging threads when the app is about to close
        self.stop_it.set()
        with open(self.db_path, 'r') as f:
            data = json.load(f)
        if data['record_book']['info']['valid'] is False:
            os.remove(os.path.join(self.cwd, 'data', 'Bh_data.json'))
        if self.valid_status is False:
            self.update_banner_status(*self.temp_var)

    def on_start(self):
        """
        Get everything ready to start the app correctly

        Check if it's the first time opening the app, if so
        open popup to get User data.
        Get progress bar ready to start, which is shown by creating a pdf file
        set up the design screen.
        Create or update the home screen and the database.
        """

        for n in range(1, 4):
            os.makedirs(os.path.join(self.cwd,
                        'reports', f'fertige-berichte-{n}'), exist_ok=True)
            os.makedirs(os.path.join(self.cwd,
                        'reports', f'berichte-{n}'), exist_ok=True)

        # Verify if a database already exist, if not open popup to get
        # data to start
        if not os.path.isfile(self.db_path):
            StartInfoPopup().open()

        self.fb = Factory.FloatButton()
        (self.root.ids['home_screen'].ids['home']
         .add_widget(self.fb))

        # Set up all design options
        design_grid = self.root.ids['design_screen'].ids['design_banner']
        for i in range(2):
            d = DesignBanner(i)
            design_grid.add_widget(d)

        # Save calendar week banner as a main class variable
        self.banner_grid = self.root.ids['home_screen'].ids['banner_grid']

        # Clear all data to start new if no Database exist
        try:
            # Check if there is already a Database, if so just update data
            if os.path.isfile(self.db_path):
                with open(self.db_path, 'r') as f:
                    data = json.load(f)
                self.START_DAY, self.START_MONTH, self.START_YEAR = \
                    [int(d) for d in
                     data['record_book']['info']['creation_date'].split('.')]
                self.set_up_start_dates(False)
                # Verify if its the first time starting the app, if so start
                # checking complettion
                self.start_checking_completed_pdfs()
            else:
                # Create database
                with open(os.path.join(self.cwd,
                                       'data',
                                       'template.json'), 'r') as f:
                    data = json.load(f)
                del data['record_book']['content'][0]['calendar_week'][:]
                with open(self.db_path, 'w', encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                new = True
                clr = False
                self.update_calw_banners(first_time=new, clear=clr)
        except IOError:
            self.open_error_popup("Es konnte keine Datenbank erstellt werden. "
                                  "Dafür wird die Datei 'template.json' "
                                  "benötigt.")

    def change_screen(self, screen_name, transition='slide',
                      direction='left', *args, **kwargs):
        """Changes current screen to a passed screen.

        Parameters
        ----------
        screen_name : str
            The name of a screen
        transition : str, optional
            The type of transition (default is 'slide')
        direction : str, optional
            The direction of the transition (default is 'left')
        """

        txt_dct = {'home_screen': 'NACHWEISE',
                   'settings_screen': 'EINSTELLUNGEN',
                   'template_screen': 'NACHWEIS',
                   'design_screen': 'DESIGN',
                   'overview_screen': 'BERICHTSHEFT'}

        # get screen manager from the .kv file
        screen_manager = self.root.ids['screen_manager']
        transitions = {'slide': (lambda d: SlideTransition(direction=d)),
                       'none': (lambda d: NoTransition(direction=d))}
        screen_manager.transition = transitions[transition](direction)
        screen_manager.current = screen_name
        menu_text = self.root.ids['menu_txt']
        # change the menu text according to the current screen
        if screen_name in txt_dct:
            menu_text.text = txt_dct[screen_name]

    def check_report_number(self, num, date_period, *args):
        """Change the period in the header according to the calendar week.

        Parameters
        ----------
        num : int
            The number of the calendar week
        date_period : str
            The period from monday to the next friday of a specific
            calendar week
        """
        self.week_num = num
        custLabel = self.root.ids['template_screen'].ids['custl']
        custLabel.text = date_period

    def save_infos(self, popup=True, *args):
        """Analyze the entered user data for validity and update user data.

        Parameters
        ----------
        popup : bool
            Indicates if the entered data was entered via
            the beginning popup or not
        """
        # Check if the data is valid and completely
        if self.is_filled_out() is False:
            self.open_error_popup(
                "Die eingegebenen Daten konnten nicht übernommen werden.")
        else:
            if popup is True:
                # Change validity of database
                with open(self.db_path, 'r') as f:
                    data = json.load(f)
                    data['record_book']['info']['valid'] = True
                with open(self.db_path, 'w', encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            with open(self.db_path, 'r') as f:
                data = json.load(f)
            data['record_book']['info']['first_name'] = self.MY_FIRST_NAME
            data['record_book']['info']['last_name'] = self.MY_LAST_NAME
            data['record_book']['info']['trainee_email'] = self.MY_EMAIL
            data['record_book']['info']['trainer_name'] = self.TRAINER_NAME
            data['record_book']['info']['trainer_email'] = self.TRAINER_EMAIL
            data['record_book']['info']['end_date'] = \
                (f'{str(self.end_day)}.{str(self.end_month)}'
                 f'.{str(self.end_year)}')
            data['record_book']['info']['creation_date'] = \
                (f'{str(self.START_DAY)}.{str(self.START_MONTH)}'
                 f'.{str(self.START_YEAR)}')
            with open(self.db_path, 'w', encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.set_up_start_dates(popup)

    def set_up_start_dates(self, first_time):
        """Set up all dates where a new apprenticeship year begins.

        Parameters
        ----------
        first_time : bool
            Indicates whether the data was entered from the
            beginning popup or not
        """
        start_date = f'{self.START_DAY}.{self.START_MONTH}.{self.START_YEAR}'
        start_date_calendar_week_numb = \
            (dt.date(self.START_YEAR, self.START_MONTH, self.START_DAY)
             .isocalendar()[1])

        if (dt.date(self.START_YEAR,
                    self.START_MONTH,
                    self.START_DAY).isocalendar()[1] ==
                dt.date(self.START_YEAR - 1, 12, 28).isocalendar()[1] and
                self.START_MONTH == 1):
            next_start_date = \
                (dt.datetime.strptime(
                    f'{self.START_YEAR}.{start_date_calendar_week_numb}.1',
                    '%G.%V.%u'))
            next_next_start_date = \
                (dt.datetime.strptime(
                    f'{self.START_YEAR+1}.{start_date_calendar_week_numb}.1',
                    '%G.%V.%u'))

            if (next_start_date.strftime('%d.%m.%Y')[-4:] ==
                    next_next_start_date.strftime('%d.%m.%Y')[-4:]):
                next_next_start_date = \
                    (dt.datetime.strptime(
                        f'{self.START_YEAR+1}.'
                        f'{start_date_calendar_week_numb}.3',
                        '%G.%V.%u'))
        else:
            next_start_date = \
                (dt.datetime.strptime((f'{self.START_YEAR+1}.'
                                       f'{start_date_calendar_week_numb}.1'),
                                      '%G.%V.%u'))

            if start_date[-4:] == next_start_date.strftime('%d.%m.%Y')[-4:]:
                next_start_date = \
                    (dt.datetime.strptime(
                        f'{self.START_YEAR + 1}.'
                        f'{start_date_calendar_week_numb}.3',
                        '%G.%V.%u'))
            nxt = (list(map(int, reversed(next_start_date.strftime('%d.%m.%Y')
                   .split('.')))))
            s_d, s_m, s_y = [int(i) for i in
                             next_start_date.strftime('%d.%m.%Y')
                             .split('.')]

            if (dt.date(*nxt).isocalendar()[1] ==
                    dt.date(s_y, 12, 28).isocalendar()[1] and s_m == 1):
                next_next_start_date = \
                    (dt.datetime.strptime(
                        f'{s_y}.{start_date_calendar_week_numb}.1',
                        '%G.%V.%u'))
            else:
                next_next_start_date = \
                    (dt.datetime.strptime(
                        (f'{self.START_YEAR + 2}.'
                         f'{start_date_calendar_week_numb}.1'),
                        '%G.%V.%u'))
                if (next_start_date.strftime('%d.%m.%Y')[-4:] ==
                        next_next_start_date.strftime('%d.%m.%Y')[-4:]):
                    next_next_start_date = \
                        (dt.datetime.strptime(
                            (f'{self.START_YEAR+2}.'
                             f'{start_date_calendar_week_numb}.3'),
                            '%G.%V.%u'))

        del self.START_DATES[:]
        self.START_DATES.append(start_date)
        self.START_DATES.append(next_start_date.strftime('%d.%m.%Y'))
        self.START_DATES.append(next_next_start_date.strftime('%d.%m.%Y'))

        # Start checking if a new completed report appeared and
        # updates calendar week banners in the homescreeen and data
        # in the json file (database).
        if first_time is True:
            self.update_calw_banners(first_time=False, clear=True)
            self.start_checking_completed_pdfs()
        # Update the calendar week banners in the homescreen and data in the
        # json file (database) of the current year
        else:
            self.change_year('Ausbildungsjahr: %d' % (int(self.year)+1))

    def change_year(self, year, *args):
        """Change the appenticeship year to the passed year.

        Parameters
        ----------
        year : int
            The apprenticeship year
        """
        with open(self.db_path, 'r') as f:
            data = json.load(f)
        if year == 'Ausbildungsjahr: 1':
            # Set up start_month start_day and start_year
            self.year = 0
            self.START_DAY, self.START_MONTH, self.START_YEAR = \
                list(map(int, (self.START_DATES[0].split('.'))))
            # Update banners and update data in the json file
            self.update_calw_banners(first_time=False, clear=True)

        elif year == 'Ausbildungsjahr: 2':
            self.year = 1
            self.START_DAY, self.START_MONTH, self.START_YEAR = \
                list(map(int, (self.START_DATES[1].split('.'))))
            clr = False
            if data['record_book']['content'][self.year]['calendar_week']:
                clr = True
            self.update_calw_banners(first_time=False, clear=clr)

        elif year == 'Ausbildungsjahr: 3':
            self.year = 2
            self.START_DAY, self.START_MONTH, self.START_YEAR = \
                list(map(int, (self.START_DATES[2].split('.'))))
            clr = False
            if data['record_book']['content'][self.year]['calendar_week']:
                clr = True
            self.update_calw_banners(first_time=False, clear=clr)


BerichtsheftApp().run()  # starts the application life cycle
