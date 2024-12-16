from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


from django.contrib.auth.forms import UserCreationForm


class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "bio",
            "role",
            "password1",
            "password2",
            # "image",
            "is_admin",
        ]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4, "cols": 40}),
            "role": forms.TextInput(attrs={"placeholder": "Enter user role"}),
        }


class UserUpdateForm(forms.ModelForm):
    password = forms.CharField(
        required=False,
        label="New Password",
        widget=forms.PasswordInput(
            attrs={"placeholder": "Enter new password (optional)"}
        ),
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "bio", "role", "is_admin"]

    def save(self, commit=True):
        user = super().save(commit=False)
        new_password = self.cleaned_data.get("password")
        if new_password:
            user.set_password(new_password)  # Hashes and sets the password
        if commit:
            user.save()
        return user
