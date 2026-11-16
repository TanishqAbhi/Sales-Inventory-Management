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
