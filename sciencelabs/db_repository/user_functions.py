from datetime import datetime
from sqlalchemy import func, distinct, orm

from sciencelabs.db_repository import session
from sciencelabs.db_repository.db_tables import User_Table, StudentSession_Table, Session_Table, Semester_Table, \
    Role_Table, user_role_Table, Schedule_Table, user_course_Table, Course_Table, CourseCode_Table, \
    SessionCourseCodes_Table, CourseViewer_Table, SessionCourses_Table
from sciencelabs.oracle_procs.db_functions import student_course_list, get_info_for_course, get_course_is_valid


class User:

    def get_session_students(self, session_id):
        return session.query(User_Table, StudentSession_Table) \
            .filter(StudentSession_Table.sessionId == session_id)\
            .filter(StudentSession_Table.studentId == User_Table.id)\
            .all()

    def get_student_info(self, semester_id):
        return session.query(User_Table, func.count(User_Table.id)) \
            .filter(User_Table.id == StudentSession_Table.studentId) \
            .filter(StudentSession_Table.sessionId == Session_Table.id) \
            .filter(Session_Table.semester_id == Semester_Table.id) \
            .filter(Semester_Table.id == semester_id) \
            .group_by(User_Table.id)\
            .order_by(User_Table.lastName.asc()) \
            .all()

    def get_user_info(self):
        return session.query(User_Table, Role_Table)\
            .filter(User_Table.id == user_role_Table.user_id) \
            .filter(User_Table.id == user_role_Table.user_id) \
            .filter(user_role_Table.role_id == Role_Table.id) \
            .filter(User_Table.deletedAt == None) \
            .all()

    def get_unique_session_attendance(self, semester_id):
        return session.query(User_Table, func.count(distinct(User_Table.id))) \
            .filter(StudentSession_Table.sessionId == Session_Table.id) \
            .filter(Session_Table.semester_id == Semester_Table.id) \
            .filter(Semester_Table.id == semester_id) \
            .filter(Schedule_Table.id == Session_Table.schedule_id) \
            .filter(StudentSession_Table.studentId == User_Table.id) \
            .group_by(User_Table.id) \
            .all()

    def get_studentsession(self, student_id, semester_id):
        return session.query(StudentSession_Table, Session_Table)\
            .filter(StudentSession_Table.studentId == student_id)\
            .filter(StudentSession_Table.sessionId == Session_Table.id)\
            .filter(Session_Table.semester_id == Semester_Table.id)\
            .filter(Semester_Table.id == semester_id)\
            .all()

    def get_user(self, user_id):
        return session.query(User_Table)\
            .filter(User_Table.id == user_id)\
            .one()

    def get_student_attendance(self, student_id, semester_id):
            return session.query(User_Table, func.count(User_Table.id)) \
                .filter(student_id == User_Table.id)\
                .filter(User_Table.id == StudentSession_Table.studentId) \
                .filter(StudentSession_Table.sessionId == Session_Table.id) \
                .filter(Session_Table.semester_id == Semester_Table.id) \
                .filter(Semester_Table.id == semester_id)\
                .group_by(User_Table.id) \
                .one()

    def get_student_courses(self, student_id, semester_id):
        return session.query(Course_Table)\
            .filter(student_id == user_course_Table.user_id)\
            .filter(user_course_Table.course_id == Course_Table.id)\
            .filter(Course_Table.semester_id == Semester_Table.id)\
            .filter(Semester_Table.id == semester_id)\
            .all()

    def get_students_in_course(self, course_id):
        return session.query(User_Table, func.count(User_Table.id))\
            .filter(Course_Table.id == course_id)\
            .filter(SessionCourses_Table.course_id == course_id)\
            .filter(SessionCourses_Table.studentsession_id == StudentSession_Table.id)\
            .filter(StudentSession_Table.studentId == User_Table.id)\
            .group_by(User_Table.id)\
            .all()

    def get_average_time_in_course(self, student_id, course_id):
        return session.query(StudentSession_Table, User_Table) \
            .filter(Course_Table.id == course_id) \
            .filter(SessionCourses_Table.course_id == course_id) \
            .filter(SessionCourses_Table.studentsession_id == StudentSession_Table.id) \
            .filter(StudentSession_Table.studentId == User_Table.id) \
            .filter(User_Table.id == student_id) \
            .all()

    def get_student_from_studentsession(self, student_id):
        return session.query(User_Table)\
            .filter(User_Table.id == student_id)

    def get_all_roles(self):
        return session.query(Role_Table)\
            .all()

    def get_user_roles(self, user_id):
        return session.query(Role_Table)\
            .filter(Role_Table.id == user_role_Table.role_id)\
            .filter(user_role_Table.user_id == User_Table.id)\
            .filter(User_Table.id == user_id)\
            .all()

    def get_professor_role(self):
        return session.query(Role_Table)\
            .filter(Role_Table.name == "Professor")\
            .one()

    def get_all_current_users(self):
        return session.query(User_Table)\
            .filter(User_Table.deletedAt == None)\
            .all()

    def delete_user(self, user_id):
        user_to_delete = self.get_user(user_id)
        user_to_delete.deletedAt = datetime.now()
        session.commit()

    def check_for_existing_user(self, username):
        try:  # return true if there is an existing user
            user = session.query(User_Table)\
                .filter(User_Table.username == username)\
                .one()
            return True
        except orm.exc.NoResultFound:  # otherwise return false
            return False

    def activate_existing_user(self, username):
        user = session.query(User_Table)\
            .filter(User_Table.username == username)\
            .one()
        user.deletedAt = None
        session.commit()

    def create_user(self, first_name, last_name, username):
        new_user = User_Table(username=username, password=None, firstName=first_name, lastName=last_name,
                              email=username+'@bethel.edu', send_email=0, deletedAt=None)
        session.add(new_user)
        session.commit()

    def set_user_roles(self, username, roles):
        user = session.query(User_Table)\
            .filter(User_Table.username == username)\
            .one()
        user_id = user.id
        for role in roles:
            user_role = user_role_Table(user_id=user_id, role_id=role)
            session.add(user_role)
        session.commit()

    def update_user_info(self, user_id, first_name, last_name, email):
        user = session.query(User_Table)\
            .filter(User_Table.id == user_id)\
            .one()
        user.firstName = first_name
        user.lastName = last_name
        user.email = email
        session.commit()

    def clear_current_roles(self, user_id):
        roles = session.query(user_role_Table)\
            .filter(user_role_Table.user_id == user_id)\
            .all()
        for role in roles:
            session.delete(role)
        session.commit()

    def get_user_by_username(self, username):
        return session.query(User_Table).filter(User_Table.username == username).one()

    def edit_user(self, first_name,last_name, username, email_pref):
        user_to_edit = self.get_user_by_username(username)
        user_to_edit.firstName = first_name
        user_to_edit.lastName = last_name
        user_to_edit.send_email = email_pref
        session.commit()

    def get_role_by_role_id(self, role_id):
        return session.query(Role_Table).filter(Role_Table.id == role_id).one()

    def get_users_to_email(self, groups, cc, bcc):
        users_to_email = []
        for group in groups:
            role = self.get_role_by_role_id(group)
            users_to_email.append(role.name)
        for user_id in cc:
            current_user = self.get_user(user_id)
            users_to_email.append(current_user.firstName + ' ' + current_user.lastName)
        for user_id in bcc:
            current_user = self.get_user(user_id)
            users_to_email.append(current_user.firstName + ' ' + current_user.lastName)
        return users_to_email

