from django.contrib import admin
from holiday_planner.models import HolidaySchedule, Destination, ScheduleItem

# Register your models here.

admin.site.register(HolidaySchedule)
admin.site.register(Destination)
admin.site.register(ScheduleItem)
