from django.db import models
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin,BaseUserManager
from django.db.models import Max
from django.contrib.auth.hashers import make_password
# Create your models here.


class CustomUserManager(BaseUserManager):
    def create_user(self,email,name,password=None,**extra_fields):
        if not email:
            raise ValueError("The email field must be set")
        email=self.normalize_email(email)
        user=self.model(email=email,name=name,**extra_fields)
        if password:
            user.set_password(password)
        else:
            raise ValueError("Password is required")
        user.save(using=self._db)
        return user
    def create_superuser(self,email,name,password=None,**extra_fields):
        extra_fields.setdefault("is_staff",True)
        extra_fields.setdefault("is_superuser",True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        
        return self.create_user(email,name,password, **extra_fields)
    

class CustomUser(AbstractBaseUser,PermissionsMixin):
    name=models.CharField(max_length=200)
    email=models.EmailField(unique=True)
    is_active=models.BooleanField(default=True)
    is_staff=models.BooleanField(default=False)
    is_superuser=models.BooleanField(default=False)
    is_company=models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['']

    def has_perm(self, perm, obj=None): 
        return self.is_superuser
    
    def has_module_perms(self, app_label):
        return self.is_superuser
    
    def __str__(self):
        return self.email
    

class Department(models.Model):
    name = models.CharField(max_length=100)
    hod_name = models.CharField(max_length=100,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name


class Course(models.Model):
    name= models.CharField(max_length=100)
    department = models.ForeignKey(Department,on_delete=models.CASCADE, related_name="course_department")

class Student(CustomUser):
    std_id=models.CharField(unique=True,max_length=50)
    img=models.FileField(upload_to='media/student_image',null=True,blank=True)
    options=( 
        ("Male","Male"),
        ("Female","Female"),
        ("Others","Others")
    )
    gender=models.CharField(max_length=100,choices=options,default="Male")
    dob=models.DateField(null=True)
    department=models.ForeignKey(Department,on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.std_id:  
            last_std_id = Student.objects.aggregate(max_id=Max('std_id'))['max_id']
            if last_std_id:
                new_id = int(last_std_id[3:]) + 1
            else:
                new_id = 1
            self.std_id = f"CLI{new_id:04d}"  
        if self.pk is None or not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.std_id 
    

class Company(CustomUser):
    industry = models.CharField(max_length=255)
    about =  models.TextField()
    logo = models.FileField(upload_to="media/Company-Logo")
    location = models.CharField(max_length=200)
    phone = models.PositiveBigIntegerField()
    site_url = models.URLField(null=True)
    options = (
        ('Approved','Approved'),
        ('Revoked','Revoked'),
        ('Pending','Pending')
    )
    status = models.CharField(max_length=100,choices=options,default="Pending",null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)  
    
    def save(self, *args, **kwargs):
        if self.pk is None or not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class JobPosts(models.Model):
    company =  models.ForeignKey(Company,on_delete=models.CASCADE,related_name="company_jobs",null=True)
    skills = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    vacancy = models.IntegerField()
    location = models.CharField(max_length=100)
    department = models.ForeignKey('Department', on_delete=models.CASCADE)
    salary = models.CharField(max_length=300,null=True)
    opening_date = models.DateField(auto_now_add=True)
    closing_date = models.DateField(null=True, blank=True)  # Make closing date optional if needed
    created_at = models.DateTimeField(auto_now_add=True,null=True)

    def __str__(self):
        return f"{self.designation} "
    

class AppliedStudents(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE,related_name='applied_st')
    jobpost = models.ForeignKey(JobPosts,on_delete=models.CASCADE,related_name='job_stuu')
    cv = models.FileField(upload_to="media/cv",null=True)
    options = (
        ("Pass","Pass"),
        ("Fail","Fail"),
        ("Pending","Pending")
    )
    intial_round1 = models.CharField(max_length=100,choices=options, default="Pending")
    tech_round2 = models.CharField(max_length=100,choices=options, default="Pending")
    is_passed =  models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True,null=True)


class TechInterview(models.Model):
    applied = models.ForeignKey(AppliedStudents,on_delete=models.CASCADE,related_name='tech_applied')
    link  = models.URLField(null=True)
    start_time = models.DateTimeField(null=True)
    status = models.CharField(max_length=200,null=True)
    

class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    link = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    
class Subject(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Question(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard')
    ]

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    text = models.TextField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    
    def __str__(self):
        return self.text[:50]

class Option(models.Model):
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    text = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text[:50]

class MockTest(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    total_questions = models.IntegerField(default=15)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.subject.name} Mock Test"

class MockTestResponse(models.Model):
    mock_test = models.ForeignKey(MockTest, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(Option, null=True, blank=True, on_delete=models.SET_NULL)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.mock_test} - {self.question}"

from django.utils import timezone
    
class AssessmentSession(models.Model):
    """Model to track an individual assessment session"""
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    total_questions = models.IntegerField()
    current_question = models.TextField(blank=True, null=True)
    current_model_answer = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.student.name}'s Assessment on {self.created_at}"

class StudentAnswer(models.Model):
    """Model to store individual student answers with optional video"""
    session = models.ForeignKey('AssessmentSession', on_delete=models.CASCADE)
    question = models.TextField()
    student_answer = models.TextField()
    model_answer = models.TextField()
    marks = models.FloatField()
    feedback = models.TextField()
    answered_at = models.DateTimeField(default=timezone.now)
    
    # Optional video file storage
    video_file = models.FileField(
        upload_to='assessment_videos/', 
        null=True, 
        blank=True
    )

    def __str__(self):
        return f"Answer for {self.question[:50]}"
    
from django.conf import settings
    
class ResetToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    def __str__(self):
        return f"Reset token for {self.user.email}"