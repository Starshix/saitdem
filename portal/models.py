from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MinLengthValidator
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    # ЛОГИН
    username_validator = RegexValidator(
        regex=r'^[a-zA-Z][a-zA-Z0-9_]{5,}$',
        message='Логин должен начинаться с буквы и содержать только латинские буквы, цифры и _, минимум 6 символа',
    )
    
    # ТЕЛЕФОН (гибкий)
    phone_validator = RegexValidator(
        regex=r'^[\d\s\-\+\(\)]{10,15}$',
        message='Введите номер телефона (10-15 цифр)'
    )
    
    # ФИО
    full_name_validator = RegexValidator(
        regex=r'^[A-Za-zА-Яа-яЁё\s\-\']+$',
        message='ФИО должно содержать только буквы, пробелы, дефисы и апострофы'
    )
    
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[username_validator, MinLengthValidator(3)],
        error_messages={
            'unique': 'Пользователь с таким логином уже существует.',
        },
        help_text='Минимум 6 символов'
    )
    
    full_name = models.CharField(
        max_length=200,
        verbose_name='ФИО',
        validators=[full_name_validator],
        help_text='Иванов Иван Иванович'
    )
    
    phone = models.CharField(
        max_length=20,
        verbose_name='Телефон',
        validators=[phone_validator]
    )
    email = models.EmailField(
        unique=True,
        verbose_name='Email',
        help_text='pochta@mail.ru'
    )
    def __str__(self):
        return f"{self.full_name} ({self.username})"

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Course(models.Model):
    """Модель курсов"""
    title = models.CharField(
        max_length=200,
        verbose_name='Название курса'
    )
    
    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активный курс'
    )
    
    def short_description(self):
        """Возвращает короткое описание (первые 100 символов)"""
        if len(self.description) > 100:
            return self.description[:100] + "..."
        return self.description
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'

    


class Application(models.Model):
    class Status(models.TextChoices):
        NEW = 'new', 'Новая'
        IN_PROGRESS = 'in_progress', 'Идет обучение'
        COMPLETED = 'completed', 'Обучение завершено'
    
    class PaymentMethod(models.TextChoices):
        CASH = 'cash', 'Наличными'
        PHONE = 'phone', 'Перевод по номеру телефона'
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='applications'
    )
    
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name='Курс',
        related_name='applications'
    )
    
    desired_start_date = models.DateField(
        verbose_name='Желаемая дата начала'
    )
    
    payment_method = models.CharField(
        max_length=10,
        choices=PaymentMethod.choices,
        verbose_name='Способ оплаты'
    )
    
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.NEW,
        verbose_name='Статус'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    
    feedback = models.TextField(
        blank=True,
        null=True,
        verbose_name='Отзыв'
    )
    
    def __str__(self):
        return f"Заявка #{self.id} - {self.course.title} ({self.user.username})"
    
    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-created_at']