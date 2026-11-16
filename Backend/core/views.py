
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction

from .models import Product, Sale, SaleItem, Customer


@login_required
def dashboard(request):
    context = {
        "product_count": Product.objects.count(),
        "sale_count": Sale.objects.count(),
        "low_stock": Product.objects.filter(
            stock_quantity__lte=5
        ),
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


# SALES HISTORY
@login_required
def sales_list(request):
    sales = Sale.objects.select_related(
        "customer"
    ).order_by("-sale_date")

    return render(
        request,
        "sales_list.html",
        {"sales": sales}
    )


# CREATE SALE
@login_required
def create_sale(request):
    products = Product.objects.all().order_by("name")
    customers = Customer.objects.all().order_by("name")

    if request.method == "POST":
        try:
            with transaction.atomic():

                product = Product.objects.select_for_update().get(
                    pk=request.POST.get("product")
                )

                quantity = int(request.POST.get("quantity", 0))

                if quantity <= 0:
                    raise ValueError("Quantity must be greater than zero.")

                if product.stock_quantity < quantity:
                    raise ValueError(
                        f"Only {product.stock_quantity} units are available."
                    )

                customer_id = request.POST.get("customer")

                customer = None
                if customer_id:
                    customer = Customer.objects.get(pk=customer_id)

                total = product.selling_price * quantity

                sale = Sale.objects.create(
                    customer=customer,
                    total_amount=total
                )

                SaleItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=quantity,
                    unit_price=product.selling_price
                )

                product.stock_quantity -= quantity
                product.save(update_fields=["stock_quantity"])

            messages.success(request, "Sale completed successfully.")

            return redirect("invoice_detail", pk=sale.pk)

        except (Product.DoesNotExist, Customer.DoesNotExist):
            messages.error(request, "Selected product or customer was not found.")

        except (ValueError, TypeError) as error:
            messages.error(request, str(error))

    return render(
        request,
        "sale_form.html",
        {
            "products": products,
            "customers": customers
        }
    )


# INVOICE DETAILS
@login_required
def invoice_detail(request, pk):
    sale = get_object_or_404(
        Sale.objects.prefetch_related("items__product"),
        pk=pk
    )

    return render(
        request,
        "invoice_detail.html",
        {"sale": sale}
    )
