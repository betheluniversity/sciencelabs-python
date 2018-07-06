class ScheduleController:
    def __init__(self):
        super(ScheduleController, self).__init__

    # TODO USE THIS METHOD TO FILL TABLE ON SCHEDULE
    def get_schedule_info(self):
        schedule = []
        for i in range(1, 8):
            schedule.append([
                "Name",
                "DOW",
                "Time",
                "Room",
                "courses",
                "tutors",
                "edit/delete"
            ])

        return schedule