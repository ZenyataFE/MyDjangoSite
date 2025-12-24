"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

from .models import Comment, Blog, Order, UserProfile, Product, Category

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ('title', 'description', 'content', 'image')
        labels = {
            'title': "Заголовок",
            'description': "Краткое содержание", 
            'content': "Полное содержание",
            'image': "Изображение"
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {'text': "Комментарий"}
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Введите ваш комментарий...'
            }),
        }

class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'Имя пользователя'}))
    password = forms.CharField(label=_("Пароль"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Пароль'}))


class FeedbackForm(forms.Form):
    RATING_CHOICES = [
        (5, 'Отлично'),
        (4, 'Хорошо'),
        (3, 'Удовлетворительно'),
        (2, 'Плохо'),
        (1, 'Очень плохо')
    ]
    
    FREQUENCY_CHOICES = [
        ('daily', 'Ежедневно'),
        ('weekly', 'Еженедельно'),
        ('monthly', 'Ежемесячно'),
        ('first_time', 'Впервые')
    ]
    
    # Поля формы
    name = forms.CharField(
        label='Ваше имя',
        max_length=100,
        min_length=2,
        error_messages={
            'required': 'Пожалуйста, введите ваше имя',
            'min_length': 'Имя должно содержать минимум 2 символа'
        }
    )
    
    email = forms.EmailField(
        label='Ваш email',
        required=False,
        error_messages={
            'invalid': 'Введите корректный email адрес'
        }
    )
    
    rating = forms.ChoiceField(
        label='Общая оценка сайта',
        choices=RATING_CHOICES,
        widget=forms.RadioSelect
    )
    
    visit_frequency = forms.ChoiceField(
        label='Как часто вы посещаете наш сайт?',
        choices=FREQUENCY_CHOICES,
        widget=forms.Select
    )
    
    improvements = forms.MultipleChoiceField(
        label='Что бы вы хотели улучшить на сайте?',
        choices=[
            ('design', 'Дизайн'),
            ('content', 'Контент'),
            ('navigation', 'Навигацию')
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    comments = forms.CharField(
        label='Ваши пожелания и комментарии',
        widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        required=False,
        max_length=1000
    )

# НОВЫЕ ФОРМЫ ДЛЯ ЭЛЕКТРОННОЙ КОММЕРЦИИ

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')
    first_name = forms.CharField(max_length=30, required=True, label='Имя')
    last_name = forms.CharField(max_length=30, required=True, label='Фамилия')
    phone = forms.CharField(max_length=20, required=True, label='Телефон')
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=True, label='Адрес')
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'address', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Создаем профиль пользователя с ролью клиента
            UserProfile.objects.create(
                user=user,
                role='client',
                phone=self.cleaned_data['phone'],
                address=self.cleaned_data['address']
            )
        return user

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('address', 'phone')
        labels = {
            'address': 'Адрес доставки',
            'phone': 'Контактный телефон'
        }
        widgets = {
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Введите полный адрес доставки'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (XXX) XXX-XX-XX'
            }),
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('name', 'description', 'price', 'category', 'image', 'in_stock')
        labels = {
            'name': 'Название товара',
            'description': 'Описание',
            'price': 'Цена',
            'category': 'Категория',
            'image': 'Изображение',
            'in_stock': 'В наличии'
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name', 'description', 'parent')
        labels = {
            'name': 'Название категория',
            'description': 'Описание',
            'parent': 'Родительская категория'
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
        }

class UserRoleForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('role',)
        labels = {
            'role': 'Роль пользователя'
        }
        widgets = {
            'role': forms.Select(attrs={'class': 'form-control'}),
        }