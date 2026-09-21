from django.urls import path
from .views import product_list, product_detail, add_or_edit_review, delete_review

app_name = "products"

urlpatterns = [
    path("", product_list, name="product_list"),
    path("review/<int:review_id>/delete/", delete_review, name="delete_review"),
    path("<slug:slug>/", product_detail, name="product_detail"),
    path("<slug:slug>/review/", add_or_edit_review, name="add_or_edit_review"),
]

