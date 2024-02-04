from django import forms

class loginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class':"form-control", 'style':"height: 50px; width: 350px;",'placeholder':'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':"form-control", 'style':"height: 50px; width: 350px;",'placeholder':'Password'}))