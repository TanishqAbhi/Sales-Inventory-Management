
from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),

    # Products
    path("products/", views.products, name="products"),
    path("products/add/", views.add_product, name="add_product"),

    # Sales
    path("sales/", views.sales_list, name="sales"),
    path("sales/create/", views.create_sale, name="create_sale"),
    path("sales/<int:pk>/", views.invoice_detail, name="invoice_detail"),
]
