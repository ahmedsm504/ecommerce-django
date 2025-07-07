# views.py

from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, ProductImage, Category, Order, OrderItem, Notification, Wishlist, Profile, ProductReview
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Q, Avg
from django.contrib import messages
from django.core.paginator import Paginator



def product_list(request):
    categories = Category.objects.prefetch_related('products').all()
    unread_notifications = 0
    if request.user.is_authenticated:
        unread_notifications = request.user.notifications.filter(is_read=False).count()

    return render(request, 'store/product_list.html', {
        'categories': categories,
        'all_categories': Category.objects.all(),
        'unread_notifications': unread_notifications,
    })


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    reviews = product.reviews.all().order_by('-created_at')
    average_rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0

    paginator = Paginator(reviews, 5)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    unread_notifications = 0
    if request.user.is_authenticated:
        unread_notifications = request.user.notifications.filter(is_read=False).count()

    context = {
        'product': product,
        'average_rating': round(average_rating, 1),
        'reviews': page_obj,
        'has_next': page_obj.has_next(),
        'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
        'unread_notifications': unread_notifications,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'store/partials/review_list.html', context)

    return render(request, 'store/product_detail.html', context)


@login_required
def add_review(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '')

        if not rating:
            messages.error(request, "Please select a rating before submitting your review.")
            return redirect('product_detail', pk=pk)

        existing_review = ProductReview.objects.filter(product=product, user=request.user).first()
        if existing_review:
            messages.warning(request, "You have already reviewed this product.")
            return redirect('product_detail', pk=pk)

        ProductReview.objects.create(
            product=product,
            user=request.user,
            rating=int(rating),
            comment=comment
        )
        messages.success(request, "Review added successfully.")
        return redirect('product_detail', pk=pk)

    return redirect('product_detail', pk=pk)


# ... (rest of views remain unchanged)


def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = category.products.filter(available=True)

    unread_notifications = 0
    if request.user.is_authenticated:
        unread_notifications = request.user.notifications.filter(is_read=False).count()

    return render(request, 'store/category_detail.html', {
        'category': category,
        'products': products,
        'unread_notifications': unread_notifications,
    })



# تسجيل مستخدم جديد
def register_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('product_list')
    else:
        form = UserCreationForm()
    return render(request, 'store/register.html', {'form': form})

# تسجيل دخول
def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('product_list')
    else:
        form = AuthenticationForm()
    return render(request, 'store/login.html', {'form': form})

# تسجيل خروج
def logout_user(request):
    logout(request)
    return redirect('product_list')

from .models import Profile  # لو مش مستورد

from .models import Notification  # تأكد إن السطر ده موجود فوق

from collections import defaultdict

@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('product_list')

    profile = request.user.profile
    if request.method == 'POST':
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        if address:
            profile.address = address
        if phone:
            profile.phone = phone
        profile.save()

        # 🟢 تجميع المنتجات حسب البائع
        seller_items = defaultdict(list)
        for product_id, quantity in cart.items():
            product = Product.objects.get(id=product_id)
            seller_items[product.seller].append({'product': product, 'quantity': quantity})

        for seller, items in seller_items.items():
            order = Order.objects.create(user=request.user, is_paid=True)

            for item in items:
                OrderItem.objects.create(order=order, product=item['product'], quantity=item['quantity'])

            # إشعار للبائع
            Notification.objects.create(
                user=seller,
                message=f"New order from {request.user.username} includes your products.",
                link="/admin/store/order/"
            )

        # إشعار للمشتري
        Notification.objects.create(
            user=request.user,
            message="Your order has been placed successfully.",
            link="/orders/"
        )

        request.session['cart'] = {}
        return render(request, 'store/checkout_success.html')

    # في حالة GET نعرض ملخص السلة
    items = []
    total = 0
    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        subtotal = product.price * quantity
        items.append({'product': product, 'quantity': quantity, 'subtotal': subtotal})
        total += subtotal

    return render(request, 'store/checkout.html', {
        'items': items,
        'total': total,
        'profile': profile,
    })


# عرض سلة المشتريات
@login_required
def view_cart(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0

    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            quantity = int(quantity)
            subtotal = product.price * quantity
            items.append({'product': product, 'quantity': quantity, 'subtotal': subtotal})
            total += subtotal
        except Product.DoesNotExist:
            continue

    return render(request, 'store/cart.html', {'items': items, 'total': total})


# إضافة منتج للسلة
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required(login_url='login')
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})

    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            quantity = 1
    except (ValueError, TypeError):
        quantity = 1

    current_quantity = cart.get(str(product_id), 0)
    cart[str(product_id)] = current_quantity + quantity

    request.session['cart'] = cart
    messages.success(request, "Product added to cart.")
    return redirect('product_detail', pk=product_id)




