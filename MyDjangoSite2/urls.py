from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from app import views
from app.forms import BootstrapAuthenticationForm
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

urlpatterns = [
    # Основные страницы
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('login/', LoginView.as_view(
        template_name='app/login.html',
        authentication_form=BootstrapAuthenticationForm,
        extra_context={'title': 'Авторизация'}
    ), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('links/', views.links, name='links'),
    path('pool/', views.pool, name='pool'),
    path('registration/', views.registration, name='registration'),
    path('blog/', views.blog, name='blog'),
    path('blogpost/<int:parametr>/', views.blogpost, name='blogpost'),
    path('newpost/', views.newpost, name='newpost'),
    path('video/', views.videopost, name='video'),
    
    # Электронная коммерция
    path('catalog/', views.catalog, name='catalog'),
    path('catalog/category/<int:category_id>/', views.category_products, name='category_products'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('orders/', views.my_orders, name='my_orders'),
    path('orders/create/', views.create_order, name='create_order'),
    path('manager/orders/', views.manager_orders, name='manager_orders'),
    path('manager/orders/<int:order_id>/update/', views.update_order_status, name='update_order_status'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    
    # Админ-панель
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/products/', views.admin_products, name='admin_products'),
    path('admin/products/add/', views.admin_product_edit, name='admin_product_add'),
    path('admin/products/edit/<int:product_id>/', views.admin_product_edit, name='admin_product_edit'),
    path('admin/categories/', views.admin_categories, name='admin_categories'),
    path('admin/categories/add/', views.admin_category_edit, name='admin_category_add'),
    path('admin/categories/edit/<int:category_id>/', views.admin_category_edit, name='admin_category_edit'),
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('admin/users/<int:user_id>/set_role/', views.set_user_role, name='set_user_role'),
    path('admin/feedback/', views.admin_feedback, name='admin_feedback'),
    # Добавьте этот путь в urlpatterns
    path('manager/orders/<int:order_id>/update/', views.update_order_status, name='update_order_status'),
    
    # Стандартная Django админка
    path('admin/', admin.site.urls),
    
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
]

# Добавляем обработку медиа-файлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += staticfiles_urlpatterns()