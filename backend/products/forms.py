from django import forms
from .models import ProductReview


class ProductReviewForm(forms.ModelForm):
    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        widget=forms.HiddenInput(),
        error_messages={
            'required': 'Please select a rating between 1 and 5 stars.',
            'min_value': 'Rating must be at least 1 star.',
            'max_value': 'Rating cannot exceed 5 stars.'
        }
    )
    review_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Write your detailed review here...',
            'required': 'required'
        }),
        required=True,
        error_messages={
            'required': 'Please enter your review text.'
        }
    )

    class Meta:
        model = ProductReview
        fields = ['rating', 'review_text']
