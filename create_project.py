
from pathlib import Path

ROOT = Path(__file__).parent

FILES = {
    "Backend/requirements.txt": """
Django
mysqlclient
python-dotenv
""",

    "Backend/.env.example": """
DB_NAME=sales_inventory
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
""",

    "Backend/manage.py": """
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
""",

    "Backend/config/__init__.py": "",

    "Backend/config/settings.py": """
from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = "django-insecure-change-this-key"
DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR.parent / "Frontend" / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {
        "context_processors": [
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
        ],
    },
}]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DB_NAME", "sales_inventory"),
        "USER": os.getenv("DB_USER", "root"),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "3306"),
    }
}

AUTH_PASSWORD_VALIDATORS = []
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR.parent / "Frontend" / "static"]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
""",

    "Backend/config/urls.py": """
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", include("core.urls")),
]
""",

    "Backend/config/wsgi.py": """
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
application = get_wsgi_application()
""",

    "Backend/config/asgi.py": """
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
application = get_asgi_application()
""",

    "Backend/core/__init__.py": "",

    "Backend/core/apps.py": """
from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
""",

    "Backend/core/models.py": """
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    def __str__(self):
        return self.name


class Customer(models.Model):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=150)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    sku = models.CharField(max_length=50, unique=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_quantity = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=5)

    def __str__(self):
        return self.name


class Sale(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    sale_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
""",

    "Backend/core/admin.py": """
from django.contrib import admin
from .models import Category, Supplier, Customer, Product, Sale, SaleItem

admin.site.register(Category)
admin.site.register(Supplier)
admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Sale)
admin.site.register(SaleItem)
""",

    "Backend/core/urls.py": """
from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("products/", views.products, name="products"),
    path("products/add/", views.add_product, name="add_product"),
]
""",

    "Backend/core/views.py": """
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Sale

@login_required
def dashboard(request):
    context = {
        "product_count": Product.objects.count(),
        "sale_count": Sale.objects.count(),
        "low_stock": Product.objects.filter(stock_quantity__lte=5),
    }
    return render(request, "dashboard.html", context)


@login_required
def products(request):
    items = Product.objects.all().order_by("name")
    return render(request, "products.html", {"products": items})


@login_required
def add_product(request):
    if request.method == "POST":
        try:
            Product.objects.create(
                name=request.POST["name"],
                sku=request.POST["sku"],
                purchase_price=request.POST["purchase_price"],
                selling_price=request.POST["selling_price"],
                stock_quantity=request.POST["stock_quantity"],
            )
            messages.success(request, "Product added successfully.")
            return redirect("products")
        except Exception as error:
            messages.error(request, str(error))

    return render(request, "product_form.html")
""",

    "Frontend/templates/base.html": """
{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sales & Inventory Management</title>
    <link rel="stylesheet" href="{% static 'css/style.css' %}">
</head>
<body>
    <header>
        <h2>Sales & Inventory Management</h2>
        {% if user.is_authenticated %}
        <nav>
            <a href="{% url 'dashboard' %}">Dashboard</a>
            <a href="{% url 'products' %}">Products</a>
            <form method="post" action="{% url 'logout' %}">
                {% csrf_token %}
                <button type="submit">Logout</button>
            </form>
        </nav>
        {% endif %}
    </header>

    <main>
        {% for message in messages %}
            <p>{{ message }}</p>
        {% endfor %}
        {% block content %}{% endblock %}
    </main>

    <script src="{% static 'js/app.js' %}"></script>
</body>
</html>
""",

    "Frontend/templates/login.html": """
{% extends 'base.html' %}
{% block content %}
<div class="form-container">
    <h2>Login</h2>
    <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit">Login</button>
    </form>
</div>
{% endblock %}
""",

    "Frontend/templates/dashboard.html": """
{% extends 'base.html' %}
{% block content %}
<h1>Dashboard</h1>
<div class="cards">
    <div class="card">
        <h3>Total Products</h3>
        <p>{{ product_count }}</p>
    </div>
    <div class="card">
        <h3>Total Sales</h3>
        <p>{{ sale_count }}</p>
    </div>
</div>

<h2>Low Stock Products</h2>
<ul>
{% for product in low_stock %}
    <li>{{ product.name }} - {{ product.stock_quantity }}</li>
{% empty %}
    <li>No low-stock products.</li>
{% endfor %}
</ul>
{% endblock %}
""",

    "Frontend/templates/products.html": """
{% extends 'base.html' %}
{% block content %}
<h1>Products</h1>
<a class="button" href="{% url 'add_product' %}">Add Product</a>

<table>
    <tr>
        <th>Name</th>
        <th>SKU</th>
        <th>Purchase Price</th>
        <th>Selling Price</th>
        <th>Stock</th>
    </tr>
    {% for product in products %}
    <tr>
        <td>{{ product.name }}</td>
        <td>{{ product.sku }}</td>
        <td>{{ product.purchase_price }}</td>
        <td>{{ product.selling_price }}</td>
        <td>{{ product.stock_quantity }}</td>
    </tr>
    {% empty %}
    <tr><td colspan="5">No products found.</td></tr>
    {% endfor %}
</table>
{% endblock %}
""",

    "Frontend/templates/product_form.html": """
{% extends 'base.html' %}
{% block content %}
<h1>Add Product</h1>
<form method="post" class="form-container">
    {% csrf_token %}
    <label>Product Name</label>
    <input type="text" name="name" required>

    <label>SKU</label>
    <input type="text" name="sku" required>

    <label>Purchase Price</label>
    <input type="number" step="0.01" name="purchase_price" required>

    <label>Selling Price</label>
    <input type="number" step="0.01" name="selling_price" required>

    <label>Stock Quantity</label>
    <input type="number" name="stock_quantity" required>

    <button type="submit">Save Product</button>
</form>
{% endblock %}
""",

    "Frontend/static/css/style.css": """
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #f4f6f9;
    color: #222;
}

header {
    background: #172554;
    color: white;
    padding: 18px 30px;
}

header h2 {
    margin: 0 0 12px;
}

nav {
    display: flex;
    align-items: center;
    gap: 20px;
}

nav a {
    color: white;
    text-decoration: none;
}

nav form {
    margin: 0;
}

main {
    padding: 30px;
}

.cards {
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
}

.card, .form-container {
    background: white;
    padding: 22px;
    border-radius: 8px;
    box-shadow: 0 2px 8px #0001;
}

.card {
    min-width: 180px;
}

.card p {
    font-size: 28px;
    font-weight: bold;
}

.form-container {
    max-width: 450px;
}

label, input {
    display: block;
    width: 100%;
    margin: 10px 0;
}

input {
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 5px;
}

button, .button {
    background: #2563eb;
    color: white;
    border: 0;
    padding: 10px 16px;
    border-radius: 5px;
    cursor: pointer;
    text-decoration: none;
}

table {
    width: 100%;
    border-collapse: collapse;
    background: white;
    margin-top: 20px;
}

th, td {
    padding: 12px;
    border: 1px solid #ddd;
    text-align: left;
}
""",

    "Frontend/static/js/app.js": """
document.addEventListener("DOMContentLoaded", function () {
    console.log("Sales and Inventory Management loaded.");
});
""",

    "Database/schema.sql": """
CREATE DATABASE IF NOT EXISTS sales_inventory;
USE sales_inventory;

-- Django will create the application tables through migrations.
""",

    "Database/sample_data.sql": """
USE sales_inventory;

-- Add sample records after Django migrations have created the tables.
""",

    "Database/database_documentation.md": """
# Database

Database: MySQL

Database name: sales_inventory

Tables are created and managed by Django migrations:
- core_category
- core_supplier
- core_customer
- core_product
- core_sale
- core_saleitem
"""
}


FOLDERS = [
    "Frontend/templates/accounts",
    "Frontend/templates/categories",
    "Frontend/templates/customers",
    "Frontend/templates/inventory",
    "Frontend/templates/invoices",
    "Frontend/templates/products",
    "Frontend/templates/reports",
    "Frontend/templates/sales",
    "Frontend/templates/suppliers",
    "Frontend/static/images",
    "Backend/accounts",
    "Backend/products",
    "Backend/categories",
    "Backend/suppliers",
    "Backend/customers",
    "Backend/inventory",
    "Backend/sales",
    "Backend/reports",
]

for folder in FOLDERS:
    (ROOT / folder).mkdir(parents=True, exist_ok=True)

for file_path, content in FILES.items():
    full_path = ROOT / file_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content.strip() + "\n", encoding="utf-8")
    print("Created:", file_path)

env_file = ROOT / "Backend/.env"
example_file = ROOT / "Backend/.env.example"

if not env_file.exists():
    env_file.write_text(
        example_file.read_text(encoding="utf-8"),
        encoding="utf-8"
    )
    print("Created: Backend/.env")

print("\\nProject files created successfully!")
