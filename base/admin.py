from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db import models
from base.models import Item, Category, Tag, User, Profile, Order
from .forms import UserCreationForm
from django.contrib.auth.models import Group

# from django.contrib.admin.options import InlineModelAdmin

# from django.db import models


class TagInline(admin.TabularInline):  # type: ignore
    model = Item.tags.through


class ItemAdmin(admin.ModelAdmin[Tag]):
    inlines = [TagInline]
    exclude = ["tags"]


class ProfileInline(admin.StackedInline[models.Model, models.Model]):
    model = Profile
    can_delete = False


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "username",
                    "email",
                    "password",
                )
            },
        ),
        (
            None,
            {
                "fields": (
                    "is_active",
                    "is_admin",
                )
            },
        ),
    )

    list_display = (
        "username",
        "email",
        "is_active",
    )
    list_filter = ()
    ordering = ()
    filter_horizontal = ()

    add_fieldsets = (
        (
            None,
            {
                "fields": (
                    "username",
                    "email",
                    "is_active",
                )
            },
        ),
    )

    add_form = UserCreationForm

    inlines = (ProfileInline,)


# 商品管理用のモデルを管理画面に追加
admin.site.register(Item)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Order)
admin.site.register(User, CustomUserAdmin)

# デフォルトで設定されているGroup モデルを非表示
admin.site.unregister(Group)
