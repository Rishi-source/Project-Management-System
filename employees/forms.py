from django import forms
from .models import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit
from crispy_forms.bootstrap import *
from django.forms.models import inlineformset_factory

class LoginForm(forms.Form):
    username = forms.CharField(max_length = 255)
    password = forms.CharField(widget = forms.PasswordInput)

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if not username and not password:
            raise forms.ValidationError('Add username and password')

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['Client_Department', 'Division', 'Name_Of_Project', 'Sanctioned_Amount', 
                  'Sanctioned_Amount_Date', 'Technical_Sanctioned_Amount', 'Technical_Sanctioned_Amount_Date','Work_order_Amount', 'Work_order_Amount_Date',
                  'Start_date', 'Stipulated_Date_Of_Completion']
        widgets = {
            'Client_Department': forms.Select(attrs={'class': 'form-control'}),
            'Division': forms.Select(attrs={'class': 'form-control'}),
            'Name_Of_Project': forms.TextInput(attrs={'class': 'form-control'}),
            'Sanctioned_Amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'Sanctioned_Amount_Date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'Technical_Sanctioned_Amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'Technical_Sanctioned_Amount_Date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'Work_order_Amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'Work_order_Amount_Date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'Start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'Stipulated_Date_Of_Completion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
class AmountReceivedForm(forms.ModelForm):
    class Meta:
        model = AmountReceived
        fields = ['Amount_Received_Date', 'Amount_Received']
        widgets = {
            'Amount_Received_Date': forms.DateInput(attrs={'class': 'form-control'}),
            'Amount_Received': forms.NumberInput(attrs={'class': 'form-control'}),
        }
class AmountReleasedForm(forms.ModelForm):
    class Meta:
        model = AmountReleased
        fields = ['Amount_Released_Date', 'Amount_Released']


class PhysicalProgressForm(forms.ModelForm):
    class Meta:
        model = PhysicalProgress
        fields = ['Date_Of_Reporting', 'Physical_Progress_Percentage']



