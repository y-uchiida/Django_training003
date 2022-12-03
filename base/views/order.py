from django.views.generic import ListView, DetailView
from base.models import Order
import json
from django.contrib.auth.mixins import LoginRequiredMixin


class OrderIndexView(LoginRequiredMixin, ListView[Order]):
    model = Order
    template_name = "pages/orders.html"
    ordering = "-created_at"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user.id)  # type: ignore


class OrderDetailView(LoginRequiredMixin, DetailView[Order]):
    model = Order
    template_name = "pages/order.html"

    # get_querysetメソッドの追記
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)  # type: ignore

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        # json to dict
        context["items"] = json.loads(obj.items)
        context["shipping"] = json.loads(obj.shipping)
        return context
