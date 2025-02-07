from django.db import models
from django.contrib.auth.models import User



class College(models.Model):
    name = models.CharField(max_length=100)
    user = models.OneToOneField(User, models.SET_NULL ,null=True, blank=True)  # لكل كلية حساب مرتبط
    logo = models.ImageField(upload_to='college_logos/', null=True, blank=True)  # حقل الشعار
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Semester(models.Model):
    semester_name = models.CharField(max_length=30, null=True)
    semester_number = models.IntegerField()
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    

    def __str__(self):
        return str(self.semester_name)  
    
class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True)
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.name}-{self.semester}"

class Lecturer(models.Model):
    name = models.CharField(max_length=100)
    number = models.IntegerField()
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    def __str__(self):
        return self.name

class Room(models.Model):
    ROOM_TYPES = [
        ('hall', 'قاعة'),
        ('computer_lab', 'معمل حاسوب'),
        ('chemistry_lab', 'معمل كيمياء'),
        ('rocks_lab', 'معمل صخور'),
        ('biology_lab', 'معمل أحياء'),
        ('movable_prosthetics_lab', 'معمل التركيبات المتحركة'),
        ('dental_lab', 'معمل صناعة الأسنان'),
        ('fixed_prosthetics_lab', 'معمل التركيبات الثابتة'),
        ('casting_lab', 'معمل الصب'),
        ('conservative_lab', 'معمل العلاج التحفظي'),
        ('electrical_engineering_lab', 'معمل هندسة كهربائية وإلكترونية'),
        ('materials_engineering_lab', 'معمل هندسة المواد'),
        ('renewable_energy_lab', 'معمل الطاقات المتجددة'),
    ]
    name = models.CharField(max_length=50)
    capacity = models.IntegerField()
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    room_type = models.CharField(max_length=400, choices=ROOM_TYPES, default='hall')
    def __str__(self):
        return f"{self.name} - {self.get_room_type_display()}"
    
    
class Course(models.Model):
    ROOM_TYPES = [
        ('hall', 'قاعة'),
        ('computer_lab', 'معمل حاسوب'),
        ('chemistry_lab', 'معمل كيمياء'),
        ('rocks_lab', 'معمل صخور'),
        ('biology_lab', 'معمل أحياء'),
    ]
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    department = models.ManyToManyField(Department)
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE)
    student_count = models.IntegerField(default=0)
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    required_room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='hall')

    def __str__(self):
        return self.name




class Term(models.Model):
    name = models.CharField(max_length=50)  
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name



class Days(models.Model):
    name = models.CharField(max_length=50) 
    
    def __str__(self):
        return self.name
    
    
class Periods(models.Model):
    name = models.CharField(max_length=50) 
    
    def __str__(self):
        return self.name
    
class ScheduleSettings(models.Model):
    college = models.ForeignKey(College, on_delete=models.CASCADE)  # المستخدم المرتبط بالإعدادات
    days = models.ManyToManyField(Days)  # الأيام المختارة
    periods = models.ManyToManyField(Periods)  # الفترات المختارة
     
    def __str__(self):
        return f"Settings for {self.college.name}"
 