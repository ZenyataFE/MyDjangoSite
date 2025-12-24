from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.db import models
import json
import os

# Импорт моделей
from .models import (
    Blog, Comment, Category, Product, 
    Order, OrderItem, UserProfile, Cart, CartItem
)

# Импорт форм
from .forms import (
    FeedbackForm, UserRegistrationForm, OrderForm, 
    ProductForm, CategoryForm, BlogForm, CommentForm
)

# ============ ОСНОВНЫЕ СТРАНИЦЫ ============

def home(request):
    """Главная страница с последними новостями"""
    latest_news = Blog.objects.all()[:3]
    return render(request, 'app/index.html', {
        'title': 'Ферма "Руно" - Главная',
        'year': datetime.now().year,
        'latest_news': latest_news,
    })

def contact(request):
    return render(request, 'app/contact.html', {
        'title': 'Контакты',
        'message': 'Страница с нашей контактной информацией.',
        'year': datetime.now().year,
    })

def about(request):
    return render(request, 'app/about.html', {
        'title': 'О нас',
        'message': 'Сведения о хозяйстве.',
        'year': datetime.now().year,
    })

def links(request):
    """Представление для страницы полезных ресурсов"""
    return render(request, 'app/links.html')

def pool(request):
    """Представление для страницы отзывов"""
    data = None
    
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            # Получаем очищенные данные
            data = {
                'name': form.cleaned_data['name'],
                'email': form.cleaned_data['email'],
                'rating': dict(form.fields['rating'].choices)[int(form.cleaned_data['rating'])],
                'visit_frequency': dict(form.fields['visit_frequency'].choices)[form.cleaned_data['visit_frequency']],
                'improvements': ', '.join([dict(form.fields['improvements'].choices)[i] for i in form.cleaned_data['improvements']]) if form.cleaned_data['improvements'] else 'Не указано',
                'comments': form.cleaned_data['comments'] or 'Не указано',
                'date': datetime.now().strftime("%d.%m.%Y %H:%M"),
                'ip': request.META.get('REMOTE_ADDR', 'Неизвестно')
            }
            
            # Сохраняем отзыв в файл (простой способ)
            save_feedback_to_file(data)
            
            form = None  # Очищаем форму для отображения благодарности
    else:
        form = FeedbackForm()
    
    return render(request, 'app/pool.html', {
        'form': form,
        'data': data,
        'title': 'Обратная связь',
        'year': datetime.now().year,
    })

def save_feedback_to_file(feedback_data):
    """Сохраняет отзыв в JSON файл"""
    try:
        # Создаем директорию если нет
        os.makedirs('feedback_data', exist_ok=True)
        
        file_path = 'feedback_data/feedbacks.json'
        
        # Читаем существующие отзывы
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    feedbacks = json.load(f)
                except json.JSONDecodeError:
                    feedbacks = []
        else:
            feedbacks = []
        
        # Добавляем новый отзыв
        feedbacks.append(feedback_data)
        
        # Сохраняем обратно
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(feedbacks, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        print(f"Ошибка при сохранении отзыва: {e}")

def load_feedbacks_from_file():
    """Загружает отзывы из JSON файла"""
    try:
        file_path = 'feedback_data/feedbacks.json'
        
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Ошибка при загрузке отзывов: {e}")
        return []

def registration(request):
    """Регистрация нового пользователя с ролью клиента"""
    assert isinstance(request, HttpRequest)
    
    if request.method == "POST":
        regform = UserRegistrationForm(request.POST)
        if regform.is_valid():
            user = regform.save()
            
            from django.contrib.auth import login
            login(request, user)
            
            messages.success(request, f'Регистрация прошла успешно! Добро пожаловать, {user.username}!')
            return redirect('home')
    else:
        regform = UserRegistrationForm()
    
    return render(
        request,
        'app/registration.html',
        {
            'regform': regform,
            'title': 'Регистрация',
            'year': datetime.now().year,
        }
    )

def blog(request):
    """Renders the blog page."""
    assert isinstance(request, HttpRequest)
    posts = Blog.objects.all()
    return render(
        request,
        'app/blog.html',
        {
            'title': 'Блог фермы',
            'posts': posts,
            'year': datetime.now().year,
        }
    )

def blogpost(request, parametr):
    """Renders the blogpost page."""
    assert isinstance(request, HttpRequest)
    
    post_1 = Blog.objects.get(id=parametr)
    comments = Comment.objects.filter(post=parametr)
    
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment_f = form.save(commit=False)
            comment_f.author = request.user
            comment_f.date = datetime.now()
            comment_f.post = Blog.objects.get(id=parametr)
            comment_f.save()
            return redirect('blogpost', parametr=post_1.id)
    else:
        form = CommentForm()
    
    return render(
        request,
        'app/blogpost.html',
        {
            'post_1': post_1,
            'comments': comments,
            'form': form,
            'year': datetime.now().year,
        }
    )

def newpost(request):
    """Добавление новой статьи блога"""
    assert isinstance(request, HttpRequest)
    
    if request.method == "POST":
        blogform = BlogForm(request.POST, request.FILES)
        if blogform.is_valid():
            blog_f = blogform.save(commit=False)
            blog_f.author = request.user
            blog_f.posted = datetime.now()
            blog_f.save()
            return redirect('blog')
    else:
        blogform = BlogForm()
    
    return render(
        request,
        'app/newpost.html',
        {
            'blogform': blogform,
            'title': 'Добавить статью',
            'year': datetime.now().year,
        }
    )

def videopost(request):
    """Страница с видео"""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/videopost.html',
        {
            'title': 'Видео с фермы',
            'year': datetime.now().year,
        }
    )

