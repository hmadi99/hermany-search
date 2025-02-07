from django.contrib import admin
from .models import Department, Lecturer, Room, Course,  Semester, College, Term, Days, Periods, ScheduleSettings

# Register your models here.
admin.site.register(Department)
admin.site.register(Lecturer)
admin.site.register(Room)
admin.site.register(Course)
admin.site.register(Semester)
admin.site.register(College)
admin.site.register(Term)
admin.site.register(Days)
admin.site.register(Periods)
admin.site.register(ScheduleSettings)


