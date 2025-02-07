from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from .forms import CollegeForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import openpyxl
import pandas as pd
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from bidi.algorithm import get_display
import arabic_reshaper
import os
from django.conf import settings
from django.http import HttpResponse
from .models import Department, Lecturer, Room, Course,  Semester, College, Term, Days, Periods, ScheduleSettings
import time
import random
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
# Create your views here.
from django.contrib.auth.models import User



def Login_view(request):
    username= None
    password = None
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.warning(request, 'اسم المستخدم أو كلمة المرور غير صحيحة')
    return render(request, 'login.html')



@login_required(login_url='Login_view')
def term(request):
    if not request.user.is_superuser:  # تأكد أن المستخدم هو مشرف
        return render(request, 'error.html', {'message': 'ليس لديك الصلاحية للوصول لهذه الصفحة .'})
    
    terms = Term.objects.all().order_by('-created_at')  # جلب جميع الفصول
    
    if request.method == 'POST':
        if 'add_term' in request.POST:
            term_name = request.POST.get('term_name')  
            if term_name:
                Term.objects.create(name=term_name)
            return redirect('term')  # إعادة التوجيه بعد الإضافة
        elif 'delete_term' in request.POST:
            term_id = request.POST.get('term_id')
            term = get_object_or_404(Term, id=term_id)
            term.delete()
            return redirect('term')  # إعادة التوجيه بعد الحذف
    
    # التأكد من إعادة استجابة في حالة الطلب GET
    return render(request, 'term.html', {
        'term': terms,
    })
    
      
        
    

@login_required(login_url='Login_view')
def manage_colleges(request):
    if not request.user.is_superuser:  # تأكد أن المستخدم هو مشرف
        return render(request, 'error.html', {'message': 'ليس لديك الصلاحية للوصول لهذه الصفحة.'})
    
    colleges = College.objects.all()  # جلب جميع الكليات

    if request.method == 'POST':
        if 'add_college' in request.POST:
            # إضافة كلية جديدة مع المستخدم
            college_name = request.POST.get('college_name')  # الحصول على اسم الكلية
            user_id = request.POST.get('user_id')  # الحصول على id المستخدم
            user = User.objects.get(id=user_id)  # العثور على المستخدم بناءً على id
            logo = request.FILES.get('logo')  # الحصول على الشعار من الطلب
            
            if college_name and user:
                College.objects.create(name=college_name, user=user, logo=logo)  # ربط الكلية بالمستخدم والشعار
            return redirect('manage_colleges')
        
        elif 'delete_college' in request.POST:
            # حذف كلية
            college_id = request.POST.get('college_id')
            college = get_object_or_404(College, id=college_id)
            college.delete()
            return redirect('manage_colleges')

    # الحصول على قائمة المستخدمين لاختيار المستخدم المرتبط بالكلية
    users = User.objects.all()

    return render(request, 'manage_colleges.html', {
        'colleges': colleges,
        'users': users,  # تمرير قائمة المستخدمين
    })




@login_required(login_url='Login_view')
def edit_college(request, college_id):
    college = get_object_or_404(College, id=college_id)

    if not request.user.is_superuser:  # تأكد أن المستخدم هو مشرف
        return render(request, 'error.html', {'message': 'ليس لديك الصلاحية للوصول لهذه الصفحة.'})

    if request.method == 'POST':
        # تحديث الكلية
        college.name = request.POST.get('college_name')  # تعديل الاسم
        user_id = request.POST.get('user_id')  # تعديل المستخدم
        college.user = User.objects.get(id=user_id)  # تحديث الحساب المرتبط
        logo = request.FILES.get('logo')  # الحصول على الشعار
        if logo:
            college.logo = logo  # تحديث الشعار إذا تم رفعه
        college.save()  # حفظ التعديلات
        return redirect('manage_colleges')  # العودة لصفحة إدارة الكليات

    # عرض نموذج التعديل
    users = User.objects.all()  # للحصول على المستخدمين لاختيار الحساب المرتبط
    return render(request, 'edit_college.html', {
        'college': college,
        'users': users,
    })

    

@login_required(login_url='Login_view')
def manage_users(request):
    if not request.user.is_superuser:  # تأكد أن المستخدم هو مشرف
        return render(request, 'error.html', {'message': 'ليس لديك الصلاحية للوصول لهذه الصفحة .'})

    users = User.objects.all()

    return render(request, 'manage_users.html', {'users': users})




@login_required(login_url='Login_view')
def add_user(request):
    if not request.user.is_superuser:
        return render(request, 'error.html', {'message': 'ليس من صلاحياتك'})

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        is_superuser = request.POST.get('is_superuser', False)

        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password),
            is_superuser=is_superuser,
        )
        messages.success(request, 'User added successfully.')
        return redirect('manage_users')

    return render(request, 'add_user.html')