# ################### The following methods are all for the cron jobs for this project ################### #

    def get_lab_courses(self, student_term_courses):
        student_term_course_codes = []
        for key in student_term_courses:
            student_term_course_codes.append(student_term_courses[key]['subj_code'] + ' '
                                             + student_term_courses[key]['crse_numb'] + ' '
                                             + student_term_courses[key]['section'])
        lab_courses = session.query(Course_Table).filter(Course_Table.semester_id == Semester_Table.id)\
            .filter(Semester_Table.active == 1).all()
        lab_course_codes = []
        for course in lab_courses:
            lab_course_codes.append(course.dept + ' ' + course.course_num + ' ' + str(course.section))
        student_lab_courses = []
        for student_course in student_term_course_codes:
            if student_course in lab_course_codes:
                student_lab_courses.append(student_course)
        return student_lab_courses

    def get_course_by_course_code(self, course_code):
        course_info = course_code.split()
        course_dept = course_info[0]
        course_num = course_info[1]
        course_section = course_info[2]
        return session.query(Course_Table).filter(Course_Table.dept == course_dept)\
            .filter(Course_Table.course_num == course_num).filter(Course_Table.section == course_section)\
            .filter(Course_Table.semester_id == Semester_Table.id).filter(Semester_Table.active == 1).one()

    def populate_user_courses_cron(self):
        # get all active students
        active_students = session.query(User_Table).filter(User_Table.deletedAt == None)\
            .filter(User_Table.id == user_role_Table.user_id)\
            .filter(user_role_Table.role_id == Role_Table.id)\
            .filter(Role_Table.name == 'Student').all()

        # this block gets student courses from banner and checks if it is valid, exists, and if not it creates it.
        for student in active_students:
            student_courses = student_course_list(student.username)
            print(student_courses)
            student_lab_courses = self.get_lab_courses(student_courses)
            for course in student_lab_courses:
                lab_course = self.get_course_by_course_code(course)
                print(get_info_for_course(lab_course.dept, lab_course.course_num))

        #         if session.query(user_course_Table).filter(user_course_Table.user_id == student.id)\
        #                 .filter(user_course_Table.course_id == lab_course.id).one_or_none():
        #             continue
        #         else:
        #             student_course_entry = user_course_Table(user_id=student.id, course_id=lab_course.id)
        #             session.add(student_course_entry)
        # session.commit()

    # This probably doesn't belong in this file, but it shares a lot of logic with the other cron job above
    def populate_courses_cron(self):
        active_courses = session.query(CourseCode_Table).filter(CourseCode_Table.active == 1).all()
        for course in active_courses:
            print(course.underived)
            if get_course_is_valid(course.dept, course.courseNum):
                print(get_info_for_course(course.dept, course.courseNum))
        if get_course_is_valid('ABC', '123'):
            print('Valid:', get_info_for_course('ABC', '123'))
        else:
            print('Invalid:', get_info_for_course('ABC', '123'))

            # TODO: WSAPI stuff that I can't figure out...
            # url = 'https://wsapi.bethel.edu/course/info/%s/%s' % (course.dept, course.courseNum)
            # request = requests.Request('GET', url)
            # prepped = request.prepare()
            # signature = hmac.new(bytes(app.config['WSAPI_SECRET'], 'utf-8'), prepped.body, digestmod=hashlib.sha512)
            # prepped.headers['Sign'] = signature.hexdigest()
            # with requests.Session() as s:
            #     r = s.send(prepped)
            # course_info = json.loads(r.content)
            # print(course_info)

##########################################################################################################
