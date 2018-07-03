# Packages
from sqlalchemy import MetaData, Table

# Local
from sciencelabs import db

metadata = MetaData()

# Tables
course = Table('Course', metadata, autoload=True, autoload_with=db)
course_code = Table('CourseCode', metadata, autoload=True, autoload_with=db)
course_profs = Table('CourseProfessors', metadata, autoload=True, autoload_with=db)
course_viewer = Table('CourseViewer', metadata, autoload=True, autoload_with=db)
role = Table('Role', metadata, autoload=True, autoload_with=db)
schedule = Table('Schedule', metadata, autoload=True, autoload_with=db)
schedule_course_codes = Table('ScheduleCourseCodes', metadata, autoload=True, autoload_with=db)
semester = Table('Semester', metadata, autoload=True, autoload_with=db)
session = Table('Session', metadata, autoload=True, autoload_with=db)
session_course_codes = Table('SessionCourseCodes', metadata, autoload=True, autoload_with=db)
session_courses = Table('SessionCourses', metadata, autoload=True, autoload_with=db)
student_session = Table('StudentSession', metadata, autoload=True, autoload_with=db)
tutor_schedule = Table('TutorSchedule', metadata, autoload=True, autoload_with=db)
tutor_session = Table('TutorSession', metadata, autoload=True, autoload_with=db)
user = Table('User', metadata, autoload=True, autoload_with=db)
user_course = Table('user_course', metadata, autoload=True, autoload_with=db)
user_role = Table('user_role', metadata, autoload=True, autoload_with=db)

# print('<--------------------------------------------------------------------------------->')
#
# role = Table('Role', metadata, autoload=True, autoload_with=db)
# print(repr(role))
#
# print('<--------------------------------------------------------------------------------->')
#
# s = select([user])
# result = conn.execute(s)
# for row in result:
#     print(row)
#
# print('<--------------------------------------------------------------------------------->')
#
# s = select([user.c.username])
# result = conn.execute(s)
# for row in result:
#     print(row)
#
# print('<--------------------------------------------------------------------------------->')
#
# s = select([role])
# result = conn.execute(s)
# for row in result:
#     print(row)
#
# print('<--------------------------------------------------------------------------------->')
#
# result = conn.execute(select([user, user.c.password]))
# for row in result:
#     print(row)
#
# print('<--------------------------------------------------------------------------------->')
#
# result = conn.execute(select([user, user.c.username]).where(user.c.username == 'bam95899'))  # or user.c.usernmae
# for row in result:
#     print(row)
#
# result.close()
