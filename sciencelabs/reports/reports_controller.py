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

