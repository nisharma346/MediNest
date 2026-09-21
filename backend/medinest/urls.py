from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import admin_dashboard

urlpatterns = [
    path("admin/", admin.site.urls),
    path("admin-dashboard/", admin_dashboard, name="admin_dashboard"),

    path("", include("core.urls")),
    path("products/", include("products.urls")),
    path("doctors/", include("doctors.urls")),
    path("appointments/", include("appointments.urls")),
    path("cart/", include("cart.urls")),
    path("wishlist/", include("wishlist.urls")),
    path("accounts/", include("accounts.urls")),
    path("orders/", include("orders.urls")),
    path("blog/", include("blog.urls")),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )