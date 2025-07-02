# store/signals.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile, Order, Notification

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(pre_save, sender=Order)
def send_status_change_notification(sender, instance, **kwargs):
    if instance.pk:
        old_order = Order.objects.get(pk=instance.pk)
        if old_order.status != instance.status:
            # Get product names from order items
            item_names = [item.product.name for item in instance.items.all()]
            if item_names:
                if len(item_names) == 1:
                    product_info = item_names[0]
                else:
                    product_info = f"{item_names[0]} and {len(item_names)-1} more item(s)"
            else:
                product_info = f"Order #{instance.id}"  # fallback

            Notification.objects.create(
                user=instance.user,
                message=f"Your order for '{product_info}' is now: {instance.get_status_display()}",
                link="/orders/"
            )
