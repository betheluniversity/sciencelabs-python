from datetime import datetime, timedelta
from sqlalchemy import orm
from sqlalchemy.orm.exc import MultipleResultsFound
from flask import session as flask_session, abort
from sciencelabs.db_repository import db_session
from sciencelabs.db_repository.db_tables import User_Table, Course_Table, CourseProfessors_Table, Semester_Table, \
    Session_Table, CourseCode_Table, SessionCourses_Table, StudentSession_Table, CourseViewer_Table, \
    ScheduleCourseCodes_Table, SessionCourseCodes_Table, user_role_Table, Role_Table, user_course_Table
from sciencelabs.wsapi.wsapi_controller import WSAPIController


class Course:
    def __init__(self):
        self.wsapi = WSAPIController()

    def get_course_info(self):
        return (db_session.query(Course_Table, User_Table)
                .filter(Course_Table.num_attendees)
                .filter(User_Table.id == CourseProfessors_Table.professor_id)
                .filter(CourseProfessors_Table.course_id == Course_Table.id)
                .filter(Course_Table.semester_id == Semester_Table.id)
                .filter(Semester_Table.active == 1)
                .all())

    def get_active_course_info(self):
        return (db_session.query(Course_Table, User_Table)
                .filter(Course_Table.num_attendees)
                .filter(User_Table.id == CourseProfessors_Table.professor_id)
                .filter(CourseProfessors_Table.course_id == Course_Table.id)
                .filter(Course_Table.semester_id == Semester_Table.id)
                .filter(Semester_Table.active == 1)
                .all())

    def get_selected_course_info(self, semester_id):
        return (db_session.query(Course_Table, User_Table)
                .filter(User_Table.id == CourseProfessors_Table.professor_id)
                .filter(CourseProfessors_Table.course_id == Course_Table.id)
                .filter(Course_Table.semester_id == Semester_Table.id)
                .filter(Semester_Table.id == semester_id)
                .all())

    def get_other_info(self, semester_id):
        return db_session.query(StudentSession_Table)\
            .filter(User_Table.id == StudentSession_Table.studentId)\
            .filter(StudentSession_Table.otherCourseName != "")\
            .filter(StudentSession_Table.otherCourseName != None)\
            .filter(StudentSession_Table.sessionId == Session_Table.id)\
            .filter(Session_Table.semester_id == Semester_Table.id)\
            .filter(Semester_Table.id == semester_id)\
            .all()

    def get_selected_prof_course_info(self, semester_id, prof_id):
        return (db_session.query(Course_Table, User_Table)
                .filter(User_Table.id == prof_id)
                .filter(User_Table.id == CourseProfessors_Table.professor_id)
                .filter(CourseProfessors_Table.course_id == Course_Table.id)
                .filter(Course_Table.semester_id == Semester_Table.id)
                .filter(Semester_Table.id == semester_id)
                .all())

    def get_selected_course_viewer_info(self, semester_id, prof_id):
        return (db_session.query(Course_Table, User_Table)
                .filter(Course_Table.id == CourseProfessors_Table.course_id)
                .filter(CourseProfessors_Table.professor_id == User_Table.id)
                .filter(CourseViewer_Table.user_id == prof_id)
                .filter(CourseViewer_Table.course_id == Course_Table.id)
                .filter(Course_Table.semester_id == semester_id)
                .all())

    def get_semester_courses(self, semester_id):
        return db_session.query(Course_Table.dept, Course_Table.course_num, CourseCode_Table.courseName,
                                CourseCode_Table.id)\
            .filter(Course_Table.semester_id == semester_id)\
            .filter(Course_Table.course_code_id == CourseCode_Table.id).distinct()

    def get_student_courses(self, student_id, semester_id):
        return db_session.query(Course_Table.id, Course_Table.dept, Course_Table.course_num,
                                CourseCode_Table.courseName)\
            .filter(user_course_Table.user_id == student_id)\
            .filter(user_course_Table.course_id == Course_Table.id)\
            .filter(Course_Table.semester_id == semester_id)\
            .filter(Course_Table.course_code_id == CourseCode_Table.id)\
            .distinct()

    def get_course(self, course_id):
        return db_session.query(Course_Table).filter(Course_Table.id == course_id).one()

    def get_courses_for_session(self, session_id):
        return db_session.query(Course_Table)\
            .filter(Course_Table.id == SessionCourses_Table.course_id)\
            .filter(SessionCourses_Table.studentsession_id == StudentSession_Table.id)\
            .filter(StudentSession_Table.sessionId == session_id)\
            .all()

    def get_professor_courses(self, prof_id, semester_id):
        teaching_courses = db_session.query(Course_Table) \
            .filter(CourseProfessors_Table.course_id == Course_Table.id) \
            .filter(CourseProfessors_Table.professor_id == prof_id) \
            .filter(Course_Table.semester_id == Semester_Table.id)\
            .filter(Semester_Table.id == semester_id)\
            .all()
        viewing_courses = db_session.query(Course_Table) \
            .filter(Course_Table.id == CourseViewer_Table.course_id) \
            .filter(CourseViewer_Table.user_id == prof_id) \
            .all()
        all_courses = []
        for course in teaching_courses:
            all_courses.append(course)
        for course in viewing_courses:
            all_courses.append(course)
        return all_courses

    def get_professor_teaching_courses(self, prof_id, semester_id):
        return db_session.query(Course_Table) \
            .filter(CourseProfessors_Table.course_id == Course_Table.id) \
            .filter(CourseProfessors_Table.professor_id == prof_id) \
            .filter(Course_Table.semester_id == Semester_Table.id)\
            .filter(Semester_Table.id == semester_id)\
            .all()

    def get_course_viewer_courses(self, user_id):
        return db_session.query(Course_Table) \
            .filter(Course_Table.id == CourseViewer_Table.course_id) \
            .filter(CourseViewer_Table.user_id == user_id) \
            .all()

    def get_semester_courses_with_section(self, semester_id):
        return db_session.query(Course_Table)\
            .filter(Course_Table.semester_id == semester_id)\
            .all()

    def get_active_coursecode(self):
        return db_session.query(CourseCode_Table)\
            .filter(CourseCode_Table.active == 1)\
            .all()

    def create_coursecode(self, cc_info):
        new_coursecode = CourseCode_Table(dept=cc_info['subject'], courseNum=cc_info['cNumber'],
                                          underived=(cc_info['subject'] + cc_info['cNumber']), active=1,
                                          courseName=cc_info['title'])
        db_session.add(new_coursecode)
        db_session.commit()
        return new_coursecode

    def create_course(self, c_info, coursecode):
        begin_date = c_info['beginDate']
        begin_date = datetime.strptime(begin_date, '%m/%d/%Y')
        begin_date.strftime('%Y-%m-%d')
        end_date = c_info['endDate']
        end_date = datetime.strptime(end_date, '%m/%d/%Y')
        end_date.strftime('%Y-%m-%d')

        begin_time = c_info['beginTime']
        begin_time = datetime.strptime(begin_time, '%I:%M%p')

        begin_time = timedelta(hours=begin_time.hour, minutes=begin_time.minute, seconds=begin_time.second)

        end_time = c_info['endTime']
        end_time = datetime.strptime(end_time, '%I:%M%p')

        end_time = timedelta(hours=end_time.hour, minutes=end_time.minute, seconds=end_time.second)

        term, year, *rest = (c_info['term'].split('-')[0].split(' '))

        semester = db_session.query(Semester_Table).filter(Semester_Table.active == 1).one()

        new_course = Course_Table(semester_id=semester.id, begin_date=begin_date,
                                  begin_time=begin_time, course_num=c_info['cNumber'],
                                  section=c_info['section'], crn=c_info['crn'], dept=c_info['subject'],
                                  end_date=end_date, end_time=end_time,
                                  meeting_day=c_info['meetingDay'], title=c_info['title'], course_code_id=coursecode.id,
                                  num_attendees=c_info['enrolled'], room=c_info['room'])
        db_session.add(new_course)
        db_session.commit()

        user = db_session.query(User_Table).filter(User_Table.username == c_info['instructorUsername']).one_or_none()

        if not user:
            user = self.create_new_prof(c_info['instructorUsername'])

        new_courseprofessor = CourseProfessors_Table(course_id=new_course.id, professor_id=user.id)
        db_session.add(new_courseprofessor)
        db_session.commit()

    def create_new_prof(self, prof_username):
        wsapi_names = self.wsapi.get_names_from_username(prof_username)
        if not wsapi_names:
            abort(503)
        names = wsapi_names['0']
        first_name = names['firstName']
        if names['prefFirstName']:
            first_name = names['prefFirstName']
        last_name = names['lastName']
        prof = self.create_user(first_name, last_name, prof_username, 0)
        self.set_user_roles(prof.id, ['Professor'])

    def create_user(self, first_name, last_name, username, send_email):
        new_user = User_Table(username=username, password=None, firstName=first_name, lastName=last_name,
                              email='{0}@bethel.edu'.format(username), send_email=send_email, deletedAt=None)
        db_session.add(new_user)
        db_session.commit()
        return new_user

    def set_user_roles(self, user_id, roles):
        for role in roles:
            role_entry = self.get_role_by_name(role)
            # Check if the user already has this role
            role_exists = db_session.query(user_role_Table)\
                .filter(user_role_Table.user_id == user_id)\
                .filter(user_role_Table.role_id == role_entry.id)\
                .one_or_none()
            if role_exists:  # If they do, skip adding it again
                continue
            user_role = user_role_Table(user_id=user_id, role_id=role_entry.id)
            db_session.add(user_role)
        db_session.commit()

    def get_role_by_name(self, role_name):
        return db_session.query(Role_Table).filter(Role_Table.name == role_name).one()

    def delete_course(self, course_id):
        course = db_session.query(Course_Table).filter(Course_Table.id == course_id).one_or_none()
        if course:
            course_profs = db_session.query(CourseProfessors_Table)\
                .filter(CourseProfessors_Table.course_id == course_id).all()
            for prof in course_profs:
                db_session.delete(prof)
            db_session.delete(course)
            db_session.commit()

    def check_for_existing_courseviewer(self, course_id):
        try:
            courseviewer = db_session.query(CourseViewer_Table)\
                .filter(CourseViewer_Table.course_id == course_id)\
                .one()
            return True
        except orm.exc.NoResultFound:
            return False

    def delete_courseviewer(self, course_id):
        courseviewers = db_session.query(CourseViewer_Table)\
            .filter(CourseViewer_Table.course_id == course_id)\
            .all()

        if courseviewers:
            for courseviewer in courseviewers:
                db_session.delete(courseviewer)
                db_session.commit()

    def get_profs_from_course(self, course_id):
        profs = db_session.query(User_Table)\
            .filter(User_Table.id == CourseProfessors_Table.professor_id)\
            .filter(CourseProfessors_Table.course_id == course_id)\
            .all()
        prof_names = []
        for prof in profs:
            prof_names.append("{0} {1}".format(prof.firstName, prof.lastName))
        return prof_names

    # Checks if the student is in the profs courses, returns true if yes
    def student_is_in_prof_course(self, student_id, prof_id):
        student_courses = self.get_student_courses(student_id, flask_session['SELECTED-SEMESTER'])
        student_course_ids = []
        for course in student_courses:
            student_course_ids.append(course.id)

        prof_courses = self.get_professor_courses(prof_id, flask_session['SELECTED-SEMESTER'])
        for course in prof_courses:
            if course.id in student_course_ids:
                return True

        return False

    def get_enrolled_students_for_semester(self, semester_id):
        semeseter_courses = self.get_semester_courses_with_section(semester_id)
        enrolled = 0
        for course in semeseter_courses:
            enrolled = enrolled + course.num_attendees if course.num_attendees else enrolled
        return enrolled

    def get_schedule_course_ids(self, schedule_id):
        schedule_courses = db_session.query(ScheduleCourseCodes_Table)\
            .filter(ScheduleCourseCodes_Table.schedule_id == schedule_id)\
            .all()
        schedule_course_ids = []
        for course in schedule_courses:
            schedule_course_ids.append(course.coursecode_id)
        return schedule_course_ids

    def get_session_course_ids(self, session_id):
        session_courses = db_session.query(SessionCourseCodes_Table) \
            .filter(SessionCourseCodes_Table.session_id == session_id).all()
        session_course_ids = []
        for course in session_courses:
            session_course_ids.append(course.coursecode_id)
        return session_course_ids

    def new_term_course_code(self, course_info):
        try:
            existing_course_code = db_session.query(CourseCode_Table)\
                .filter(CourseCode_Table.dept == course_info['0']['subject'])\
                .filter(CourseCode_Table.courseNum == course_info['0']['cNumber'])\
                .filter(CourseCode_Table.courseName == course_info['0']['title'])\
                .one_or_none()
        except MultipleResultsFound:
            existing_course_code = db_session.query(CourseCode_Table)\
                .filter(CourseCode_Table.dept == course_info['0']['subject'])\
                .filter(CourseCode_Table.courseNum is course_info['0']['cNumber'])\
                .filter(CourseCode_Table.courseName == course_info['0']['title'])\
                .one_or_none()

        if existing_course_code:
            if existing_course_code.active == 0:
                existing_course_code.active = 1
                db_session.commit()
            return existing_course_code

        else:
            new_course_code = self.create_coursecode(course_info['0'])
            return new_course_code

    def new_term_course(self, all_course_info, course_code):
        semester = db_session.query(Semester_Table).filter(Semester_Table.active == 1).one()
        for key, course_info in all_course_info.items():
            existing_course = db_session.query(Course_Table)\
                    .filter(semester.id == Course_Table.semester_id)\
                    .filter(course_info['crn'] == Course_Table.crn)\
                    .filter(course_info['subject'] == Course_Table.dept)\
                    .filter(course_info['cNumber'] == Course_Table.course_num)\
                    .filter(course_info['section'] == Course_Table.section)\
                    .filter(course_info['title'] == Course_Table.title)\
                    .one_or_none()

            if not existing_course:
                self.create_course(course_info, course_code)

    def get_current_courses(self):
        return db_session.query(Course_Table).filter(Course_Table.semester_id == Semester_Table.id)\
            .filter(Semester_Table.active == 1).all()

    def get_course_profs(self, course_id):
        return db_session.query(User_Table).filter(User_Table.id == CourseProfessors_Table.professor_id)\
            .filter(CourseProfessors_Table.course_id == course_id).all()