# ============ ДЕКОРАТОРЫ ДЛЯ ПРОВЕРКИ РОЛЕЙ ============

def client_required(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            if not hasattr(request.user, 'userprofile'):
                UserProfile.objects.create(user=request.user, role='client')
            if request.user.userprofile.role in ['client', 'manager', 'admin']:
                return function(request, *args, **kwargs)
        messages.error(request, 'Доступ только для зарегистрированных клиентов')
        return redirect('login')
    return wrap

def manager_required(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            if not hasattr(request.user, 'userprofile'):
                role = 'admin' if request.user.is_superuser else 'client'
                UserProfile.objects.create(user=request.user, role=role)
            
            if (request.user.userprofile.role in ['manager', 'admin'] or 
                request.user.is_superuser):
                return function(request, *args, **kwargs)
        
        messages.error(request, 'Доступ только для менеджеров и администраторов')
        return redirect('login')
    return wrap

def admin_required(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            if not hasattr(request.user, 'userprofile'):
                role = 'admin' if request.user.is_superuser else 'client'
                UserProfile.objects.create(user=request.user, role=role)
            
            if request.user.userprofile.role == 'admin' or request.user.is_superuser:
                return function(request, *args, **kwargs)
        messages.error(request, 'Доступ только для администраторов')
        return redirect('login')
    return wrap

# ============ КАТАЛОГ ТОВАРОВ ============

def catalog(request):
    """Страница каталога товаров"""
    categories = Category.objects.filter(parent__isnull=True)
    products = Product.objects.filter(in_stock=True)   ###Фильтр
    
    cart_info = {}
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_info = {item.product_id: item.quantity for item in cart.items.all()}
        except Cart.DoesNotExist:
            pass
    
    return render(request, 'app/catalog.html', {
        'title': 'Каталог продукции',
        'categories': categories,
        'products': products,
        'cart_info': cart_info,
        'year': datetime.now().year,
    })

def category_products(request, category_id):
    """Товары конкретной категории"""
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category, in_stock=True)
    subcategories = Category.objects.filter(parent=category)
    
    return render(request, 'app/category_products.html', {
        'title': f'Категория: {category.name}',
        'category': category,
        'products': products,
        'subcategories': subcategories,
        'year': datetime.now().year,
    })

def product_detail(request, product_id):
    """Детальная страница товара"""
    product = get_object_or_404(Product, id=product_id)
    
    # Получаем количество товара в корзине пользователя
    cart_quantity = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_item = cart.items.filter(product=product).first()
            if cart_item:
                cart_quantity = cart_item.quantity
        except Cart.DoesNotExist:
            pass
    
    # Вычисляем общую стоимость
    total_cost = product.price * cart_quantity if cart_quantity > 0 else 0
    
    return render(request, 'app/product_detail.html', {
        'title': product.name,
        'product': product,
        'cart_quantity': cart_quantity,
        'total_cost': total_cost,
        'year': datetime.now().year,
    })

# ============ КОРЗИНА ============

@login_required
def cart(request):
    """Корзина пользователя"""
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all()
        total_price = sum(item.total_price() for item in cart_items)
    except Cart.DoesNotExist:
        cart_items = []
        total_price = 0
    
    return render(request, 'app/cart.html', {
        'title': 'Корзина',
        'cart_items': cart_items,
        'total_price': total_price,
        'year': datetime.now().year,
    })

@login_required
def add_to_cart(request, product_id):
    """Добавление товара в корзину"""
    product = get_object_or_404(Product, id=product_id)
    
    if not hasattr(request.user, 'userprofile'):
        UserProfile.objects.create(user=request.user, role='client')
    
    user_role = request.user.userprofile.role
    
    if user_role == 'guest':
        messages.error(request, 
            '❌ Гости не могут добавлять товары в корзину. '
            'Пожалуйста, зарегистрируйтесь для совершения покупок.'
        )
        return redirect('registration')
    
    elif user_role in ['manager', 'admin']:
        messages.warning(request,
            f'⚠️ Вы не можете добавлять товары в корзину, так как являетесь '
            f'<strong>{request.user.userprofile.get_role_display().lower()}</strong>. '
            f'Эта функция доступна только клиентам.'
        )
        return redirect('product_detail', product_id=product_id)
    
    elif user_role == 'client':
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': 1}
        )
        
        if not created:
            cart_item.quantity += 1
            cart_item.save()
            message = f'✅ Товар "<strong>{product.name}</strong>" добавлен в корзину! Теперь его <strong>{cart_item.quantity} шт.</strong>'
        else:
            message = f'✅ Товар "<strong>{product.name}</strong>" добавлен в корзину!'
        
        messages.success(request, message)
        return redirect('product_detail', product_id=product_id)
    
    else:
        messages.error(request, 'Неизвестная роль пользователя')
        return redirect('product_detail', product_id=product_id)

@login_required
def update_cart(request, item_id):
    """Обновление количества товара в корзине"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    if request.method == 'POST':
        new_quantity = int(request.POST.get('quantity', 1))
        if new_quantity > 0:
            cart_item.quantity = new_quantity
            cart_item.save()
            messages.success(request, 'Количество товара обновлено')
        else:
            cart_item.delete()
            messages.success(request, 'Товар удален из корзины')
    
    return redirect('cart')

@login_required
def remove_from_cart(request, item_id):
    """Удаление товара из корзины"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f'Товар "{product_name}" удален из корзины')
    return redirect('cart')

# ============ ЗАКАЗЫ ============

@client_required
def my_orders(request):
    """История заказов клиента"""
    orders = Order.objects.filter(client=request.user).order_by('-created_at')
    return render(request, 'app/my_orders.html', {
        'title': 'Мои заказы',
        'orders': orders,
        'year': datetime.now().year,
    })

@client_required
def create_order(request):
    """Создание заказа из корзины"""
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all()
        
        if not cart_items:
            messages.error(request, 'Ваша корзина пуста')
            return redirect('cart')
        
        if request.method == 'POST':
            form = OrderForm(request.POST)
            if form.is_valid():
                order = form.save(commit=False)
                order.client = request.user
                order.total_price = cart.total_price()
                order.save()
                
                for cart_item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        price=cart_item.product.price
                    )
                
                cart.items.all().delete()
                
                messages.success(request, f'Заказ #{order.id} успешно создан! С вами свяжется менеджер для подтверждения.')
                return redirect('my_orders')
    except Cart.DoesNotExist:
        messages.error(request, 'Ваша корзина пуста')
        return redirect('cart')
    
    initial_data = {}
    if hasattr(request.user, 'userprofile'):
        initial_data = {
            'phone': request.user.userprofile.phone,
            'address': request.user.userprofile.address
        }
    form = OrderForm(initial=initial_data)
    
    return render(request, 'app/create_order.html', {
        'title': 'Оформление заказа',
        'form': form,
        'cart_items': cart_items,
        'total_price': cart.total_price(),
        'year': datetime.now().year,
    })