@login_required(login_url='Login_view')
def edit_user(request, user_id):
    if not request.user.is_superuser:
        return render(request, 'error.html', {'message': 'ليس من صلاحياتك'})

    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        user.username = request.POST['username']
        user.email = request.POST['email']
        user.is_superuser = 'is_superuser' in request.POST
        user.save()
        messages.success(request, 'User updated successfully.')
        return redirect('manage_users')

    return render(request, 'edit_user.html', {'user': user})



@login_required(login_url='Login_view')
def delete_user(request, user_id):
    if not request.user.is_superuser:
        return render(request, 'error.html', {'message': 'ليس من صلاحياتك'})

    user = User.objects.get(id=user_id)
    user.delete()
    messages.success(request, 'User deleted successfully.')
    return redirect('manage_users')




@login_required(login_url='Login_view')
def home(request):
    user_college = None
    if request.user.is_superuser:
        rooms_count = Room.objects.all().count()
        lecturers_count = Lecturer.objects.all().count()
        departments_count = Department.objects.all().count()
        courses_count = Course.objects.all().count()
    else:
        user_college = get_object_or_404(College, user=request.user)
        rooms_count = Room.objects.filter(college=user_college).count()
        lecturers_count = Lecturer.objects.filter(college=user_college).count()
        departments_count = Department.objects.filter(college=user_college).count()
        courses_count = Course.objects.filter(college=user_college).count()

    context = {
        'rooms_count': rooms_count,
        'lecturers_count': lecturers_count,
        'departments_count': departments_count,
        'courses_count': courses_count,
        'user_college': user_college
    }
    return render(request, 'home.html', context)



@login_required(login_url='Login_view')
def add_lecturer(request):
    # الحصول على الكلية المرتبطة بالمستخدم الحالي
    user_college = get_object_or_404(College, user=request.user)

    if request.method == 'POST':
        name = request.POST.get('name')
        number = request.POST.get('number')

        # التحقق من وجود البيانات
        if name and number:
            # ربط المحاضر بالكلية الخاصة بالمستخدم
            Lecturer.objects.create(name=name, number=number, college=user_college)
            return redirect('add_lecturer')

    # عرض المحاضرين المرتبطين بالكلية الخاصة بالمستخدم
    lecturers = Lecturer.objects.filter(college=user_college).order_by('name')
    return render(request, 'add_lecturer.html', {'lecturers': lecturers})




@login_required(login_url='Login_view')
def delete_lecturer(request, lecturer_id):
    # الحصول على الكلية المرتبطة بالمستخدم الحالي
    user_college = get_object_or_404(College, user=request.user)

    # التحقق من أن المحاضر الذي سيتم حذفه مرتبط بالكلية الخاصة بالمستخدم
    lecturer = get_object_or_404(Lecturer, id=lecturer_id, college=user_college)
    lecturer.delete()
    return redirect('add_lecturer')



@login_required(login_url='Login_view')
def add_department(request):
    # الحصول على الكلية المرتبطة بالمستخدم الحالي
    user_college = get_object_or_404(College, user=request.user)

    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        semester_id = request.POST.get('semester')  # الحصول على الفصل الدراسي
        semester = Semester.objects.get(id=semester_id) if semester_id else None

        # التحقق من وجود البيانات
        if name and code:
            # ربط القسم بالكلية الخاصة بالمستخدم
            Department.objects.create(name=name, code=code, semester=semester, college=user_college)
            return redirect('add_department')

    # عرض الأقسام المرتبطة بالكلية الخاصة بالمستخدم
    departments = Department.objects.filter(college=user_college).order_by('name')
    semesters = Semester.objects.all()  # استدعاء جميع الفصول الدراسية
    return render(request, 'add_department.html', {'departments': departments, 'semesters': semesters})




@login_required(login_url='Login_view')
def delete_department(request, department_id):
     # الحصول على الكلية المرتبطة بالمستخدم الحالي
    user_college = get_object_or_404(College, user=request.user)

    department = get_object_or_404(Department, id=department_id, college=user_college)
    department.delete()
    return redirect('add_department')




@login_required(login_url='Login_view')
def add_room(request):
    # الحصول على الكلية المرتبطة بالمستخدم الحالي
    user_college = get_object_or_404(College, user=request.user)

    if request.method == 'POST':
        name = request.POST.get('name')
        capacity = request.POST.get('capacity')
        room_type = request.POST.get('room_type')

        # التحقق من وجود البيانات
        if name and capacity and room_type:
            # ربط الغرفة بالكلية الخاصة بالمستخدم
            Room.objects.create(name=name, capacity=capacity, room_type=room_type, college=user_college)

        return redirect('add_room')

    # عرض الغرف المرتبطة بالكلية الخاصة بالمستخدم
    rooms = Room.objects.filter(college=user_college).order_by('name')

    return render(request, 'add_room.html', {'rooms': rooms})



