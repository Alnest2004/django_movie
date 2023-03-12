from django import forms
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from snowpenguin.django.recaptcha3.fields import ReCaptchaField

from .models import Reviews, Rating, RatingStar, User


class ReviewForm(forms.ModelForm):
    """Форма отзывов"""
    captcha = ReCaptchaField()

    class Meta:
        model = Reviews
        fields = ("name", "email", "text", "captcha")
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control border"}),
            "email": forms.EmailInput(attrs={"class": "form-control border"}),
            "text": forms.Textarea(attrs={"class": "form-control border"})
        }


class RatingForm(forms.ModelForm):
    """Форма добавления рейтинга"""
    # что бы выводить список добавленных нами звёзд, мы должны переопределить
    # поле star. widget это то как будет представлена форма в html. Меняя
    # widget мы можем менять внешний вид наших форм
    star = forms.ModelChoiceField(
        queryset=RatingStar.objects.all(), widget=forms.RadioSelect(), empty_label=None
    )

    class Meta:
        model = Rating
        fields = ("star",)


class UserCreationForm(BaseUserCreationForm):
    phone = forms.CharField(max_length=20, required=True, help_text='Phone number')

    class Meta:
        model = User
        fields = ('username', 'phone', 'password1', 'password2')


class VerifyForm(forms.Form):
    code = forms.CharField(max_length=8, required=True, help_text='Enter code')