@client_required
def order_detail(request, order_id):
    """Детали заказа"""
    order = get_object_or_404(Order, id=order_id, client=request.user)
    
    # Получаем товары заказа
    order_items = order.items.all()
    
    return render(request, 'app/order_detail.html', {
        'title': f'Заказ #{order.id}',
        'order': order,
        'order_items': order_items,
        'year': datetime.now().year,
    })

# ============ ПАНЕЛЬ МЕНЕДЖЕРА ============

@manager_required
def manager_orders(request):
    """Управление заказами для менеджера"""
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'app/manager_orders.html', {
        'title': 'Управление заказами',
        'orders': orders,
        'year': datetime.now().year,
    })

@manager_required
def update_order_status(request, order_id):
    """Изменение статуса заказа менеджером"""
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f'Статус заказа #{order.id} изменен на "{order.get_status_display()}"')
        else:
            messages.error(request, 'Неверный статус заказа')
    return redirect('manager_orders')

# ============ АДМИН-ПАНЕЛЬ ============

@admin_required
def admin_dashboard(request):
    """Главная страница админ-панели"""
    stats = {
        'users_count': User.objects.count(),
        'products_count': Product.objects.count(),
        'categories_count': Category.objects.count(),
        'orders_count': Order.objects.count(),
        'blog_posts_count': Blog.objects.count(),
    }
    
    recent_products = Product.objects.all().order_by('-created_at')[:5]
    recent_orders = Order.objects.all().order_by('-created_at')[:5]
    
    return render(request, 'app/admin_dashboard.html', {
        'title': 'Панель управления',
        'stats': stats,
        'recent_products': recent_products,
        'recent_orders': recent_orders,
        'year': datetime.now().year,
    })

