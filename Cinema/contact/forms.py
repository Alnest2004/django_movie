from django import forms
from snowpenguin.django.recaptcha3.fields import ReCaptchaField
from .models import *


class ContactForm(forms.ModelForm):
    """Форма подписки по email"""
    captcha = ReCaptchaField()

    class Meta:
        model = Contact
        fields = ("email", "captcha")
        widgets = {
            "email": forms.TextInput(attrs={"class": "editContent", "placeholder": "Your Email..."})
        }
        # используется для дополнительной настройки поля. В данном случаи меняет значение
        # в <label> </label>. Было: <label>Email</label> Стало: <label> </label>
        labels = {
            "email": ''
        }