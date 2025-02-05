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