@admin_required
def admin_feedback(request):
    """Просмотр отзывов для администратора"""
    # Загружаем отзывы из файла
    feedbacks = load_feedbacks_from_file()
    
    # Статистика
    stats = {
        'total': len(feedbacks),
        'today': len([f for f in feedbacks if f.get('date', '').startswith(datetime.now().strftime("%d.%m.%Y"))]),
    }
    
    return render(request, 'app/admin_feedback.html', {
        'title': 'Просмотр отзывов',
        'feedbacks': feedbacks[::-1],  # Новые сверху
        'stats': stats,
        'year': datetime.now().year,
    })

@admin_required
def admin_users(request):
    """Управление пользователями"""
    users = User.objects.all().select_related('userprofile')
    return render(request, 'app/admin_users.html', {
        'title': 'Управление пользователями',
        'users': users,
        'year': datetime.now().year,
    })

@admin_required
def delete_user(request, user_id):
    """Удаление пользователя"""
    user = get_object_or_404(User, id=user_id)
    if user != request.user and not user.is_superuser:
        username = user.username
        user.delete()
        messages.success(request, f'Пользователь {username} удален')
    else:
        messages.error(request, 'Нельзя удалить этого пользователя')
    return redirect('admin_users')

@admin_required
def set_user_role(request, user_id):
    """Изменение роли пользователя"""
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        new_role = request.POST.get('role')
        if new_role in ['guest', 'client', 'manager', 'admin']:
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.role = new_role
            profile.save()
            messages.success(request, f'Роль пользователя {user.username} изменена на {new_role}')
    return redirect('admin_users')

@admin_required
def admin_products(request):
    """Управление товарами"""
    products = Product.objects.all().select_related('category')
    
    if request.method == 'POST':
        if 'delete_id' in request.POST:
            product_id = request.POST.get('delete_id')
            product = get_object_or_404(Product, id=product_id)
            product.delete()
            messages.success(request, f'Товар "{product.name}" удален')
            return redirect('admin_products')
    
    return render(request, 'app/admin_products.html', {
        'title': 'Управление товарами',
        'products': products,
        'year': datetime.now().year,
    })

@admin_required
def admin_product_edit(request, product_id=None):
    """Редактирование/добавление товара"""
    if product_id:
        product = get_object_or_404(Product, id=product_id)
    else:
        product = None
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            saved_product = form.save()
            if product_id:
                messages.success(request, f'Товар "{saved_product.name}" обновлен')
            else:
                messages.success(request, f'Товар "{saved_product.name}" добавлен')
            return redirect('admin_products')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'app/admin_product_edit.html', {
        'title': 'Редактирование товара' if product_id else 'Добавление товара',
        'form': form,
        'product': product,
        'year': datetime.now().year,
    })

@admin_required
def admin_categories(request):
    """Управление категориями"""
    categories = Category.objects.all()
    
    if request.method == 'POST':
        if 'delete_id' in request.POST:
            category_id = request.POST.get('delete_id')
            category = get_object_or_404(Category, id=category_id)
            if Product.objects.filter(category=category).exists():
                messages.error(request, f'Нельзя удалить категорию "{category.name}" - в ней есть товары')
            else:
                category.delete()
                messages.success(request, f'Категория "{category.name}" удалена')
            return redirect('admin_categories')
    
    return render(request, 'app/admin_categories.html', {
        'title': 'Управление категориями',
        'categories': categories,
        'year': datetime.now().year,
    })

@admin_required
def admin_category_edit(request, category_id=None):
    """Редактирование/добавление категории"""
    if category_id:
        category = get_object_or_404(Category, id=category_id)
    else:
        category = None
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            saved_category = form.save()
            if category_id:
                messages.success(request, f'Категория "{saved_category.name}" обновлена')
            else:
                messages.success(request, f'Категория "{saved_category.name}" добавлена')
            return redirect('admin_categories')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'app/admin_category_edit.html', {
        'title': 'Редактирование категории' if category_id else 'Добавление категории',
        'form': form,
        'category': category,
        'year': datetime.now().year,
    })