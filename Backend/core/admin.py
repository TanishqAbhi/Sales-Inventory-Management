from django.contrib import admin
from .models import Category, Supplier, Customer, Product, Sale, SaleItem

admin.site.register(Category)
admin.site.register(Supplier)
admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Sale)
admin.site.register(SaleItem)