@login_required(login_url='Login_view')
def delete_room(request, room_id):
    user_college = get_object_or_404(College, user=request.user)

    room = get_object_or_404(Room, id=room_id, college=user_college)
    room.delete()
    return redirect('add_room')



@login_required(login_url='Login_view')
def add_course(request):
    # الحصول على الكلية المرتبطة بالمستخدم الحالي
    user_college = get_object_or_404(College, user=request.user)

    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        student_count = request.POST.get('student_count')
        departments = request.POST.getlist('departments')  # الأقسام
        lecturers = request.POST.get('lecturer')  # المحاضر
        required_room_type = request.POST.get('required_room_type')  # نوع الغرفة المطلوبة

        # إنشاء الكورس وربطه بالكلية الخاصة بالمستخدم
        course = Course(
            name=name,
            code=code,
            student_count=student_count,
            lecturer=Lecturer.objects.get(id=lecturers),
            required_room_type=required_room_type,  # نوع الغرفة
            college=user_college
        )
        course.save()  # حفظ المقرر

        # تعيين الأقسام للمقرر
        if departments:
            course.department.set(Department.objects.filter(id__in=departments))

        return redirect('add_course')

    # عرض البيانات اللازمة للنموذج
    courses = Course.objects.filter(college=user_college).order_by('name')
    departments = Department.objects.filter(college=user_college)
    lecturers = Lecturer.objects.filter(college=user_college)

    return render(request, 'add_course.html', {
        'courses': courses,
        'departments': departments,
        'lecturers': lecturers,
    })



@login_required(login_url='Login_view')
def edit_course(request, course_id):
    # الحصول على الكلية المرتبطة بالمستخدم الحالي
    user_college = get_object_or_404(College, user=request.user)

    # جلب المقرر المطلوب تعديله
    course = get_object_or_404(Course, id=course_id, college=user_college)

    if request.method == 'POST':
        # تحديث بيانات المقرر
        course.name = request.POST.get('name')
        course.code = request.POST.get('code')
        course.student_count = request.POST.get('student_count')
        course.required_room_type = request.POST.get('required_room_type')
        course.lecturer = Lecturer.objects.get(id=request.POST.get('lecturer'))

        # تحديث الأقسام المرتبطة بالمقرر
        departments = request.POST.getlist('departments')
        if departments:
            course.department.set(Department.objects.filter(id__in=departments))

        course.save()  # حفظ التعديلات
        return redirect('add_course')  # إعادة التوجيه إلى صفحة المقررات

    # عرض بيانات المقرر في النموذج
    departments = Department.objects.filter(college=user_college)
    lecturers = Lecturer.objects.filter(college=user_college)

    return render(request, 'edit_course.html', {
        'course': course,
        'departments': departments,
        'lecturers': lecturers,
    })




@login_required(login_url='Login_view')
def delete_course(request, course_id):
    user_college = get_object_or_404(College, user=request.user)

    course = get_object_or_404(Course, id=course_id, college=user_college)
    course.delete()
    return redirect('add_course') 






@login_required(login_url='Login_view')
def choose(request):
    user_college = College.objects.get(user=request.user)  # الكلية المرتبطة بالمستخدم
    days = Days.objects.all()
    periods = Periods.objects.all()

    if request.method == 'POST':
        selected_days = request.POST.getlist('days')
        selected_periods = request.POST.getlist('periods')

        # إنشاء إعدادات الجدول أو تحديثها
        schedule_settings, created = ScheduleSettings.objects.get_or_create(college=user_college)
        schedule_settings.days.set(selected_days)
        schedule_settings.periods.set(selected_periods)
        schedule_settings.save()

        return redirect('home')  # إعادة التوجيه بعد الحفظ

    return render(request, 'choose.html', {'days': days, 'periods': periods})




