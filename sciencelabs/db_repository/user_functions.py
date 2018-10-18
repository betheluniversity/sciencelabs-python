from datetime import datetime, time
from sqlalchemy import func, distinct, orm

from sciencelabs.db_repository import session
from sciencelabs.db_repository.db_tables import User_Table, StudentSession_Table, Session_Table, Semester_Table, \
    Role_Table, user_role_Table, Schedule_Table, user_course_Table, Course_Table, CourseCode_Table, \
    SessionCourseCodes_Table, CourseViewer_Table, SessionCourses_Table, CourseProfessors_Table
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

    def create_user(self, first_name, last_name, username, send_email):
        new_user = User_Table(username=username, password=None, firstName=first_name, lastName=last_name,
                              email=username+'@bethel.edu', send_email=send_email, deletedAt=None)
        session.add(new_user)
        session.commit()
        return new_user

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

    def populate_user_courses_cron(self):
        print(get_info_for_course('MAT', '125'))
        # We will be creating a message as we go to be logged at the end
        message = ''
        # get all active students
        active_students = session.query(User_Table).filter(User_Table.deletedAt == None)\
            .filter(User_Table.id == user_role_Table.user_id)\
            .filter(user_role_Table.role_id == Role_Table.id)\
            .filter(Role_Table.name == 'Student').all()

        for student in active_students:
            # Get courses from banner
            student_banner_courses = student_course_list(student.username)
            print(student_banner_courses)
            message += student.firstName + ' ' + student.lastName + ' ' + 'Courses:\n'
            # Check if courseCode exists (yes = move on, no = quit)
            for key, course in student_banner_courses.items():
                if session.query(CourseCode_Table).filter(CourseCode_Table.courseNum == course['crse_numb'])\
                        .filter(CourseCode_Table.dept == course['subj_code'])\
                        .filter(CourseCode_Table.active == 1).one_or_none():
                    message += course['subj_code'] + ' ' + course['crse_numb'] + '\n'
                    # For this valid lab course we need to get it's full info now
                    possible_courses = get_info_for_course(course['subj_code'], course['crse_numb'])
                    # Get right section for the student
                    for key, possible_course in possible_courses.items():
                        if possible_course['section'] == course['section']:
                            student_course = possible_course
                    semester_info = student_course['term'].split()  # Returns in form ['term', 'year', '-', 'CAS']
                    # Check if semester exists (yes = move on, no = throw exception)
                    semester = session.query(Semester_Table).filter(Semester_Table.term == semester_info[0])\
                        .filter(Semester_Table.year == semester_info[1]).one_or_none()
                    if not semester:
                        raise Exception
                    # Check if professor exists (yes = move on, no = create professor and move on)
                    professor = session.query(User_Table)\
                        .fitler(User_Table.username == student_course['instructorUsername']).one_or_none()
                    if not professor:
                        # Name comes in form 'First M. Last'
                        name_info = student_course['instructor'].split()
                        first_name = name_info[0]
                        last_name = name_info[2]
                        professor = self.create_user(first_name, last_name, student_course['instructorUsername'], 1)
                        self.set_user_roles(professor.username, [40005])
                    # Check that entry in Course table exists (yes = move on, no = create course and move on)
                    course_entry = session.query(Course_Table).filter(Course_Table.crn == student_course['crn'])\
                        .filter(Course_Table.semester_id == semester.id).one_or_none()
                    if not course_entry:
                        db_start_date = datetime.strptime(student_course['beginDate'], "%m/%d/%Y").strftime("%Y-%m-%d")
                        db_end_date = datetime.strptime(student_course['endDate'], "%m/%d/%Y").strftime("%Y-%m-%d")
                        db_start_time = datetime.strptime(student_course['beginTime'], "%I:%M%p").strftime("%H:%M:%S")
                        db_end_time = datetime.strptime(student_course['endTime'], "%I:%M%p").strftime("%H:%M:%S")
                        course_code = session.query(CourseCode_Table)\
                            .filter(CourseCode_Table.courseNum == student_course['cNumber'])\
                            .filter(CourseCode_Table.dept == student_course['subject']).one()
                        course_entry = Course_Table(semester_id=semester.id, begin_date=db_start_date,
                                                    begin_time=db_start_time, course_num=student_course['cNumber'],
                                                    section=student_course['section'], crn=student_course['crn'],
                                                    dept=student_course['subject'], end_date=db_end_date,
                                                    end_time=db_end_time, meeting_day=student_course['meetingDay'],
                                                    title=student_course['title'], course_code_id=course_code.id,
                                                    num_attendees=student_course['enrolled'], room=student_course['room'])
                        session.add(course_entry)
                    # Create a professor_course table entry
                    professor_course = CourseProfessors_Table(professor_id=professor.id, course_id=course_entry.id)
                    session.add(professor_course)
                    # Create user_course table entry
                    new_user_course = user_course_Table(user_id=student.id, course_id=course_entry.id)
                    session.add(new_user_course)
        session.commit()
        # return message for logging purposes
        return message

    # This probably doesn't belong in this file, but it shares a lot of logic with the other cron job above
    def populate_courses_cron(self):
        # We will be creating a message as we go to be logged at the end
        message = ''
        # Get all active courseCodes
        active_courses = session.query(CourseCode_Table).filter(CourseCode_Table.active == 1).all()
        for course in active_courses:
            print(course.underived)
            # validate course with banner
            if get_course_is_valid(course.dept, course.courseNum):
                print(get_info_for_course(course.dept, course.courseNum))
                # For each active courseCode get courses (banner):
                banner_courses = get_info_for_course(course.dept, course.courseNum)
                # Update courseCode info
                course.dept = banner_courses[0]['subject']
                course.courseNum = banner_courses[0]['cNumber']
                course.underived = banner_courses[0]['subject'] + banner_courses[0]['cNumber']
                course.active = 1
                course.courseName = banner_courses[0]['title']
                for key, banner_course in banner_courses.items():
                    # Check if semester exists (yes = move on, no = throw exception)
                    semester_info = banner_course['term'].split()  # Returns in form ['term', 'year', '-', 'CAS']
                    semester = session.query(Semester_Table).filter(Semester_Table.term == semester_info[0]) \
                        .filter(Semester_Table.year == semester_info[1]).one_or_none()
                    if not semester:
                        raise Exception
                    # Check if professor exists (yes = move on, no = create professor and move on)
                    professor = session.query(User_Table) \
                        .fitler(User_Table.username == banner_course['instructorUsername']).one_or_none()
                    if not professor:
                        # Name comes in form 'First M. Last'
                        name_info = banner_course['instructor'].split()
                        first_name = name_info[0]
                        last_name = name_info[2]
                        professor = self.create_user(first_name, last_name, banner_course['instructorUsername'], 1)
                        self.set_user_roles(professor.username, [40005])
                    # Check that entry in Course table exists (yes = move on, no = create course and move on)
                    course_entry = session.query(Course_Table).filter(Course_Table.crn == banner_course['crn']) \
                        .filter(Course_Table.semester_id == semester.id).one_or_none()
                    if not course_entry:
                        db_start_date = datetime.strptime(banner_course['beginDate'], "%m/%d/%Y").strftime("%Y-%m-%d")
                        db_end_date = datetime.strptime(banner_course['endDate'], "%m/%d/%Y").strftime("%Y-%m-%d")
                        db_start_time = datetime.strptime(banner_course['beginTime'], "%I:%M%p").strftime("%H:%M:%S")
                        db_end_time = datetime.strptime(banner_course['endTime'], "%I:%M%p").strftime("%H:%M:%S")
                        course_code = session.query(CourseCode_Table) \
                            .filter(CourseCode_Table.courseNum == banner_course['cNumber']) \
                            .filter(CourseCode_Table.dept == banner_course['subject']).one()
                        course_entry = Course_Table(semester_id=semester.id, begin_date=db_start_date,
                                                    begin_time=db_start_time, course_num=banner_course['cNumber'],
                                                    section=banner_course['section'], crn=banner_course['crn'],
                                                    dept=banner_course['subject'], end_date=db_end_date,
                                                    end_time=db_end_time, meeting_day=banner_course['meetingDay'],
                                                    title=banner_course['title'], course_code_id=course_code.id,
                                                    num_attendees=banner_course['enrolled'], room=banner_course['room'])
                        session.add(course_entry)
                    # Create a professor_course table entry
                    professor_course = CourseProfessors_Table(professor_id=professor.id, course_id=course_entry.id)
                    session.add(professor_course)
        session.commit()
        # return message for logging purposes
        return message

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

    def test(self):
        print(get_course_is_valid('MAT', '125'))
        print(get_info_for_course('MAT', '125'))

##########################################################################################################
