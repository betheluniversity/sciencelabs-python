# Packages
from sqlalchemy import select

# Local
from sciencelabs import conn
from sciencelabs.db_repository import user


class ReportController:
    def __init__(self):
        super(ReportController, self).__init__

    def get_student_info(self):
        # TODO STILL NEED ATTENDANCE AND REPORT
        student_list = conn.execute(select([user]))
        students = []
        for row in student_list:
            students.append([
                row[4],
                row[3],
                row[5],
            ])
        return students
