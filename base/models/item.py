from django.db import models
import uuid
import os


def upload_image_to(instance: "Item", filename):
    item_id = (instance.id,)
    return os.path.join("static", f"items/{item_id}/{filename}")


class Item(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(default="", max_length=50)
    price = models.PositiveIntegerField(default=0)
    stock = models.PositiveIntegerField(default=0)
    description = models.TextField(default="", blank=True)
    sold_count = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=False)
    image = models.ImageField(default="", blank=True, upload_to=upload_image_to)
    category = models.ForeignKey("Category", on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField("Tag")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name


class Category(models.Model):
    slug = models.CharField(max_length=32, primary_key=True)
    name = models.CharField(max_length=32)

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    slug = models.CharField(max_length=32, primary_key=True)
    name = models.CharField(max_length=32)

    def __str__(self) -> str:
        return self.name
