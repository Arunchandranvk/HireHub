from  django import forms 
from .models import  *


class LogForm(forms.Form):
    email=forms.EmailField(widget=forms.EmailInput(attrs={"placeholder":"Email","class":"form-control","style":"border-radius: 0.75rem; "}))
    password=forms.CharField(widget=forms.PasswordInput(attrs={"placeholder":"Password","class":"form-control","style":"border-radius: 0.75rem; "}))


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        exclude = ['std_id']

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = '__all__'

    
import re

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = '__all__'
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name and len(name) < 2:
            raise forms.ValidationError("Name must be at least 2 characters long.")
        return name
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Check if email already exists
        if Company.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            # Validate password strength
            if len(password) < 8:
                raise forms.ValidationError("Password must be at least 8 characters long.")
            if not re.search(r'[A-Z]', password):
                raise forms.ValidationError("Password must contain at least one uppercase letter.")
            if not re.search(r'[a-z]', password):
                raise forms.ValidationError("Password must contain at least one lowercase letter.")
            if not re.search(r'[0-9]', password):
                raise forms.ValidationError("Password must contain at least one digit.")
        return password
    
    def clean_logo(self):
        logo = self.cleaned_data.get('logo')
        if logo:
            # Validate file size (limit to 5MB)
            if logo.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Logo file size must be less than 5MB.")
            
            # Validate file extension
            valid_extensions = ['jpg', 'jpeg', 'png', 'gif']
            ext = logo.name.split('.')[-1].lower()
            if ext not in valid_extensions:
                raise forms.ValidationError(f"Logo must be in one of the following formats: {', '.join(valid_extensions)}")
        return logo
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.is_company = True  
        if commit:
            instance.save()
        return instance
    
    
class JobPostForm(forms.ModelForm):
    class Meta:
        model = JobPosts
        fields = ['designation', 'skills', 'vacancy', 'location', 'department', 'salary', 'closing_date']
        widgets = {
            'closing_date': forms.DateInput(attrs={'type': 'date', 'class': ' border border-gray-300 rounded-lg p-2 w-full'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'border border-gray-300 rounded-lg p-2 w-full'})


class ApplicationStatusForm(forms.ModelForm):
    class Meta:
        model = AppliedStudents
        fields = ['intial_round1', 'tech_round2', 'is_passed']
        widgets = {
            'intial_round1': forms.Select(attrs={'class': 'border border-gray-300 rounded-lg p-2 w-full'}),
            'tech_round2': forms.Select(attrs={'class': 'border border-gray-300 rounded-lg p-2 w-full'}),
            'is_passed': forms.CheckboxInput(attrs={'class': 'border rounded border-gray-300'}),
        }
        



class TechInterviewForm(forms.ModelForm):
    class Meta:
        model = TechInterview
        fields = ['link', 'start_time', 'status']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',  # Enables the datetime picker
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
            }),
        }
        
        

class AssessmentConfigForm(forms.Form):
    """Form for configuring assessment parameters"""
    num_questions = forms.IntegerField(
        label='Number of Questions',
        min_value=1,
        max_value=10,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter number of questions (1-10)'
        })
    )
    
   
class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label='Email Address')

# Form for setting a new password
class SetNewPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(), label='New Password')
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label='Confirm Password')
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords don't match")
        
        return cleaned_data