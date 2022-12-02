from django.shortcuts import render  # noqa
from django.views.generic import ListView, DetailView
from base.models import Item


class IndexListView(ListView[Item]):
    model = Item
    template_name = "pages/index.html"


class ItemDetailView(DetailView[Item]):
    model = Item
    template_name: str = "pages/item.html"
