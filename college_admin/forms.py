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

    


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = '__all__'

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