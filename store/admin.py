from django.contrib import admin
from .models import (
    Product, Category, ProductImage,
    Order, OrderItem, Notification,
    Wishlist, ProductReview
)

# ✅ إدارة المنتجات
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'available', 'seller', 'category')
    list_filter = ('available', 'category')
    search_fields = ('name',)
    exclude = ('seller',)  # ما يظهرش في الفورم

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(seller=request.user)

    def has_change_permission(self, request, obj=None):
        if obj and not request.user.is_superuser:
            return obj.seller == request.user
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and not request.user.is_superuser:
            return obj.seller == request.user
        return super().has_delete_permission(request, obj)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.seller = request.user
        obj.save()

    def get_readonly_fields(self, request, obj=None):
        if obj:  # تعديل
            return self.readonly_fields + ('seller',)
        return self.readonly_fields


# ✅ إدارة الطلبات - تاجر يتحكم في طلبات منتجاته
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'is_paid', 'status', 'created_at')
    inlines = [OrderItemInline]
    readonly_fields = ('user', 'created_at')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(items__product__seller=request.user).distinct()

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.readonly_fields
        # التاجر يمكنه تعديل is_paid و status فقط
        if obj and obj.items.filter(product__seller=request.user).exists():
            return ('user', 'created_at')
        return [f.name for f in self.model._meta.fields]

    def has_change_permission(self, request, obj=None):
        if obj and not request.user.is_superuser:
            return obj.items.filter(product__seller=request.user).exists()
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and not request.user.is_superuser:
            return obj.items.filter(product__seller=request.user).exists()
        return super().has_delete_permission(request, obj)

# ✅ إدارة التقييمات - تاجر يرى تقييمات منتجاته فقط
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(product__seller=request.user)

    def has_change_permission(self, request, obj=None):
        if obj and not request.user.is_superuser:
            return obj.product.seller == request.user
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and not request.user.is_superuser:
            return obj.product.seller == request.user
        return super().has_delete_permission(request, obj)

# ✅ إدارة التصنيفات
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

    def save_model(self, request, obj, form, change):
        if not Category.objects.filter(name__iexact=obj.name).exists():
            obj.save()

# ✅ إدارة الصور
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image')

# ✅ إدارة الإشعارات
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'created_at')

# ✅ إدارة المفضلة
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product')


# ✅ تسجيل جميع الموديلات في لوحة الإدارة
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(ProductImage, ProductImageAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(Wishlist, WishlistAdmin)
admin.site.register(ProductReview, ProductReviewAdmin)
