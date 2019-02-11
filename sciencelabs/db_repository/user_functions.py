from datetime import datetime
from sqlalchemy import func, distinct, orm

from sciencelabs.db_repository import db_session
from sciencelabs.db_repository.db_tables import User_Table, StudentSession_Table, Session_Table, Semester_Table, \
    Role_Table, user_role_Table, Schedule_Table, user_course_Table, Course_Table, CourseCode_Table, \
    SessionCourses_Table, CourseProfessors_Table
from sciencelabs.wsapi.wsapi_controller import WSAPIController


class User:
    def __init__(self):
        self.wsapi = WSAPIController()

    def get_session_students(self, session_id):
        return db_session.query(User_Table, StudentSession_Table) \
            .filter(StudentSession_Table.sessionId == session_id)\
            .filter(StudentSession_Table.studentId == User_Table.id)\
            .all()

    def get_student_info(self, semester_id):
        return db_session.query(User_Table) \
            .filter(User_Table.id == StudentSession_Table.studentId) \
            .filter(StudentSession_Table.sessionId == Session_Table.id) \
            .filter(Session_Table.semester_id == Semester_Table.id) \
            .filter(Semester_Table.id == semester_id) \
            .group_by(User_Table.id)\
            .order_by(User_Table.lastName.asc()) \
            .all()

    def get_user_info(self):
        return db_session.query(User_Table, Role_Table)\
            .filter(User_Table.id == user_role_Table.user_id) \
            .filter(user_role_Table.role_id == Role_Table.id) \
            .filter(User_Table.deletedAt == None) \
            .all()

    def get_unique_session_attendance(self, semester_id):
        return db_session.query(User_Table, func.count(distinct(User_Table.id))) \
            .filter(StudentSession_Table.sessionId == Session_Table.id) \
            .filter(Session_Table.semester_id == Semester_Table.id) \
            .filter(Semester_Table.id == semester_id) \
            .filter(Schedule_Table.id == Session_Table.schedule_id) \
            .filter(StudentSession_Table.studentId == User_Table.id) \
            .group_by(User_Table.id) \
            .all()

    def get_studentsession(self, student_id, semester_id):
        return db_session.query(StudentSession_Table, Session_Table)\
            .filter(StudentSession_Table.studentId == student_id)\
            .filter(StudentSession_Table.sessionId == Session_Table.id)\
            .filter(Session_Table.semester_id == Semester_Table.id)\
            .filter(Semester_Table.id == semester_id)\
            .all()

    def get_user(self, user_id):
        return db_session.query(User_Table)\
            .filter(User_Table.id == user_id)\
            .one_or_none()

    def get_student_attendance(self, student_id, semester_id):
            return db_session.query(User_Table, func.count(User_Table.id)) \
                .filter(student_id == User_Table.id)\
                .filter(User_Table.id == StudentSession_Table.studentId) \
                .filter(StudentSession_Table.sessionId == Session_Table.id) \
                .filter(Session_Table.semester_id == Semester_Table.id) \
                .filter(Semester_Table.id == semester_id)\
                .group_by(User_Table.id) \
                .one()

    def get_unique_sessions_attended(self, student_id, semester_id):
        return db_session.query(func.count(StudentSession_Table.sessionId))\
            .filter(student_id == User_Table.id)\
            .filter(User_Table.id == StudentSession_Table.studentId)\
            .filter(StudentSession_Table.sessionId == Session_Table.id)\
            .filter(Session_Table.semester_id == Semester_Table.id)\
            .filter(Semester_Table.id == semester_id)\
            .group_by(StudentSession_Table.sessionId)\
            .all()

    def get_student_courses(self, student_id, semester_id):
        return db_session.query(Course_Table)\
            .filter(student_id == user_course_Table.user_id)\
            .filter(user_course_Table.course_id == Course_Table.id)\
            .filter(Course_Table.semester_id == Semester_Table.id)\
            .filter(Semester_Table.id == semester_id)\
            .all()

    def get_students_in_course(self, course_id):
        return db_session.query(User_Table, func.count(User_Table.id))\
            .filter(Course_Table.id == course_id)\
            .filter(SessionCourses_Table.course_id == course_id)\
            .filter(SessionCourses_Table.studentsession_id == StudentSession_Table.id)\
            .filter(StudentSession_Table.studentId == User_Table.id)\
            .group_by(User_Table.id)\
            .all()

    def get_average_time_in_course(self, student_id, course_id):
        return db_session.query(StudentSession_Table, User_Table) \
            .filter(Course_Table.id == course_id) \
            .filter(SessionCourses_Table.course_id == course_id) \
            .filter(SessionCourses_Table.studentsession_id == StudentSession_Table.id) \
            .filter(StudentSession_Table.studentId == User_Table.id) \
            .filter(User_Table.id == student_id) \
            .all()

    def get_student_from_studentsession(self, student_id):
        return db_session.query(User_Table)\
            .filter(User_Table.id == student_id)

    def get_all_roles(self):
        return db_session.query(Role_Table)\
            .all()

    def get_user_roles(self, user_id):
        return db_session.query(Role_Table)\
            .filter(Role_Table.id == user_role_Table.role_id)\
            .filter(user_role_Table.user_id == User_Table.id)\
            .filter(User_Table.id == user_id)\
            .all()

    def get_user_role_ids(self, user_id):
        user_roles = db_session.query(Role_Table)\
            .filter(Role_Table.id == user_role_Table.role_id)\
            .filter(user_role_Table.user_id == User_Table.id)\
            .filter(User_Table.id == user_id)\
            .all()
        user_role_ids = []
        for role in user_roles:
            user_role_ids.append(role.id)
        return user_role_ids

    def get_professor_role(self):
        return db_session.query(Role_Table)\
            .filter(Role_Table.name == "Professor")\
            .one()

    def get_all_current_users(self):
        return db_session.query(User_Table)\
            .filter(User_Table.deletedAt == None)\
            .all()

    def get_all_current_students(self):
        return db_session.query(User_Table).filter(User_Table.deletedAt == None)\
            .filter(User_Table.id == user_role_Table.user_id).filter(user_role_Table.role_id == Role_Table.id)\
            .filter(Role_Table.name == 'Student').order_by(User_Table.lastName.asc()).all()

    def get_all_current_tutors(self):
        return db_session.query(User_Table).filter(User_Table.deletedAt == None)\
            .filter(User_Table.id == user_role_Table.user_id).filter(user_role_Table.role_id == Role_Table.id)\
            .filter(Role_Table.name == 'Tutor').order_by(User_Table.lastName.asc()).all()

    def delete_user(self, user_id):
        user_to_delete = self.get_user(user_id)
        user_to_delete.deletedAt = datetime.now()
        db_session.commit()

    def check_for_existing_user(self, username):
        try:  # return true if there is an existing user
            user = db_session.query(User_Table)\
                .filter(User_Table.username == username)\
                .one()
            return True
        except orm.exc.NoResultFound:  # otherwise return false
            return False

    def activate_existing_user(self, username):
        user = db_session.query(User_Table)\
            .filter(User_Table.username == username)\
            .one()
        user.deletedAt = None
        db_session.commit()

    def create_user(self, first_name, last_name, username, send_email):
        new_user = User_Table(username=username, password=None, firstName=first_name, lastName=last_name,
                              email=username+'@bethel.edu', send_email=send_email, deletedAt=None)
        db_session.add(new_user)
        db_session.commit()
        return new_user

    def get_role_by_name(self, role_name):
        return db_session.query(Role_Table).filter(Role_Table.name == role_name).one()

    def set_user_roles(self, username, roles):
        user = self.get_user_by_username(username)
        user_id = user.id
        for role in roles:
            role_entry = self.get_role_by_name(role)
            user_role = user_role_Table(user_id=user_id, role_id=role_entry.id)
            db_session.add(user_role)
        db_session.commit()

    def update_user_info(self, user_id, first_name, last_name, email):
        user = db_session.query(User_Table)\
            .filter(User_Table.id == user_id)\
            .one()
        user.firstName = first_name
        user.lastName = last_name
        user.email = email
        db_session.commit()

    def clear_current_roles(self, user_id):
        roles = db_session.query(user_role_Table)\
            .filter(user_role_Table.user_id == user_id)\
            .all()
        for role in roles:
            db_session.delete(role)
        db_session.commit()

    def get_user_by_username(self, username):
        return db_session.query(User_Table).filter(User_Table.username == username).one_or_none()

    def edit_user(self, first_name,last_name, username, email_pref):
        user_to_edit = self.get_user_by_username(username)
        user_to_edit.firstName = first_name
        user_to_edit.lastName = last_name
        user_to_edit.send_email = email_pref
        db_session.commit()

    def get_role_by_role_id(self, role_id):
        return db_session.query(Role_Table).filter(Role_Table.id == role_id).one()

