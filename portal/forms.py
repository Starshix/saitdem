from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.validators import MinLengthValidator
from .models import CustomUser, Application, Course


from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.core.exceptions import ValidationError

class SimpleUserCreationForm(forms.ModelForm):
    """Упрощенная форма регистрации без подтверждения пароля"""
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        validators=[MinLengthValidator(8)],
        help_text='Минимум 8 символов'
    )
    
    class Meta:
        model = CustomUser
        fields = ['username', 'full_name', 'phone', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '8(XXX)XXX-XX-XX'
            }),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'username': 'Логин',
            'full_name': 'ФИО',
            'phone': 'Телефон',
            'email': 'Email',
        }
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
    



class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label='Логин',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )


class ApplicationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['course'].widget.attrs.update({
            'class': 'form-control',
            'id': 'course-select',
            'onchange': 'showCourseDescription()'
        })
    
    class Meta:
        model = Application
        fields = ['course', 'desired_start_date', 'payment_method']
        widgets = {
            'desired_start_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                    'placeholder': 'YYYY-MM-DD'
                }
            ),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'course': 'Курс',
            'desired_start_date': 'Желаемая дата начала',
            'payment_method': 'Способ оплаты',
        }


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['feedback']
        widgets = {
            'feedback': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Оставьте ваш отзыв о качестве обучения...'
            }),
        }
        labels = {
            'feedback': 'Отзыв',
        }


class ApplicationStatusForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'status': 'Статус заявки',
        }

class UserProfileForm(forms.ModelForm):
    current_password = forms.CharField(
        label='Текущий пароль (для подтверждения изменений)',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False
    )
    
    new_password = forms.CharField(
        label='Новый пароль (оставьте пустым, если не хотите менять)',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        min_length=8
    )
    
    confirm_password = forms.CharField(
        label='Подтверждение нового пароля',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False
    )
    
    class Meta:
        model = CustomUser
        fields = ['full_name', 'phone', 'email']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '8(XXX)XXX-XX-XX'
            }),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'full_name': 'ФИО',
            'phone': 'Телефон',
            'email': 'Email',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        current_password = cleaned_data.get('current_password')
        
        if new_password and new_password != confirm_password:
            self.add_error('confirm_password', 'Пароли не совпадают')
        
        if new_password and not current_password:
            self.add_error('current_password', 'Введите текущий пароль для смены пароля')
        
        return cleaned_data
    
