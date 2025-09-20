from django.contrib import admin
from django.db.models import Count
from django import forms
from django.core.exceptions import ValidationError

from .models import Student, Instructor, Course, Enrollment


class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = '__all__'

    def clean(self):
        cleaned = super().clean()
        student = cleaned.get('student')
        course = cleaned.get('course')
        if student and course:
            qs = Enrollment.objects.filter(student=student, course=course)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError("This student is already enrolled in this course.")
        return cleaned


class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    form = EnrollmentForm
    extra = 1
    autocomplete_fields = ['student']  # search students when many exist


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'instructor', 'enrolled_count')
    search_fields = ('code', 'title')
    list_select_related = ('instructor',)
    inlines = [EnrollmentInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(_enrolled_count=Count('enrollments'))

    @admin.display(ordering='_enrolled_count', description='Enrolled students')
    def enrolled_count(self, obj):
        return obj._enrolled_count


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'department', 'enrollment_date')
    search_fields = ('name', 'email')
    list_filter = ('department',)


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'department', 'hire_date', 'course_count')
    search_fields = ('name', 'email')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(_course_count=Count('courses'))

    @admin.display(ordering='_course_count', description='Number of courses')
    def course_count(self, obj):
        return obj._course_count


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    form = EnrollmentForm
    list_display = ('student', 'course', 'enrollment_date', 'grade')
    search_fields = ('student__name', 'student__email', 'course__code', 'course__title')
    list_filter = ('course',)