from django import forms

class LoginForm(forms.Form):
	user = forms.CharField(label="", help_text="", max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Username or email'}))
	password = forms.CharField(label="", help_text="", max_length=100, widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
	depth = forms.IntegerField(label="", help_text="", min_value=1, max_value=10, widget=forms.NumberInput(attrs={'placeholder': 'Depth of search'}))
	roots = forms.CharField(label="", help_text="", max_length=200, required=False, widget=forms.TextInput(attrs={'placeholder': 'Custom roots of search'}))
	rescrap = forms.BooleanField(label="Rescrap known data", help_text="")