# ################### The following methods are all for the cron jobs for this project ################### #

    def get_or_create_course(self, course, semester):
        course_entry = db_session.query(Course_Table).filter(Course_Table.crn == course['crn']) \
            .filter(Course_Table.semester_id == semester.id).one_or_none()
        if not course_entry:
            db_start_date = datetime.strptime(course['beginDate'], "%m/%d/%Y").strftime("%Y-%m-%d")
            db_end_date = datetime.strptime(course['endDate'], "%m/%d/%Y").strftime("%Y-%m-%d")
            db_start_time = None
            if course['beginTime']:
                db_start_time = datetime.strptime(course['beginTime'], "%I:%M%p").strftime("%H:%M:%S")
            db_end_time = None
            if course['endTime']:
                db_end_time = datetime.strptime(course['endTime'], "%I:%M%p").strftime("%H:%M:%S")
            course_code = db_session.query(CourseCode_Table) \
                .filter(CourseCode_Table.courseNum == course['cNumber']) \
                .filter(CourseCode_Table.dept == course['subject']).one()
            course_entry = Course_Table(semester_id=semester.id, begin_date=db_start_date,
                                        begin_time=db_start_time, course_num=course['cNumber'],
                                        section=course['section'], crn=course['crn'],
                                        dept=course['subject'], end_date=db_end_date,
                                        end_time=db_end_time, meeting_day=course['meetingDay'],
                                        title=course['title'], course_code_id=course_code.id,
                                        num_attendees=course['enrolled'], room=course['room'])
            db_session.add(course_entry)
            db_session.commit()
        return course_entry

    def check_semester_exists(self, course):
        semester_info = course['term'].split()  # Returns in form ['term', 'year', '-', 'CAS']
        semester = db_session.query(Semester_Table).filter(Semester_Table.term == semester_info[0]) \
            .filter(Semester_Table.year == semester_info[1]).one_or_none()
        if not semester:
            raise Exception
        else:
            return semester

    def get_or_create_professor(self, course):
        professor = db_session.query(User_Table) \
            .filter(User_Table.username == course['instructorUsername']).one_or_none()
        if not professor:
            # Name comes in form 'First M. Last'
            name_info = course['instructor'].split()
            first_name = name_info[0]
            last_name = name_info[2]
            professor = self.create_user(first_name, last_name, course['instructorUsername'], 1)
            self.set_user_roles(professor.username, ['Professor'])
        return professor

    def check_or_create_professor_course(self, professor, course):
        professor_course = db_session.query(CourseProfessors_Table) \
            .filter(CourseProfessors_Table.professor_id == professor.id) \
            .filter(CourseProfessors_Table.course_id == course.id).one_or_none()
        if not professor_course:
            new_professor_course = CourseProfessors_Table(professor_id=professor.id, course_id=course.id)
            db_session.add(new_professor_course)
            db_session.commit()

    def populate_user_courses_cron(self):
        # We will be creating a message as we go to be logged at the end
        message = ''

        # get all active students
        active_students = self.get_all_current_students()

        for student in active_students:
            # Get courses from banner
            student_banner_courses = self.wsapi.get_student_courses(student.username)
            message += student.firstName + ' ' + student.lastName + ' ' + 'Courses:\n'

            # Check if courseCode exists (yes = move on, no = quit)
            for key, course in student_banner_courses.items():
                if db_session.query(CourseCode_Table).filter(CourseCode_Table.courseNum == course['cNumber'])\
                        .filter(CourseCode_Table.dept == course['subject'])\
                        .filter(CourseCode_Table.active == 1).one_or_none():
                    message += course['subject'] + ' ' + course['cNumber'] + '\n'

                    # Check if semester exists (yes = move on, no = throw exception)
                    try:
                        semester = self.check_semester_exists(course)
                    except:
                        message += "Error: Semester not Found"
                        return message

                    # Check if professor exists (yes = move on, no = create professor and move on)
                    professor = self.get_or_create_professor(course)

                    # Check that entry in Course table exists (yes = move on, no = create course and move on)
                    course_entry = self.get_or_create_course(course, semester)

                    # Create a professor_course table entry if needed
                    self.check_or_create_professor_course(professor, course_entry)

                    # Create user_course table entry if needed
                    user_course = db_session.query(user_course_Table).filter(user_course_Table.user_id == student.id)\
                        .filter(user_course_Table.course_id == course_entry.id).one_or_none()
                    if not user_course:
                        new_user_course = user_course_Table(user_id=student.id, course_id=course_entry.id)
                        db_session.add(new_user_course)
                        db_session.commit()

        # return message for logging purposes
        return message

    # This probably doesn't belong in this file, but it shares a lot of logic with the other cron job above
    def populate_courses_cron(self):
        # We will be creating a message as we go to be logged at the end
        message = ''

        # Get all active courseCodes from lab database
        active_courses = db_session.query(CourseCode_Table).filter(CourseCode_Table.active == 1).all()
        for course in active_courses:
            # verify that the course code is valid with banner
            if self.wsapi.validate_course(course.dept, course.courseNum):
                message += "Valid Course Code\n"

                # For each active courseCode get courses (banner):
                banner_courses = self.wsapi.get_course_info(course.dept, course.courseNum)

                # Check to make sure banner_courses isn't None - if it is then the course isn't offered this semester
                # even though is has a valid course code. This check should be redundant in most cases, but potentially
                # not all, which is why I included it.
                if banner_courses:
                    # Update courseCode info
                    course.dept = banner_courses['0']['subject']
                    course.courseNum = banner_courses['0']['cNumber']
                    course.underived = banner_courses['0']['subject'] + banner_courses['0']['cNumber']
                    course.active = 1
                    course.courseName = banner_courses['0']['title']
                    db_session.commit()
                    message += "Course Code edited\n"
                    message += course.underived + " (" + course.courseName + ")\n"

                    for key, banner_course in banner_courses.items():
                        # Check if semester exists (yes = move on, no = throw exception)
                        try:
                            semester = self.check_semester_exists(banner_course)
                        except:
                            message += "Error: Semester not Found"
                            return message

                        # Check if professor exists (yes = move on, no = create professor and move on)
                        professor = self.get_or_create_professor(banner_course)

                        # Check that entry in Course table exists (yes = move on, no = create course and move on)
                        course_entry = self.get_or_create_course(banner_course, semester)

                        # Create a professor_course table entry if needed
                        self.check_or_create_professor_course(professor, course_entry)
                else:
                    message += "Course not offered this semester\n"
            else:
                message += "Invalid Course Code\n"

        # return message for logging purposes
        return message

