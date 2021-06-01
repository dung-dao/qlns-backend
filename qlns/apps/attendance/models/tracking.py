import os
import uuid

from django.db import models


def upload_to(instance, filename):
    _, file_extension = os.path.splitext('/' + filename)
    return 'attendance_faces/' + str(uuid.uuid4()) + file_extension


class Tracking(models.Model):
    attendance = models.ForeignKey(to='Attendance', on_delete=models.CASCADE, related_name='tracking_data')
    is_overtime = models.BooleanField(default=False)

    check_in_time = models.DateTimeField()
    check_in_lat = models.FloatField(null=True)
    check_in_lng = models.FloatField(null=True)
    check_in_outside = models.BooleanField(null=True)

    check_out_time = models.DateTimeField(null=True)
    check_out_lat = models.FloatField(null=True)
    check_out_lng = models.FloatField(null=True)
    check_out_outside = models.BooleanField(null=True)

    check_in_note = models.TextField(null=True)
    check_out_note = models.TextField(null=True)

    location = models.ForeignKey(to='job.Location', on_delete=models.SET_NULL, null=True)

    actual_work_hours = models.FloatField(default=0)
    ot_work_hours = models.FloatField(default=0)

    check_in_image = models.ImageField(upload_to=upload_to, null=True)
    check_in_face_authorized = models.BooleanField(null=True)

    check_out_image = models.ImageField(upload_to=upload_to, null=True)
    check_out_face_authorized = models.BooleanField(null=True)

    def calc_work_hours(self):
        if self.check_out_time is None:
            self.ot_work_hours = 0.0
            self.actual_work_hours = 0.0
            return

        is_overtime = self.check_overtime()
        self.ot_work_hours = (self.check_out_time - self.check_in_time).seconds / 3600 \
            if is_overtime else 0.0
        self.actual_work_hours = self.attendance.schedule.get_work_hours(self.check_in_time, self.check_out_time) \
            if not is_overtime else 0.0

    def check_overtime(self):
        if self.check_out_time is None:
            raise Exception("Validate check out time not null!")

        schedule = self.attendance.schedule
        work_hours = schedule.get_work_hours(self.check_in_time, self.check_out_time)
        return work_hours == 0
