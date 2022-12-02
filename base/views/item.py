from django.shortcuts import render  # noqa
from django.views.generic import ListView
from base.models import Item


class IndexListView(ListView[Item]):
    model = Item
    template_name = "pages/index.html"
