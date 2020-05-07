import os
import string
import subprocess
import json
from kivy.uix.modalview import ModalView
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.factory import Factory


class CreationPopup(ModalView):
    """
    Popup with Progress Bar

    Attributes
    ----------
    box : CreationProgressBar object (subclass from BoxLayout)
        The layout of the popup
    progress_bar : ProgressBar object
        The progress bar
    size_hint : tuple
        The size of the Popup
    rep : int
        The progress of the progress bar

    Methods
    -------
    update()
        Set a new limit for the progress bar
    progress_bar_start()
        Initiate the progresss bar and open popup to show progress bar
    progression()
        Increment the progress bar value and return False when finished
    popup_open()
        Invocate the progression method every 10 microseconds
    """
    # Set up progress_bar, which is shown while creating a PDF file
    def __init__(self, **kwargs):
        super(CreationPopup, self).__init__(**kwargs)
        self.box = Factory.CreationProgressBar()
        self.progress_bar = ProgressBar(size_hint_x=.7,
                                        pos_hint={'center_x': .5,
                                                  'center_y': .5})
        self.size_hint = (.5, .3)
        self.box.add_widget(self.progress_bar)
        self.add_widget(self.box)
        self.bind(on_open=self.popup_open)
        self.rep = 20

    def update(self):
        """Set a new limit for the progress bar."""
        self.rep += 20
        self.popup_open()

    def progress_bar_start(self, *args):
        """Initiate the progresss bar and open popup to show progress bar."""
        self.progress_bar.value = 1
        self.open()

    def progression(self, *args):
        """Increment the progress bar value and return False when finished."""
        if self.progress_bar.value >= 100:
            self.dismiss()
            # returns False to stop the iteration
            return False
        elif self.progress_bar.value >= self.rep:
            return False
        self.progress_bar.value += 1

    def popup_open(self, *args):
        """Invocate the progression method every 10 microseconds."""
        Clock.schedule_interval(self.progression, .00001)


class CreateReport():
    """Creates Report as a PDF file.

    This class takes the given data from a specific calendar week in the
    json file and the passed arguments to fill at specific places a TEX file.
    And this TEX file will be used to build a PDF file by using pdflatex.

    Attributes
    ----------
    week : int
        the calendar week
    year : int
        The apprenticeship year
    out_filename : string
        The name of the output PDF and TEX file
    first_row_color : string
        The color of the first row
    first_column_color : string
        The color of the first column
    cal_w : int
        The calender week
    number_of_rep : int
        The report number
    bar : CreationPopup object
        Popup with a Progress Bar inside

    Methods
    -------
    create_tex_file()
        Create the report as a TEX file
    create_tex_file(build_path)
        Create the report as a PDF file
    """

    def __init__(self, week,
                 year,
                 out_filename,
                 row_color,
                 column_color,
                 cal_w,
                 number_of_rep):
        self.project_path = os.path.curdir
        self.build_path = os.path.join(self.project_path,
                                       'reports',
                                       'berichte-'+str(year+1))
        self.week = week
        self.year = year
        self.out_filename = os.path.join(self.build_path, out_filename)
        self.row_color = row_color
        self.column_color = column_color
        self.cal_w = cal_w
        self.number_of_rep = number_of_rep
        self.bar = CreationPopup()

    def create(self):
        """Create the report as a TEX file."""

        self.bar = CreationPopup()
        self.bar.progress_bar_start()
        db_path = os.path.join('.', 'data', 'Bh_data.json')
        dept = []
        latex_files = ['packages.txt', 'commands.txt',
                       'metadata.txt', 'content.txt']
        in_filenames = [os.path.join(self.project_path, 'template', txt_file)
                        for txt_file
                        in latex_files]
        in_files_content = []
        packages, commands, metadata, content = '', '', '', ''

        for idx in range(len(in_filenames)):
            with open(in_filenames[idx], 'r') as f:
                in_files_content.append(f.read())
        packages, commands, metadata, content = in_files_content

        LATEX_TEMPLATE = string.Template(
            rf'''
            \documentclass[ngerman, a4paper]{{scrreprt}}
            {packages}
            {commands}
            {metadata}
            \begin{{document}}
            {content}
            \end{{document}}
            ''')
        with open(db_path) as f:
            data = json.load(f)
        date_period = (data['record_book']['content'][self.year]
                       ['calendar_week'][self.week]['header']
                       ['from_to_date'].split(' - '))
        week_data = (data['record_book']['content'][self.year]['calendar_week']
                     [self.week])

        dept = (', '.join(set([week_data[i]['department'] for i in
                ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'] if
                week_data[i]['department'] != ""])))
        dept = dept[:35]
        latex = LATEX_TEMPLATE.safe_substitute(
            yearOfTraining=(data['record_book']['content'][self.year]
                            ['year_of_apprenticeship']),
            department=dept,
            number=(data['record_book']['content'][self.year]['calendar_week']
                    [self.week]['header']['report_num']),
            traineeName=(f"{data['record_book']['info']['first_name']} "
                         f"{data['record_book']['info']['last_name']}"),
            mondayText=week_data['monday']['activities'],
            mondayHours=week_data['monday']['hours'],
            tuesdayText=week_data['tuesday']['activities'],
            tuesdayHours=week_data['tuesday']['hours'],
            wednesdayText=week_data['wednesday']['activities'],
            wednesdayHours=week_data['wednesday']['hours'],
            thursdayText=week_data['thursday']['activities'],
            thursdayHours=week_data['thursday']['hours'],
            fridayText=week_data['friday']['activities'],
            fridayHours=week_data['friday']['hours'],
            sigDateTrainee=date_period[0],
            signatureTrainee=os.path.join('.', 'signature', 'signature.png'),
            fromDate=date_period[0],
            toDate=date_period[1],
            first_row_color=self.row_color,
            first_column_color=self.column_color,
            IHK_Logo=os.path.join('icons', 'symbol.png'),
            cal_w=self.cal_w,
            number_of_rep=self.number_of_rep,
            email=data['record_book']['info']['trainee_email'])
        self.bar.update()
        with open(self.out_filename + '.tex', 'w') as out_file:
            out_file.write(latex)
        self.create_pdf_file()
        self.bar.update()

    def create_pdf_file(self):
        """Create the report as a PDF file."""
        self.bar.update()
        subprocess.run(['pdflatex',
                        '-output-directory',
                        self.build_path,
                        self.out_filename], stdout=open(os.devnull, 'wb'))
        self.bar.update()
