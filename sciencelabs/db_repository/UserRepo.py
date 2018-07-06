from sciencelabs.db_repository import User


class UserFunctions:

    def get_report_student_info(self):
        # # TODO STILL NEED ATTENDANCE AND REPORT
        # student_list = conn.execute(select([user]))
        # students = []
        # for row in student_list:
        #     students.append([
        #         row[4],  # lastName
        #         row[3],  # firstName
        #         row[5],  # Email
        #         'attendance',
        #         'report'
        #     ])
        # return students
        students = []
        for row in User.get_report_student_info(self):
            students.append([
                row[0],
                row[1],
                row[2],
                'attendance',
                'report'
            ])
        return students

    def get_user_info(self):
        users = []
        for row in User.get_user_info(self):
            users.append([
                row[0],
                row[1],
                row[2],
                row[3],
                'edit',
                'check'
            ])
        return users