@login_required(login_url='Login_view')
def generate_schedule(request):
    # الحصول على الكلية المرتبطة بالمستخدم الحالي
    user_college = get_object_or_404(College, user=request.user)
    
    # جلب البيانات المرتبطة بالكلية الخاصة بالمستخدم
    rooms = Room.objects.filter(college=user_college) or []
    courses = Course.objects.filter(college=user_college) or []
    unscheduled_courses = []  # قائمة للمقررات غير المجدولة
    memory_size = 10  # حجم الذاكرة في خوارزمية هيرمان
    memory = []  # تخزين أفضل الحلول السابقة
    max_iterations = 20  # عدد التكرارات
    start_time = time.time()  # بدء حساب الوقت
    
    # القيم الافتراضية للأيام والفترات
    DEFAULT_DAYS = ['السبت', 'الأحد', 'الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس']
    DEFAULT_PERIODS = ['8:10', '10:12', '12:2', '2:4']

    # جلب إعدادات الجدول الخاصة بالكلية
    schedule_settings = ScheduleSettings.objects.filter(college=user_college).first()
    DAYS = [day.name for day in schedule_settings.days.all()] if schedule_settings and schedule_settings.days.exists() else DEFAULT_DAYS
    PERIODS = [period.name for period in schedule_settings.periods.all()] if schedule_settings and schedule_settings.periods.exists() else DEFAULT_PERIODS



    def sort_courses_by_department_overlap(courses):
        sorted_courses = sorted(courses, key=lambda course: len(course.department.all()), reverse=True)
        return sorted_courses
    
    
    
    # إعداد هيكل الجدول
    def initialize_schedule():
        schedule = {}
        for day in DAYS:
            schedule[day] = {}
            for period in PERIODS:
                schedule[day][period] = []  # قائمة فارغة لكل فترة
        return schedule

    
    # تقييم الجدول بناءً على التعارضات
    def evaluate_schedule(schedule):
        score = 0
        max_possible_score = 0  # الحد الأقصى للنقاط المحتملة

        for day in DAYS:
            for period in PERIODS:
                details = schedule.get(day, {}).get(period, [])
                num_details = len(details)

                # كل تعارض محتمل يضيف إلى الحد الأقصى
                max_possible_score += (num_details * (num_details - 1)) * 12  # تعارض القاعات
                max_possible_score += (num_details * (num_details - 1)) * 80  # تعارض المحاضرين
                max_possible_score += (num_details * (num_details - 1)) * 20  # تعارض المحاضرين
                max_possible_score += (num_details) * 50  # تعارض نوع الغرفة
                for i, detail1 in enumerate(details):
                    for detail2 in details[i + 1:]:
                        # تعارض القاعات
                        if detail1["room"] == detail2["room"]:
                            score += 12
                        # تعارض المحاضرين
                        if detail1["lecturer"] == detail2["lecturer"]:
                            score += 80
                            
                        # التحقق من تطابق نوع الغرفة مع نوع الغرفة المطلوبة للمقرر
                        if detail1["room"].room_type != detail1["course"].required_room_type:
                            score += 50  # تعارض بسبب نوع الغرفة (وزن 50 كنموذج)


                        # الحصول على أسماء الأقسام للمقررات
                        course1_departments = {dep.name for dep in detail1["course"].department.all()}
                        course2_departments = {dep.name for dep in detail2["course"].department.all()}

                        # التأكد من أن المقررات من نفس القسم قبل مقارنة السمستر
                        if not course1_departments & course2_departments:
                            continue  # إذا كانت المقررات لا تنتمي لنفس القسم، نتخطى المقارنة

                        # تعارض الفصول الدراسية
                        for dep1 in course1_departments:
                            for dep2 in course2_departments:
                                semester1 = next(dep.semester.semester_number for dep in detail1["course"].department.all() if dep.name == dep1)
                                semester2 = next(dep.semester.semester_number for dep in detail2["course"].department.all() if dep.name == dep2)
                                if abs(semester1 - semester2) <= 1:  # تعارض في نفس السمستر أو سمسترات متجاورة
                                    score += 20

        # حساب نسبة الدقة
        accuracy = (1 - score / max_possible_score) * 100 if max_possible_score > 0 else 100
        return score, accuracy



    def generate_initial_solution():
        schedule = initialize_schedule()  # افتراض وجود دالة initialize_schedule لتحضير الجدول
        sorted_courses = sort_courses_by_department_overlap(courses)  # ترتيب المقررات حسب التداخل بين الأقسام

        for course in sorted_courses:
            assigned = False
            for _ in range(11111):  # المحاولة 777 مرة لإيجاد فترة مناسبة
                day = random.choice(DAYS)
                period = random.choice(PERIODS)

                # البحث عن قاعة مناسبة للمقرر
                suitable_room = next(
                (room for room in rooms if 
                 room.capacity >= (course.student_count * 0.8) and  # التحقق من السعة
                 room.room_type == course.required_room_type and        # التحقق من نوع الغرفة
                 all(detail["room"] != room for detail in schedule[day][period])  # التحقق من عدم التعارض
                ),
                None
            )

                if suitable_room:
                    # التحقق من عدم وجود تعارض في الأقسام والسمسترات
                    conflicting = False
                    for detail in schedule[day][period]:
                        # الحصول على أسماء الأقسام للمقررات
                        course1_departments = {dep.name for dep in detail["course"].department.all()}
                        course2_departments = {dep.name for dep in course.department.all()}

                        # التأكد من أن المقررات من نفس القسم قبل مقارنة السمستر
                        if not course1_departments & course2_departments:
                            continue  # إذا كانت المقررات لا تنتمي لنفس القسم، نتخطى المقارنة

                        # مقارنة السمسترات فقط إذا كانت المقررات في نفس القسم
                        for dep1 in course1_departments:
                            for dep2 in course2_departments:
                                # الحصول على السمستر من خلال القسم
                                semester1 = next(dep.semester.semester_number for dep in detail["course"].department.all() if dep.name == dep1)
                                semester2 = next(dep.semester.semester_number for dep in course.department.all() if dep.name == dep2)
                                
                                # التأكد من أن السمسترات ليست متشابهة أو متجاورة
                                if semester1 == semester2 or abs(semester1 - semester2) == 1:
                                    conflicting = True
                                    break
                            if conflicting:
                                break

                    if not conflicting:
                        # إضافة المقرر إلى الجدول
                        schedule[day][period].append({
                            "course": course,
                            "lecturer": course.lecturer,
                            "room": suitable_room,
                        })
                        assigned = True
                        break

            
        return schedule




    
    # دالة تحسين الجدول مع تجنب تعارضات المقررات والفترات
    def optimize_schedule(schedule):
        for _ in range(100):  # عدد محاولات التحسين لكل جدول
            day1, day2 = random.sample(DAYS, 2)
            period1, period2 = random.sample(PERIODS, 2)

            if schedule[day1][period1] and schedule[day2][period2]:
                lecturers1 = [detail["lecturer"] for detail in schedule[day1][period1]]
                lecturers2 = [detail["lecturer"] for detail in schedule[day2][period2]]
                rooms1 = [detail["room"] for detail in schedule[day1][period1]]
                rooms2 = [detail["room"] for detail in schedule[day2][period2]]

                # التأكد من أن المقررات في نفس القسم
                departments1 = [", ".join([dep.name for dep in detail["course"].department.all()]) for detail in schedule[day1][period1]]
                departments2 = [", ".join([dep.name for dep in detail["course"].department.all()]) for detail in schedule[day2][period2]]

                # التأكد من أن المقررات تنتمي إلى نفس القسم قبل مقارنة السمستر
                conflicting_courses = False
                for detail1 in schedule[day1][period1]:
                    for detail2 in schedule[day2][period2]:
                        department1 = ", ".join([dep.name for dep in detail1["course"].department.all()])
                        department2 = ", ".join([dep.name for dep in detail2["course"].department.all()])

                        # التأكد من أن الأقسام متطابقة
                        if department1 != department2:
                            continue  # إذا كانت الأقسام مختلفة نتجاهل المقارنة

                        # إذا كانت الأقسام متطابقة نواصل مقارنة السمستر
                        semester1 = detail1["course"].department.first().semester.semester_number
                        semester2 = detail2["course"].department.first().semester.semester_number

                        # التأكد من أن المقررات في سمسترات بعيدة أو متجاورة
                        if semester1 == semester2:  # نفس السمستر
                            conflicting_courses = True
                            break
                        elif abs(semester1 - semester2) == 1:  # سمسترات متجاورة
                            conflicting_courses = True
                            break
                    if conflicting_courses:
                        break

                if not conflicting_courses:
                    # التأكد من عدم تعارض القاعات والمحاضرين
                    if not (set(lecturers1) & set(lecturers2)) and not (set(rooms1) & set(rooms2)):
                        # تبديل الجدول بين الفترتين
                        schedule[day1][period1], schedule[day2][period2] = schedule[day2][period2], schedule[day1][period1]

        return schedule
    
    
    

    # تنفيذ خوارزمية هيرمان
    
    initial_solutions = [generate_initial_solution() for _ in range(10)]
    evaluated_solutions = [(solution, evaluate_schedule(solution)) for solution in initial_solutions]

    # إضافة جميع الحلول الأولية إلى الذاكرة
    memory = evaluated_solutions.copy()

    current_solution = min(memory, key=lambda x: x[1][0])[0]
    
    for iteration in range(max_iterations):
        # إنشاء جداول جديدة وتحسينها
        new_solution = optimize_schedule(current_solution)
        new_score = evaluate_schedule(new_solution)

        # تحديث أفضل الحلول في الذاكرة
        if len(memory) < memory_size:
            memory.append((new_solution, new_score))
        else:
            worst_solution = max(memory, key=lambda x: x[1])
            if new_score <= worst_solution[1]:
                memory.remove(worst_solution)
                memory.append((new_solution, new_score))

        #  # اختيار أفضل جدول من الذاكرة للحل التالي
        current_solution = min(memory, key=lambda x: x[1])[0]
        
    # استخراج أفضل جدول من الذاكرة
    best_schedule = min(memory, key=lambda x: x[1])[0]
    # استخراج الدقة أيضًا
    Score, Accuracy = evaluate_schedule(best_schedule)

    # استخراج الجداول والدقة من الذاكرة
    top_5_schedules_with_accuracy = sorted(memory, key=lambda x: x[1][1], reverse=True)[:5]
    all_schedules_with_accuracy = [(solution[0], solution[1][1]) for solution in top_5_schedules_with_accuracy]  # [0] للجدول و [1] للنسبة المئوية

    unscheduled_courses = [course for course in courses if not any(
        course == detail["course"] for day in DAYS for period in PERIODS for detail in best_schedule[day][period]
    )]

    # حساب الوقت المستغرق
    end_time = time.time()
    elapsed_time = end_time - start_time
    score, accuracy = evaluate_schedule(best_schedule)
    
    print(f"Score: {score}")
    print(f"Accuracy: {accuracy:.2f}%")
    
    print(f"Time of the algorithm: {elapsed_time} seconds")
    
    def convert_to_serializable(schedule):
        serializable_schedule = {}
        for day, periods in schedule.items():
            serializable_schedule[day] = {}
            for period, details in periods.items():
                if details:
                    serializable_schedule[day][period] = [
                        {
                            "course": {"code": detail["course"].code, "name": detail["course"].name},
                            "lecturer": {"name": detail["lecturer"].name},
                            "room": {"name": detail["room"].name},
                        }
                        for detail in details
                    ]
                else:
                    serializable_schedule[day][period] = []
        return serializable_schedule

    
    
    

    # أثناء تخزين البيانات في الجلسة
    serializable_schedules_with_accuracy = [
        (convert_to_serializable(schedule), accuracy) for schedule, accuracy in all_schedules_with_accuracy
    ]
    request.session["schedules_with_accuracy"] = serializable_schedules_with_accuracy
    
    def convert_best_schedule_to_serializable(best_schedule):
        """
        دالة لتحويل أفضل جدول إلى تنسيق يمكن تسلسله
        """
        serializable_schedule = {}
        
        # التكرار عبر الأيام والفترات
        for day, periods in best_schedule.items():
            serializable_schedule[day] = {}
            for period, details in periods.items():
                if details:
                    # إذا كانت هناك محاضرات في الفترة المحددة
                    serializable_schedule[day][period] = [
                        {
                            "course": {"code": detail["course"].code, "name": detail["course"].name},
                            "lecturer": {"name": detail["lecturer"].name},
                            "room": {"name": detail["room"].name},
                        }
                        for detail in details
                    ]
                else:
                    # إذا كانت الفترة فارغة
                    serializable_schedule[day][period] = []
        
        return serializable_schedule

        
        # تحويل أفضل جدول إلى تنسيق قابل للتسلسل
    best_schedule_serializable = convert_best_schedule_to_serializable(best_schedule)

    # تخزين الجدول في الجلسة
    request.session['best_schedule'] = best_schedule_serializable

    # إرسال الجدول النهائي إلى HTML
    return render(request, 'create_schedule.html', {
        'schedules_with_accuracy':all_schedules_with_accuracy ,
        'unscheduled_courses': unscheduled_courses,
        'schedule': best_schedule,
        'accuracy': accuracy,
        'periods': PERIODS
    })






