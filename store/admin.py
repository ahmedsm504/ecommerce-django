from django.contrib import admin
from .models import Product, ProductImage
from .models import Notification

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'available')
    inlines = [ProductImageInline]

admin.site.register(Product, ProductAdmin)
from .models import Category
admin.site.register(Category)

# store/admin.py

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'created_at', 'is_read')
    search_fields = ('user__username', 'message')
    list_filter = ('is_read', 'created_at')


from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at', 'is_paid', 'status']
    list_filter = ['status', 'is_paid', 'created_at']
    search_fields = ['user__username', 'id']
    inlines = [OrderItemInline]
    list_editable = ['status', 'is_paid']  # ✅ تسمح بتعديل مباشر من القائمة

