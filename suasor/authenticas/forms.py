from django import forms

class SuasorLoginForm(forms.Form):
    user_id = forms.CharField(label="", help_text="", max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Facebook user ID'}))
    password = forms.CharField(label="", help_text="", max_length=20, widget=forms.PasswordInput(attrs={'placeholder': 'Password for Suasor'}))