def export_schedule_to_excel(request):
    # إنشاء ملف Excel جديد
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "جدول المحاضرات"

    # إضافة عنوان الأعمدة
    headers = ["اليوم", "8-10", "10-12", "12-2", "2-4"]
    sheet.append(headers)

    # جلب البيانات من الجداول (مثال توضيحي)
    schedules_with_accuracy = request.session.get("schedules_with_accuracy", [])
    for schedule, accuracy in schedules_with_accuracy:
        sheet.append([f"دقة الجدول: {accuracy}%"])
        for day, periods in schedule.items():
            row = [day]
            for period, details in periods.items():
                if details:
                    cell_content = "\n".join(
                        f"{detail['course'].get('code', '')} - {detail['lecturer'].get('name', '')} - {detail['room'].get('name', '')}"
                        for detail in details
                    )
                else:
                    cell_content = "فارغ"
                row.append(cell_content)
            sheet.append(row)

    # إعداد استجابة HttpResponse لتنزيل الملف
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="schedules.xlsx"'
    workbook.save(response)
    return response


# مسار الخط
font_path = os.path.join(settings.BASE_DIR, "static/fonts/Amiri-Regular.ttf")
pdfmetrics.registerFont(TTFont("Amiri", font_path))

def export_schedule_to_pdf(request):
    # إعداد استجابة HttpResponse لتنزيل الملف
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="best_schedule.pdf"'

    # إعداد ملف PDF مع الاتجاه الأفقي
    pdf = SimpleDocTemplate(response, pagesize=landscape(A4))  # استخدام A4 Landscape
    elements = []
    styles = getSampleStyleSheet()

    # إعداد نمط الفقرات مع الخط العربي
    arabic_style = ParagraphStyle(
        name="Arabic",
        fontName="Amiri",
        fontSize=10,  # يمكن تقليل حجم الخط إذا كانت النصوص طويلة
        alignment=1,  # محاذاة إلى المنتصف
        wordWrap='CJK',  # لتغطية النصوص الطويلة
    )
        
     # الحصول على الكلية المرتبطة بالمستخدم الحالي
    user_college = get_object_or_404(College, user=request.user)
    
    # يمكنك اختيار الفصل الدراسي (مثلاً، أحدث فصل أو فصل معين حسب الحاجة)
    current_term = Term.objects.last()  # هنا يمكنك استخدام أي منطق لجلب الفصل الدراسي الحالي
    

    if user_college.logo:
        logo_path = os.path.join(settings.MEDIA_ROOT, user_college.logo.name)  # استخدام المسار الفعلي
    else:
       logo_path = None  # إذا لم يكن هناك شعار
    try:
        logo = Image(logo_path, width=100, height=50)
        elements.append(logo)
        elements.append(Spacer(1, 5))  # مسافة بين الشعار والمحتوى
    except FileNotFoundError:
        elements.append(Paragraph("شعار الكلية غير متوفر", styles["Normal"]))


    # إضافة النص الذي يعكس الكلية والفصل الدراسي
    title_text = f"الجدول الدراسي ل{user_college.name} - {current_term.name}" if current_term else f"الجدول الدراسي لكلية {user_college.name}"

    reshaped_title = arabic_reshaper.reshape(title_text)
    bidi_title = get_display(reshaped_title)
    elements.append(Paragraph(bidi_title, arabic_style))
    elements.append(Spacer(1, 6))  # مسافة بين العنوان وبقية المحتوى

    # جلب الجدول الأفضل
    best_schedule = request.session.get("best_schedule")
    if not best_schedule:
        no_schedule_text = "لم يتم العثور على جدول."
        reshaped_text = arabic_reshaper.reshape(no_schedule_text)
        bidi_text = get_display(reshaped_text)
        elements.append(Paragraph(bidi_text, arabic_style))
    else:
        # إعداد الجدول
        headers = ["اليوم", "8-10", "10-12", "12-2", "2-4"]
        reshaped_headers = [get_display(arabic_reshaper.reshape(header)) for header in headers]
        data = [reshaped_headers]

        for day, periods in best_schedule.items():
            reshaped_day = get_display(arabic_reshaper.reshape(day))
            row = [reshaped_day]
            for period, details in periods.items():
                if details:
                    cell_content = "\n".join(
                        f"{detail['course'].get('code', '')} -- {detail['room'].get('name', '')}"
                        for detail in details
                    )
                    reshaped_content = get_display(arabic_reshaper.reshape(cell_content))
                else:
                    reshaped_content = get_display(arabic_reshaper.reshape("فارغ"))
                row.append(reshaped_content)
            data.append(row)

        # تعديل عرض الأعمدة لتناسب الوضع الأفقي
        col_widths = [150, 150, 150, 150, 150]  # زيادة عرض الأعمدة لتسع المحتوى بشكل أفضل

        # إضافة الجدول مع زيادة حجم الأعمدة
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, -1), "Amiri"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),  # لضبط المحاذاة عموديًا
            ("WORDSPACE", (0, 0), (-1, -1), 4),  # زيادة التباعد بين الكلمات في الخلايا
        ]))

        elements.append(table)

    # بناء الملف PDF
    pdf.build(elements)
    return response








