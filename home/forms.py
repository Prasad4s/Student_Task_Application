from django import forms
from .models import student

from django import forms

class TaskForm(forms.Form):
    name = forms.ChoiceField(choices=[])
    task_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Enter Task'}))
    task_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    def __init__(self, *args, **kwargs):
        names = kwargs.pop('names', [])
        super(TaskForm, self).__init__(*args, **kwargs)
        self.fields['name'].choices = [(name.student_id, name.name) for name in names]

    
class RegisterForm(forms.Form):
    name = forms.CharField(max_length=100)
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)



class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

