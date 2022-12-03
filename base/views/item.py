from django.shortcuts import render  # noqa
from django.views.generic import ListView, DetailView
from base.models import Item, Category, Tag


class IndexListView(ListView[Item]):
    model = Item
    template_name = "pages/index.html"

    # ListView には Pagination 機能が付属している
    # paginate_by で 1ページの表示件数を指定できる
    paginate_by = 20

    queryset = Item.objects.filter(is_published=True)


class ItemDetailView(DetailView[Item]):
    model = Item
    template_name: str = "pages/item.html"


# 指定のカテゴリーが設定されている商品の一覧を表示する
class CategoryListView(ListView[Item]):
    model = Item
    template_name = "pages/item_list.html"

    # ListView には Pagination 機能が付属している
    # paginate_by で 1ページの表示件数を指定できる
    paginate_by = 20

    def get_queryset(self):
        self.category = Category.objects.get(slug=self.kwargs["pk"])
        return Item.objects.filter(is_published=True, category=self.category)

    # template で参照する変数に、title 情報を追加
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Category #{self.category.name}"
        return context


# 指定のタグが設定されている商品の一覧を表示する
class TagListView(ListView[Item]):
    model = Item
    template_name = "pages/item_list.html"

    # ListView には Pagination 機能が付属している
    # paginate_by で 1ページの表示件数を指定できる
    paginate_by = 20

    def get_queryset(self):
        self.tag = Tag.objects.get(slug=self.kwargs["pk"])
        return Item.objects.filter(is_published=True, tags=self.tag)

    # template で参照する変数に、title 情報を追加
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Tag #{self.tag.name}"
        return context