@login_required(login_url='Login_view')
def generate_schedule_final(request):
    # الأيام والفترات الدراسية
    DAYS = ["السبت", "الاحد", "الاثنين", "الثلاثاء", "الاربعاء", "الخميس",
            " السبت - الاسبوع الثاني", "الاحد - الاسبوع الثاني", "الاثنين - الاسبوع الثاني", "الثلاثاء - الاسبوع الثاني", "الاربعاء - الاسبوع الثاني", "الخميس - الاسبوع الثاني",
            "السبت - الاسبوع الثالث", "الاحد - الاسبوع الثالث", "الاثنين - الاسبوع الثالث", "الثلاثاء - الاسبوع الثالث", "الاربعاء - الاسبوع الثالث", "الخميس - الاسبوع الثالث"]
    PERIODS = ["8:10", "10:12", "12:2", "2:4"]

    # الحصول على الكلية المرتبطة بالمستخدم الحالي
    user_college = get_object_or_404(College, user=request.user)

    # جلب البيانات المرتبطة بالكلية الخاصة بالمستخدم
    rooms = Room.objects.filter(college=user_college) or []
    courses = Course.objects.filter(college=user_college) or []
    unscheduled_courses = []  # قائمة للمقررات غير المجدولة
    # إعداد هيكل الجدول
    def initialize_schedule():
        schedule = {}
        for day in DAYS:
            schedule[day] = {}
            for period in PERIODS:
                schedule[day][period] = []  # قائمة فارغة لكل فترة
        return schedule

    # ترتيب المقررات حسب عدد الأقسام المشتركة
    def sort_courses_by_priority(courses):
        return sorted(
            courses,
            key=lambda course: (
                len(course.department.all()),  # عدد الأقسام المرتبطة بالمقرر
                -course.student_count           # عدد الطلاب (ترتيب عكسي ليتم جدولة الأكبر أولاً عند التساوي)
            ),
            reverse=True
        )

    # التحقق من إمكانية تخصيص غرفة للمقرر
    def is_room_suitable(room, course, schedule, day, period):
        if room.capacity < course.student_count or room.room_type != course.required_room_type:
            return False
        for detail in schedule[day][period]:
            if detail["room"] == room:
                return False
        return True

        # التحقق من تعارض الأقسام والفصول في نفس اليوم
    def has_department_conflict(schedule, course, day):
        # الحصول على الأقسام والفصول الخاصة بالمقرر الجديد
        course_departments = {dep.name for dep in course.department.all()}
        course_semesters = {dep.semester.semester_number for dep in course.department.all()}

        # جمع جميع المقررات المجدولة في نفس اليوم بجميع فتراته
        scheduled_courses_in_day = [
            detail["course"]
            for period in PERIODS
            for detail in schedule[day][period]
        ]

        # التحقق من تعارض الأقسام والفصول بين المقرر الجديد والمقررات المجدولة
        for scheduled_course in scheduled_courses_in_day:
            scheduled_departments = {dep.name for dep in scheduled_course.department.all()}
            scheduled_semesters = {dep.semester.semester_number for dep in scheduled_course.department.all()}

            # تحقق من تداخل الأقسام
            if course_departments & scheduled_departments:
                # تحقق من تداخل الفصول
                if not course_semesters.isdisjoint(scheduled_semesters) or any(
                    abs(s1 - s2) == 1 for s1 in course_semesters for s2 in scheduled_semesters
                ):
                    return True  # يوجد تعارض

        return False  # لا يوجد تعارض

    
    # إنشاء الحل الأولي
    def generate_initial_solution():
        schedule = initialize_schedule()
        sorted_courses = sort_courses_by_priority(courses)  # ترتيب المقررات حسب الأولوية
        for course in sorted_courses:
            assigned = False
            for _ in range(1000):
                day = random.choice(DAYS)
                period = random.choice(PERIODS)
                suitable_room = next(
                    (room for room in rooms if is_room_suitable(room, course, schedule, day, period)),
                    None
                )
                if suitable_room and not has_department_conflict(schedule, course, day):
                    schedule[day][period].append({
                        "course": course,
                        "room": suitable_room,
                    })
                    assigned = True
                    break
            if not assigned:
                unscheduled_courses.append(course)
        return schedule

    # تقييم الجدول
    def evaluate_schedule(schedule):
        score = 0
        for day in DAYS:
            for period in PERIODS:
                details = schedule[day][period]
                for i in range(len(details)):
                    for j in range(i + 1, len(details)):
                        if details[i]["room"] == details[j]["room"]:
                            score += 50
            day_courses = [detail["course"] for period in PERIODS for detail in schedule[day][period]]
            for i in range(len(day_courses)):
                for j in range(i + 1, len(day_courses)):
                    course1 = day_courses[i]
                    course2 = day_courses[j]
                    course1_departments = {dep.name for dep in course1.department.all()}
                    course2_departments = {dep.name for dep in course2.department.all()}
                    course1_semesters = {dep.semester.semester_number for dep in course1.department.all()}
                    course2_semesters = {dep.semester.semester_number for dep in course2.department.all()}

                    if course1_departments & course2_departments:
                        if not course1_semesters.isdisjoint(course2_semesters) or any(
                            abs(s1 - s2) == 1 for s1 in course1_semesters for s2 in course2_semesters
                        ):
                            score += 1
        return score


    current_solution = generate_initial_solution()
  
    best_schedule = current_solution
    # استخراج الدقة أيضًا
    score = evaluate_schedule(best_schedule)

    # تحويل الجدول إلى تنسيق قابل للعرض
    def convert_to_serializable(schedule):
        serializable_schedule = {}
        for day, periods in schedule.items():
            serializable_schedule[day] = {}
            for period, details in periods.items():
                if details:
                    serializable_schedule[day][period] = [
                        {
                            "course": {"code": detail["course"].code, "name": detail["course"].name},
                            "room": {"name": detail["room"].name},
                        }
                        for detail in details
                    ]
                else:
                    serializable_schedule[day][period] = []
        return serializable_schedule

    serializable_schedule = convert_to_serializable(best_schedule)

    return render(request, 'create_schedule_final.html', {
        'schedule': serializable_schedule,
        'unscheduled_courses': unscheduled_courses,
        'score': score,
    })
