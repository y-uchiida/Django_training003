from django.contrib import admin
from base.models import Item, Category, Tag
from django.contrib.auth.models import Group

# from django.contrib.admin.options import InlineModelAdmin

# from django.db import models


class TagInline(admin.TabularInline):  # type: ignore
    model = Item.tags.through


class ItemAdmin(admin.ModelAdmin[Tag]):
    inlines = [TagInline]
    exclude = ["tags"]


# 商品管理用のモデルを管理画面に追加
admin.site.register(Item)
admin.site.register(Category)
admin.site.register(Tag)

# デフォルトで設定されているGroup モデルを非表示
admin.site.unregister(Group)