# حذف منتج من السلة
@login_required
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart.pop(str(product_id), None)
    request.session['cart'] = cart
    return redirect('view_cart')


# تعديل الكميات في السلة
@require_POST
@login_required
def update_cart(request):
    cart = request.session.get('cart', {})

    for product_id in list(cart.keys()):
        qty_key = f"quantity_{product_id}"
        qty = request.POST.get(qty_key)
        try:
            qty = int(qty)
            if qty > 0:
                cart[product_id] = qty
            else:
                cart.pop(product_id)
        except (ValueError, TypeError):
            continue

    request.session['cart'] = cart
    return redirect('view_cart')

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Profile

@login_required
def my_account(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        request.user.first_name = name
        request.user.save()

        profile.phone = phone
        profile.address = address
        profile.save()

        return redirect('my_account')

    return render(request, 'store/my_account.html', {
        'profile': profile,
    })

@login_required
def notifications_view(request):
    notifications = request.user.notifications.order_by('-created_at')
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'store/notifications.html', {
        'notifications': notifications,
        'unread_notifications': 0  # علشان مينزلش في البار عدد قديم
    })


from django.contrib.auth.decorators import login_required
from .models import Order

@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/order_list.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/order_detail.html', {'order': order})

@login_required
def delete_notification(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.delete()
    return redirect('notifications')


@login_required
def clear_notifications(request):
    request.user.notifications.all().delete()
    return redirect('notifications')

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status in ['pending', 'processing']:
        order.status = 'cancelled'
        order.save()

        Notification.objects.create(
            user=request.user,
            message=f"Your order containing: {', '.join(item.product.name for item in order.items.all())} has been cancelled.",
            link="/orders/"
        )

    return redirect('order_list')


@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'store/wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.get_or_create(user=request.user, product=product)
    return redirect('wishlist')

@login_required
def remove_from_wishlist(request, product_id):
    Wishlist.objects.filter(user=request.user, product_id=product_id).delete()
    return redirect('wishlist')


def search_products(request):
    query = request.GET.get('q', '')
    products = Product.objects.all()

    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    # فلترة
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    color = request.GET.get('color')
    size = request.GET.get('size')
    rating = request.GET.get('rating')

    if price_min:
        products = products.filter(price__gte=price_min)
    if price_max:
        products = products.filter(price__lte=price_max)
    if color:
        products = products.filter(color__iexact=color)
    if size:
        products = products.filter(size__iexact=size)
    if rating:
        products = products.annotate(avg_rating=Avg('reviews__rating')).filter(avg_rating__gte=rating)

    return render(request, 'store/search_results.html', {
        'products': products,
        'query': query
    })




from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from .models import ProductReview, Product

@login_required
def edit_review_inline(request, product_id, review_id):
    review = get_object_or_404(ProductReview, id=review_id, product_id=product_id, user=request.user)

    if request.method == 'POST':
        review.rating = int(request.POST['rating'])
        review.comment = request.POST.get('comment', '')
        review.save()

    return redirect('product_detail', pk=product_id)

@login_required
def delete_review(request, product_id, review_id):
    review = get_object_or_404(ProductReview, id=review_id, product_id=product_id, user=request.user)

    if request.method == 'POST':
        review.delete()

    return redirect('product_detail', pk=product_id)



from django.contrib.auth.decorators import login_required
from .models import OrderItem, Product

@login_required
def seller_orders(request):
    # كل المنتجات الخاصة بالإدمن الحالي
    seller_products = Product.objects.filter(seller=request.user)

    # كل العناصر اللي فيها منتجات هذا الإدمن
    order_items = OrderItem.objects.filter(product__in=seller_products).select_related('order', 'product')

    # نجهز جدول الطلبات مع المنتجات المطلوبة من هذا الإدمن
    orders_dict = {}
    for item in order_items:
        order_id = item.order.id
        if order_id not in orders_dict:
            orders_dict[order_id] = {
                'order': item.order,
                'items': []
            }
        orders_dict[order_id]['items'].append(item)

    return render(request, 'store/seller_orders.html', {
        'seller_orders': orders_dict.values(),
    })


from django.contrib.auth.models import User

def seller_products(request, seller_id):
    seller = get_object_or_404(User, id=seller_id)
    products = Product.objects.filter(seller=seller, available=True)

    return render(request, 'store/seller_products.html', {
        'seller': seller,
        'products': products,
    })
