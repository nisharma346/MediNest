from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render

from .models import Article, ArticleCategory


def article_list(request):
    categories = ArticleCategory.objects.filter(is_active=True).annotate(
        article_count=Count('articles', filter=Q(articles__is_published=True))
    ).order_by("name")

    search_query = request.GET.get("q", "").strip()
    selected_category = request.GET.get("category", "")

    selected_category_obj = None
    if selected_category:
        selected_category_obj = categories.filter(slug=selected_category).first()

    articles = Article.objects.filter(is_published=True).select_related("category")

    if search_query:
        articles = articles.filter(
            Q(title__icontains=search_query)
            | Q(short_description__icontains=search_query)
            | Q(content__icontains=search_query)
        )

    if selected_category:
        articles = articles.filter(category__slug=selected_category)

    articles = articles.order_by("-published_date", "-created_at")

    featured_articles = Article.objects.filter(
        is_published=True,
        is_featured=True,
    ).order_by("-published_date", "-created_at")[:3]

    context = {
        "articles": articles,
        "featured_articles": featured_articles,
        "categories": categories,
        "selected_category": selected_category,
        "selected_category_obj": selected_category_obj,
        "search_query": search_query,
        "total_articles_count": articles.count(),
    }
    return render(request, "blog/article_list.html", context)


def article_detail(request, slug):
    article = get_object_or_404(
        Article,
        slug=slug,
        is_published=True,
    )

    related_articles = Article.objects.filter(
        is_published=True,
        category=article.category,
    ).exclude(pk=article.pk).order_by("-published_date", "-created_at")[:4]

    context = {
        "article": article,
        "related_articles": related_articles,
    }
    return render(request, "blog/article_detail.html", context)
