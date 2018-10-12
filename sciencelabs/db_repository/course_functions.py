import requests
import hmac
import hashlib

from datetime import datetime, timedelta
from sqlalchemy import orm
from flask import json

from sciencelabs import app
from sciencelabs.db_repository import session
from sciencelabs.db_repository.db_tables import User_Table, Course_Table, CourseProfessors_Table, Semester_Table, \
    Session_Table, CourseCode_Table, SessionCourses_Table, StudentSession_Table, CourseViewer_Table
from sciencelabs.oracle_procs.db_functions import get_course_is_valid, get_info_for_course

class Course:

    def get_course_info(self):
        return (session.query(Course_Table, User_Table)
                .filter(Course_Table.num_attendees)
                .filter(User_Table.id == CourseProfessors_Table.professor_id)
                .filter(CourseProfessors_Table.course_id == Course_Table.id)
                .filter(Course_Table.semester_id == Semester_Table.id)
                .filter(Semester_Table.active == 1)
                .all())

    def get_active_course_info(self, semester_id):
        return (session.query(Course_Table, User_Table)
                .filter(Course_Table.num_attendees)
                .filter(User_Table.id == CourseProfessors_Table.professor_id)
                .filter(CourseProfessors_Table.course_id == Course_Table.id)
                .filter(Course_Table.semester_id == Semester_Table.id)
                .filter(Semester_Table.active == 1)
                .all())

    def get_selected_course_info(self, semester_id):
        return (session.query(Course_Table, User_Table)
                .filter(User_Table.id == CourseProfessors_Table.professor_id)
                .filter(CourseProfessors_Table.course_id == Course_Table.id)
                .filter(Course_Table.semester_id == Semester_Table.id)
                .filter(Semester_Table.id == semester_id)
                .all())

    def get_semester_courses(self, semester_id):
        return session.query(Course_Table.dept, Course_Table.course_num, CourseCode_Table.courseName, CourseCode_Table.id)\
            .filter(Course_Table.semester_id == semester_id)\
            .filter(Course_Table.course_code_id == CourseCode_Table.id).distinct()

    def get_student_courses(self, student_id, semester_id):
        return session.query(Course_Table.id, Course_Table.dept, Course_Table.course_num, CourseCode_Table.courseName)\
            .filter(CourseCode_Table.id == Course_Table.course_code_id)\
            .filter(Course_Table.id == SessionCourses_Table.course_id)\
            .filter(SessionCourses_Table.studentsession_id == StudentSession_Table.id)\
            .filter(StudentSession_Table.sessionId == Session_Table.id)\
            .filter(Session_Table.semester_id == semester_id) \
            .filter(StudentSession_Table.studentId == User_Table.id)\
            .filter(User_Table.id == student_id)\
            .distinct()

    def get_course(self, course_id):
        return session.query(Course_Table, User_Table, Semester_Table)\
            .filter(Course_Table.id == course_id)\
            .filter(CourseProfessors_Table.course_id == course_id)\
            .filter(CourseProfessors_Table.professor_id == User_Table.id)\
            .filter(Course_Table.semester_id == Semester_Table.id)\
            .one()

    def get_courses_for_session(self, session_id):
        return session.query(Course_Table)\
            .filter(Course_Table.id == SessionCourses_Table.course_id)\
            .filter(SessionCourses_Table.studentsession_id == StudentSession_Table.id)\
            .filter(StudentSession_Table.sessionId == session_id)\
            .all()

    def get_professor_courses(self, prof_id):
        return session.query(Course_Table)\
            .filter(CourseProfessors_Table.course_id == Course_Table.id)\
            .filter(CourseProfessors_Table.professor_id == prof_id) \
            .filter(Course_Table.semester_id == Semester_Table.id)\
            .filter(Semester_Table.active == 1)\
            .all()

    def get_semester_courses_with_section(self, semester_id):
        return session.query(Course_Table)\
            .filter(Course_Table.semester_id == semester_id)\
            .all()

    def get_active_coursecode(self):
        return session.query(CourseCode_Table)\
            .filter(CourseCode_Table.active == 1)\
            .all()

    def check_for_existing_coursecode(self, cc_info):
        try:
            coursecode = session.query(CourseCode_Table)\
                .filter(cc_info['subject'] == CourseCode_Table.dept)\
                .filter(cc_info['cNumber'] == CourseCode_Table.courseNum)\
                .filter(cc_info['title'] == CourseCode_Table.courseName)\
                .one()
            return True
        except orm.exc.NoResultFound:
            return False

    def check_if_existing_coursecode_is_active(self, cc_info):
        coursecode = session.query(CourseCode_Table)\
                .filter(cc_info['subject'] == CourseCode_Table.dept)\
                .filter(cc_info['cNumber'] == CourseCode_Table.courseNum)\
                .filter(cc_info['title'] == CourseCode_Table.courseName)\
                .one()
        if coursecode.active == 0:
            self.activate_existing_coursecode(cc_info)

    def activate_existing_coursecode(self, cc_info):
        coursecode = session.query(CourseCode_Table)\
            .filter(cc_info['subject'] == CourseCode_Table.dept)\
            .filter(cc_info['cNumber'] == CourseCode_Table.courseNum)\
            .filter(cc_info['title'] == CourseCode_Table.courseName)\
            .one()
        coursecode.active = 1
        session.commit()

    def create_coursecode(self, cc_info):
        new_coursecode = CourseCode_Table(dept=cc_info['subject'], courseNum=cc_info['cNumber'],
                                          underived=(cc_info['subject'] + cc_info['cNumber']), active=1,
                                          courseName=cc_info['title'])
        session.add(new_coursecode)
        session.commit()

    def check_for_existing_course(self, c_info):
        try:
            course = session.query(Course_Table)\
                .filter(c_info['crn'] == Course_Table.crn)\
                .filter(c_info['subject'] == Course_Table.dept)\
                .filter(c_info['cNumber'] == Course_Table.course_num)\
                .filter(c_info['section'] == Course_Table.section)\
                .filter(c_info['meetingDay'] == Course_Table.meeting_day)\
                .filter(c_info['title'] == Course_Table.title)\
                .filter(c_info['enrolled'] == Course_Table.num_attendees)\
                .filter(c_info['room'] == Course_Table.room)\
                .one()
            return True
        except orm.exc.NoResultFound:
            return False

    def get_coursecode(self, cc_info):
        return session.query(CourseCode_Table)\
            .filter(cc_info['subject'] == CourseCode_Table.dept)\
            .filter(cc_info['cNumber'] == CourseCode_Table.courseNum)\
            .filter(cc_info['title'] == CourseCode_Table.courseName)\
            .one()

    def create_course(self, c_info):
        coursecode = self.get_coursecode(c_info)
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

        # TODO DON'T REALLY KNOW WHETHER TO CREATE IT OR NOT WHEN TERM/YEAR DOESN'T EXIST, RIGHT NOW WE ARE JUST CREATING IT
        # TODO MAYBE JUST MAKE IT IF THE CLASS IS DURING THE CURRENT ACTIVE TERM/YEAR

        semester_id = None
        semester_list = session['SEMESTER-LIST']
        for semesters in semester_list:
            if semesters.year == year and semesters.term == term:
                semester_id = semesters.id

        new_course = Course_Table(semester_id=semester_id, begin_date=begin_date,
                                  begin_time=begin_time, course_num=c_info['cNumber'],
                                  section=c_info['section'], crn=c_info['crn'], dept=c_info['subject'],
                                  end_date=end_date, end_time=end_time,
                                  meeting_day=c_info['meetingDay'], title=c_info['title'], course_code_id=coursecode.id,
                                  num_attendees=c_info['enrolled'], room=c_info['room'])
        session.add(new_course)
        session.commit()

        user = session.query(User_Table).filter(User_Table.username == c_info['instructorUsername']).first()

        if user:
            new_courseprofessor = CourseProfessors_Table(course_id=new_course.id, professor_id=user.id)
            session.add(new_courseprofessor)
            session.commit()

    def deactivate_coursecode(self, dept, course_num):
        coursecode = session.query(CourseCode_Table) \
            .filter(dept == CourseCode_Table.dept) \
            .filter(course_num == CourseCode_Table.courseNum) \
            .one()
        coursecode.active = 0
        session.commit()

    def delete_course(self, course, user):

        does_exist = self.check_for_existing_courseviewer(course.id)
        if does_exist:
            self.delete_courseviewer(course.id)

        courseprofessor = session.query(CourseProfessors_Table)\
            .filter(CourseProfessors_Table.course_id == course.id)\
            .filter(CourseProfessors_Table.professor_id == user.id)\
            .one()

        session.delete(courseprofessor)
        session.commit()

        session.delete(course)
        session.commit()

    def check_for_existing_courseviewer(self, course_id):
        try:
            courseviewer = session.query(CourseViewer_Table)\
                .filter(CourseViewer_Table.course_id == course_id)\
                .one()
            return True
        except orm.exc.NoResultFound:
            return False

    def delete_courseviewer(self, course_id):
        courseviewers = session.query(CourseViewer_Table)\
            .filter(CourseViewer_Table.course_id == course_id)\
            .all()

        if courseviewers:
            for courseviewer in courseviewers:
                session.delete(courseviewer)
                session.commit()

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

