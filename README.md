# Bethel University Tutor Labs

Tutorlabs is Bethel's attendance and reporting application for group tutoring sessions that occur on campus. This app
previoiusly existed as a php project, but we are upgrading it to python to improve performance and make future upgrades
quicker and easier. There are seven different labs that all run off of this same code base: Business Lab,
Computer Science Lab, Math Lab, Nursing Lab, Physics Lab, Science Lab, and World Languages and Cultures Lab.

The two main functions for this application are:
* Attendance tracking for students and tutors who attend or work group tutoring sessions.
* Reporting for lab administrators and professors to see the attendance trends.

There are several supporting functions for this application, including creating and editing users and their roles
(which affect their permissions for viewing certain pages) and managing which courses are offered for tutoring.
Additionally, admins can also create Schedules, which create recurring sessions and assign the appropriate tutors and
courses to them, send emails to lab users, and set up new semesters.