from apps.quiz.models import MyUser, OptionQuestion, Question
from django import forms
from django.contrib.auth.forms import AuthenticationForm


class LoginForm(forms.Form):
    username = forms.CharField(max_length=20, required=True)
    password = forms.CharField(max_length=20, required=True, widget=forms.PasswordInput)

    class Meta:
        model = (MyUser,)
        fields = ["username", "password"]


# class QuestionForm(forms.ModelForm):
#     class Meta:
#         model = Question,
#         fields = ["statement", "time", "difficult_level", "idD", "idA", "idC"]
#         widgets = {
#             "statement": forms.Textarea(attrs={
#                 "class": "form-control",
#                 "rows": 3,
#             }),
#             "idD": forms.Select(attrs={
#                 "class": "form-select",
#             }),
#             "idA": forms.Select(attrs={
#                 "class": "form-select",
#             }),
#             "idC": forms.Select(attrs={
#                 "class": "form-select",
#             }),
#         }

# class OptionQuestionForm(forms.ModelForm):
#     class Meta:
#         model = OptionQuestion,
#         fields = ["motive"]
#         widgets = {
#             "motive": forms.Textarea(attrs={
#                 "class": "form-control",
#                 "rows": 3,
#             }),
#             "idO": forms.Select(attrs={
#                 "class": "form-select",
#             })
#         }
