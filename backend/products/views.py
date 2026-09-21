from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, F, ExpressionWrapper, DecimalField
from django.core.paginator import Paginator

from wishlist.models import WishlistItem
from orders.models import OrderItem
from .models import Product, Category, ProductReview
from .forms import ProductReviewForm



def product_list(request):
    # Base queryset - active products only
    queryset = Product.objects.filter(is_active=True).select_related("category")

    # Annotate discounted price for exact price filtering and sorting
    discounted_expr = ExpressionWrapper(
        F("price") * (1.0 - F("discount_percentage") / 100.0),
        output_field=DecimalField(max_digits=10, decimal_places=2)
    )
    queryset = queryset.annotate(discounted_price_val=discounted_expr)

    # 1. Search filter
    search_query = request.GET.get("search", "").strip()
    if search_query:
        queryset = queryset.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )

    # 2. Category filter
    category_slug = request.GET.get("category", "").strip()
    if category_slug:
        queryset = queryset.filter(category__slug=category_slug)

    # 3. Price filter (min_price & max_price)
    min_price = request.GET.get("min_price", "").strip()
    max_price = request.GET.get("max_price", "").strip()
    if min_price:
        try:
            min_val = float(min_price)
            queryset = queryset.filter(discounted_price_val__gte=min_val)
        except ValueError:
            pass

    if max_price:
        try:
            max_val = float(max_price)
            queryset = queryset.filter(discounted_price_val__lte=max_val)
        except ValueError:
            pass

    # 4. Discount filter ("sale")
    discount_filter = request.GET.get("discount", "").strip()
    if discount_filter == "sale":
        queryset = queryset.filter(discount_percentage__gt=0)

    # 5. Stock filter ("in_stock")
    in_stock = request.GET.get("in_stock", "").strip()
    if in_stock in ["true", "1", "on"]:
        queryset = queryset.filter(stock__gt=0)

    # 6. Sorting
    sort_by = request.GET.get("sort", "newest").strip()
    if sort_by == "price_low":
        queryset = queryset.order_by("discounted_price_val", "price")
    elif sort_by == "price_high":
        queryset = queryset.order_by("-discounted_price_val", "-price")
    elif sort_by == "name_asc":
        queryset = queryset.order_by("name")
    elif sort_by == "name_desc":
        queryset = queryset.order_by("-name")
    else:  # newest / default
        queryset = queryset.order_by("-created_at")

    # Dynamic total count before pagination
    total_count = queryset.count()

    # Pagination (6 products per page)
    paginator = Paginator(queryset, 6)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    # Wishlist IDs for logged-in users
    wishlist_ids = set()
    if request.user.is_authenticated:
        wishlist_ids = set(
            WishlistItem.objects.filter(user=request.user).values_list("product_id", flat=True)
        )

    # Fetch all active categories for filter dropdown/sidebar
    categories = Category.objects.filter(is_active=True).order_by("name")

    # Prepare QueryString for pagination links preserving active filters
    query_params = request.GET.copy()
    if "page" in query_params:
        query_params.pop("page")
    querystring = query_params.urlencode()

    return render(
        request,
        "products/product_list.html",
        {
            "products": page_obj,
            "page_obj": page_obj,
            "total_count": total_count,
            "categories": categories,
            "wishlist_ids": wishlist_ids,
            "search_query": search_query,
            "selected_category": category_slug,
            "min_price": min_price,
            "max_price": max_price,
            "discount_filter": discount_filter,
            "in_stock": in_stock,
            "sort_by": sort_by,
            "querystring": querystring,
        }
    )



def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)

    in_wishlist = False
    has_purchased = False
    user_review = None

    if request.user.is_authenticated:
        in_wishlist = WishlistItem.objects.filter(user=request.user, product=product).exists()
        has_purchased = OrderItem.objects.filter(
            order__user=request.user,
            product=product
        ).exclude(order__status="cancelled").exists()
        user_review = ProductReview.objects.filter(product=product, user=request.user).first()

    approved_reviews = product.approved_reviews.select_related("user")
    rating_breakdown = product.rating_breakdown
    review_form = ProductReviewForm(instance=user_review) if user_review else ProductReviewForm()

    return render(
        request,
        "products/product_detail.html",
        {
            "product": product,
            "in_wishlist": in_wishlist,
            "has_purchased": has_purchased,
            "user_review": user_review,
            "approved_reviews": approved_reviews,
            "rating_breakdown": rating_breakdown,
            "review_form": review_form,
        }
    )


@login_required
def add_or_edit_review(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)

    has_purchased = OrderItem.objects.filter(
        order__user=request.user,
        product=product
    ).exclude(order__status="cancelled").exists()

    if not has_purchased:
        messages.error(request, "You can review this product after purchasing it.")
        return redirect("products:product_detail", slug=slug)

    user_review = ProductReview.objects.filter(product=product, user=request.user).first()

    if request.method == "POST":
        form = ProductReviewForm(request.POST, instance=user_review)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.is_approved = True
            review.save()

            if user_review:
                messages.success(request, "Your review has been updated successfully!")
            else:
                messages.success(request, "Thank you! Your review has been submitted successfully.")
        else:
            messages.error(request, "Please enter a valid rating (1 to 5 stars) and review text.")

    return redirect("products:product_detail", slug=slug)


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(ProductReview, id=review_id, user=request.user)
    product_slug = review.product.slug
    review.delete()
    messages.success(request, "Your review has been removed.")
    return redirect("products:product_detail", slug=product_slug)

