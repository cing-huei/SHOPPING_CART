from django import forms
from captcha.fields import CaptchaField

class PostForm(forms.Form):
    captcha = CaptchaField()