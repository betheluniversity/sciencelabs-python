from datetime import datetime

class ScienceLabsController(object):
    def __init__(self):
        # TODO: not sure what should go here
        self.date_format = '%d/%m/%Y'

    def format_date(self, date):
        original = datetime.strptime(date, '%Y-%m-%d')
        formatted = original.strftime('%m/%d/%Y')
        return formatted

