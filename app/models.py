from django.db import models
from django.contrib import admin
from django.urls import reverse
from datetime import datetime
from django.contrib.auth.models import User


# Расширение модели пользователя для ролей
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('guest', 'Гость'),
        ('client', 'Клиент'),
        ('manager', 'Менеджер'),
        ('admin', 'Администратор'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='guest')
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    address = models.TextField(blank=True, verbose_name="Адрес")
    
    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

# Модели для каталога товаров
class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    description = models.TextField(blank=True, verbose_name="Описание")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name="Родительская категория")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "категории"

class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название товара")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категория")
    image = models.FileField(upload_to='products/', default='temp.jpg', verbose_name="Изображение")  # ИЗМЕНЕНО: FileField вместо ImageField
    in_stock = models.BooleanField(default=True, verbose_name="В наличии")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "товар"
        verbose_name_plural = "товары"

# Модели для заказов
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает обработки'),
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменен'),
    ]
    
    client = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Клиент")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Общая стоимость")
    address = models.TextField(verbose_name="Адрес доставки")
    phone = models.CharField(max_length=20, verbose_name="Контактный телефон")
    
    def __str__(self):
        return f"Заказ #{self.id} - {self.client.username}"
    
    class Meta:
        verbose_name = "заказ"
        verbose_name_plural = "заказы"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

class Blog(models.Model):
    title = models.CharField(
        max_length=100,
        unique_for_date="posted",
        verbose_name="Заголовок"
    )
    description = models.TextField(verbose_name="Краткое содержание")
    content = models.TextField(verbose_name="Полное содержание")
    posted = models.DateTimeField(
        default=datetime.now,
        db_index=True,
        verbose_name="Опубликована"
    )
    author = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Автор"
    )
    image = models.FileField(
        default='temp.jpg',
        verbose_name="Путь к картинке"
    )
    
    # Методы класса
    def get_absolute_url(self):
        """Возвращает строку с URL-адресом записи"""
        return reverse("blogpost", args=[str(self.id)])
    
    def __str__(self):
        """Возвращает название, используемое для представления отдельных записей"""
        return self.title
    
    # Метаданные
    class Meta:
        db_table = "Posts"
        ordering = ["-posted"]
        verbose_name = "статья блога"
        verbose_name_plural = "статьи блога"


class Comment(models.Model):
    text = models.TextField(verbose_name="Текст комментария")
    date = models.DateTimeField(default=datetime.now, db_index=True, verbose_name="Дата комментария")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор комментария")
    post = models.ForeignKey(Blog, on_delete=models.CASCADE, verbose_name="Статья комментария")
    
    def __str__(self):
        return f'Комментарий {self.author} к статье "{self.post.title}"'
    
    class Meta:
        db_table = "Comments"
        ordering = ["-date"]
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"


class Cart(models.Model):
    """Корзина покупок"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Корзина пользователя {self.user.username}"

    def total_price(self):
        return sum(item.total_price() for item in self.items.all())

    def items_count(self):
        return self.items.count()

class CartItem(models.Model):
    """Элемент корзины"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def total_price(self):
        return self.product.price * self.quantity

    class Meta:
        unique_together = ['cart', 'product']
        
class Feedback(models.Model):
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
    
    name = models.CharField(max_length=100, verbose_name="Имя")
    email = models.EmailField(verbose_name="Email", blank=True)
    rating = models.IntegerField(choices=RATING_CHOICES, verbose_name="Оценка")
    visit_frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, verbose_name="Частота посещений")
    improvements = models.CharField(max_length=200, blank=True, verbose_name="Предложения по улучшению")
    comments = models.TextField(verbose_name="Комментарии", blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата отправки")
    ip_address = models.GenericIPAddressField(verbose_name="IP адрес", blank=True, null=True)
    
    def __str__(self):
        return f"Отзыв от {self.name} ({self.created_at.date()})"
    
    class Meta:
        verbose_name = "отзыв"
        verbose_name_plural = "отзывы"
        ordering = ['-created_at']


# Регистрация моделей в административном разделе
admin.site.register(Blog)
admin.site.register(Comment)
admin.site.register(UserProfile)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Cart)
admin.site.register(CartItem)

