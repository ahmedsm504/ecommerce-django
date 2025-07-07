from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('category/<int:category_id>/', views.category_detail, name='category_detail'),
    path('product/<int:pk>/review/', views.add_review, name='add_review'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('checkout/', views.checkout, name='checkout'),
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('account/', views.my_account, name='my_account'),
    path('password-change/', auth_views.PasswordChangeView.as_view(
        template_name='store/password_change.html',
        success_url='/account/'
    ), name='password_change'),

    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
   path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),

    path('cart/', views.view_cart, name='view_cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart/', views.update_cart, name='update_cart'),

    path('notifications/delete/<int:pk>/', views.delete_notification, name='delete_notification'),
    path('notifications/clear/', views.clear_notifications, name='clear_notifications'),

    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),

    path('search/', views.search_products, name='search_products'),
    path('product/<int:product_id>/review/<int:review_id>/edit/', views.edit_review_inline, name='edit_review_inline'),
    path('product/<int:product_id>/review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
    path('seller/<int:seller_id>/', views.seller_products, name='seller_products'),

    path('seller/orders/', views.seller_orders, name='seller_orders'),

]
