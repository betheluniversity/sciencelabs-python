class ReportController:
    def __init__(self):
        super(ReportController, self).__init__

    # TODO FINISH METHOD
    def get_closed_monthly_info(self):
        monthly = []
        for i in range(1, 8):
            monthly.append([
                'Schedule Name',
                'DOW',
                'Schedule Time',
                'Total Attendance',
                '% Total'
            ])
        return monthly

    # TODO FINISH METHOD
    def get_monthly_info(self):
        monthly = []
        for i in range(1, 27):
            monthly.append([
                'Name',
                'Date',
                'DOW',
                'Schedule Time',
                'Total Attendance',
                'report'
            ])
        return monthly

    # TODO FINISH METHOD
    def get_cumulative_info(self):
        return []

    # TODO FINISH METHOD
    def get_term_info(self):
        term = []
        for i in range(1, 8):
            term.append([
                "Schedule Name",
                "DOW",
                "Start Time",
                "Stop Time",
                "Number of Sessions",
                "Attendance",
                "Percentage"
            ])
        return term
