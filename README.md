# Django E-commerce Platform

This is a full-featured e-commerce website built with Django. It includes core features like product management, user accounts, shopping cart, wishlist, product reviews, notifications, and user behavior tracking with a simple analytics dashboard.

## Features

- User registration, login, and password change
- Product catalog with categories and multiple images
- Product detail pages with ratings and user reviews
- Add to cart and update quantities
- Wishlist system for saving favorite items
- Review system (add/edit/delete)
- Internal notifications for users
- Order checkout and order tracking
- Order cancellation for eligible orders
- Track user behavior (time on page, scrolling, clicking)
- Analytics dashboard to view behavior data

## Tech Stack

### Backend
- Python 3.13
- Django 5.1.6

### Frontend
- HTML + Bootstrap 5
- JavaScript (vanilla)
- Fetch API for AJAX requests

### Libraries Used
- django-crispy-forms – for better form rendering
- django-widget-tweaks – to customize form inputs
- pillow – for image processing
- django.contrib.messages – for flash messages

## Setup Instructions

1. **Clone the repository**

```bash
git clone https://github.com/ahmedsm504/ecommerce-django.git
cd ecommerce-django
```

2. **Create and activate a virtual environment**

```bash
python -m venv env
env\Scripts\activate  # On Windows
```

3. **Install required packages**

```bash
pip install -r requirements.txt
```

4. **Apply migrations**

```bash
python manage.py migrate
```

5. **Run development server**

```bash
python manage.py runserver
```

6. **Create admin user (optional)**

```bash
python manage.py createsuperuser
```

## Folder Structure

- `store/models.py` – defines Product, Review, Order, Wishlist, Notification, and UserBehavior models
- `store/views.py` – contains all business logic for products, cart, behavior tracking, etc.
- `store/templates/` – all HTML templates
- `store/static/` – CSS, JS, images

## User Behavior Tracking

We implemented a lightweight tracker using JavaScript. It sends the following to the server:
- Time spent on page (in seconds)
- Whether the user scrolled
- Whether the user clicked

These are saved in the `UserBehavior` model.

## Analytics Dashboard

Admin or staff users can access a dashboard showing:
- Page URLs visited
- Time spent
- Whether user scrolled or clicked
- Timestamps

This data is displayed using plain HTML tables.

## License

This project is licensed for educational and commercial use. Feel free to fork and contribute.