##########################################################################################################

    def create_user_at_sign_in(self, username, semester):
        wsapi_names = self.wsapi.get_names_from_username(username)
        names = wsapi_names['0']
        first_name = names['firstName']
        if names['prefFirstName']:
            first_name = names['prefFirstName']
        last_name = names['lastName']
        student = self.create_user(first_name, last_name, username, 0)
        self.set_user_roles(username, ['Student'])
        user_courses = self.wsapi.get_student_courses(username)
        for key, course in user_courses.items():
            if db_session.query(CourseCode_Table).filter(CourseCode_Table.courseNum == course['cNumber'])\
                    .filter(CourseCode_Table.dept == course['subject'])\
                    .filter(CourseCode_Table.active == 1).one_or_none():
                course_entry = db_session.query(Course_Table).filter(course['crn'] == Course_Table.crn)\
                    .filter(Course_Table.semester_id == semester.id).one_or_none()
                if course_entry:
                    new_user_course = user_course_Table(user_id=student.id, course_id=course_entry.id)
                    db_session.add(new_user_course)
                    db_session.commit()
        return student

    def get_users_in_group(self, role_id):
        return db_session.query(User_Table).filter(User_Table.id == user_role_Table.user_id)\
            .filter(user_role_Table.role_id == role_id).all()

    def get_email_from_id(self, user_id):
        user = self.get_user(user_id)
        return user.email

    def get_recipient_emails(self, groups, cc_ids):
        emails = []
        for cc in cc_ids:
            emails.append(self.get_email_from_id(cc))
        for group in groups:
            group_users = self.get_users_in_group(group)
            for user in group_users:
                emails.append(self.get_email_from_id(user.id))
        return emails

    def get_bcc_emails(self, bcc_ids):
        emails = []
        for bcc in bcc_ids:
            emails.append(self.get_email_from_id(bcc))
        return emails

    # todo: should we be using session_courses?
    def get_end_of_session_recipients(self):  #, session_courses):
        # todo: ideally we wouldn't use id's, we would use the name.
        admins = self.get_users_in_group(40001)  # Id for admins
        profs = self.get_users_in_group(40005)  # Id for profs
        recipients = []
        for admin in admins:
            if admin.send_email == 1 and admin not in recipients:
                recipients.append(admin)
        for prof in profs:
            if prof.send_email == 1 and prof not in recipients:
                recipients.append(prof)

        return recipients

    def user_is_tutor(self, user_id):
        user_roles = self.get_user_roles(user_id)
        for role in user_roles:
            if role.name == 'Tutor' or role.name == 'Lead Tutor':
                return True
        return False
