from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.views.generic import ListView
from .models import CustomUser, Application, Course
import os
from django.conf import settings

from .forms import (
    SimpleUserCreationForm, 
    CustomAuthenticationForm,
    ApplicationForm,
    FeedbackForm,
    ApplicationStatusForm,
    UserProfileForm
)

def admin_required(view_func):
    decorated_view_func = user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='login'
    )(view_func)
    return decorated_view_func


def register_view(request):
    if request.method == 'POST':
        form = SimpleUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Регистрация прошла успешно! Теперь вы можете войти.')
            return redirect('login')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = SimpleUserCreationForm()
    
    return render(request, 'portal/register.html', {'form': form})


class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'portal/login.html'
    
    def get_success_url(self):
        user = self.request.user
        if user.is_superuser:
            messages.success(self.request, f'Добро пожаловать в панель администратора, {user.username}!')
            return '/myadmin/dashboard/'
        else:
            messages.success(self.request, f'Добро пожаловать, {user.full_name}!')
            return '/profile/'


def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('login')


@login_required
def profile_view(request):
    user_applications = Application.objects.filter(user=request.user)
    
    if request.method == 'POST' and 'feedback' in request.POST:
        app_id = request.POST.get('application_id')
        application = get_object_or_404(Application, id=app_id, user=request.user)
        form = FeedbackForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            messages.success(request, 'Отзыв успешно сохранен!')
            return redirect('profile')
    
    return render(request, 'portal/profile.html', {
        'applications': user_applications,
        'feedback_form': FeedbackForm()
    })

@login_required
def edit_profile_view(request):
    user = request.user
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            new_password = form.cleaned_data.get('new_password')
            current_password = form.cleaned_data.get('current_password')
            
            if new_password:
                if not user.check_password(current_password):
                    form.add_error('current_password', 'Неверный текущий пароль')
                    return render(request, 'portal/edit_profile.html', {'form': form})
                
                user.set_password(new_password)
            
            user = form.save(commit=False)
            if new_password:
                user.set_password(new_password)
            user.save()
            
            if new_password:
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(request, user)
            
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user)
    
    return render(request, 'portal/edit_profile.html', {'form': form})


@login_required
def create_application_view(request):
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.save()
            messages.success(request, 'Заявка успешно создана! Она будет рассмотрена администратором.')
            return redirect('profile')
    else:
        form = ApplicationForm()
    

    active_courses = Course.objects.filter(is_active=True)
    form.fields['course'].queryset = active_courses
    
    courses_data = [
        {
            'id': course.id,
            'title': course.title,
            'description': course.description,
            'short_desc': course.short_description() if hasattr(course, 'short_description') else course.description[:100] + "..."
        }
        for course in active_courses
    ]
    
    return render(request, 'portal/application_form.html', {
        'form': form,
        'courses_data': courses_data,
    })


@admin_required
def admin_dashboard_view(request):
    all_applications = Application.objects.all()
    
    if request.method == 'POST' and 'status' in request.POST:
        app_id = request.POST.get('application_id')
        application = get_object_or_404(Application, id=app_id)
        form = ApplicationStatusForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            messages.success(request, f'Статус заявки #{app_id} изменен.')
            return redirect('admin_dashboard')
    
    return render(request, 'portal/admin_dashboard.html', {
        'applications': all_applications,
        'status_form': ApplicationStatusForm()
    })


def home_view(request):
    """Главная страница"""
    # Получаем список изображений для слайдера
    slider_images = []
    slider_path = os.path.join(settings.MEDIA_ROOT, 'slider')
        
    if os.path.exists(slider_path):
        # Ищем файлы с расширениями изображений
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        for filename in os.listdir(slider_path):
            if any(filename.lower().endswith(ext) for ext in image_extensions):
                # Создаем путь относительно MEDIA_URL
                slider_images.append(f'slider/{filename}')
        
    # Если нет реальных изображений, используем заглушки
    if not slider_images:
        slider_images = [
            'slider/image08.webp',
            'slider/image09.webp', 
            'slider/image10.webp',
            'slider/image11.jpg'
        ]
        
    context = {
        'slider_images': slider_images[:4],  # Берем максимум 4 изображения
    }

    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admin_dashboard')
        else:
            return redirect('profile')
    return render(request, 'portal/home.html', context)