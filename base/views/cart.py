from django.shortcuts import redirect
from django.conf import settings
from django.views.generic import View, ListView
from django.db.models.query import QuerySet
from base.models import Item
from collections import OrderedDict


class CartListView(ListView[Item]):
    model = Item
    template_name = "pages/cart.html"

    # テンプレートに渡すリストデータを作成する処理
    def get_queryset(self) -> "QuerySet[Item]":
        cart = self.request.session.get("cart", None)
        if cart is None or len(cart) == 0:
            # カートに商品が入っていなければ、トップページに戻る
            return redirect("/")
        self.queryset = []
        self.total = 0

        # self.queryset に、Session の中身を詰めていく
        for item_pk, quantity in cart["items"].items():
            obj = Item.objects.get(pk=item_pk)
            obj.quantity = quantity
            obj.subtotal = int(obj.price * quantity)
            self.queryset.append(obj)
            self.total += obj.subtotal

        # 消費税額の計算
        self.tax_included_total = int(self.total * (settings.TAX_RATE + 1))
        cart["total"] = self.total
        cart["tax_included_total"] = self.tax_included_total
        self.request.session["cart"] = cart
        return super().get_queryset()

    # テンプレートが受け取るコンテキストデータを作成する処理
    # 一覧表示するデータ(object_list) はget_queryset() で作るので、それ以外のものを処理する
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["total"] = self.total
            context["tax_included_total"] = self.tax_included_total
        except Exception:
            pass
        return context


class AddCartView(View):
    def post(self, request):
        item_pk = request.POST.get("item_pk")
        quantity = int(request.POST.get("quantity"))

        # Session にカート内の商品情報を保持する
        cart = request.session.get("cart", None)

        # カートが空の場合、OrderedDict で初期化する
        # uuid をキー、購入する数量を値に持つDictデータ
        if cart is None or len(cart) == 0:
            items: OrderedDict[str, int] = OrderedDict()
            cart = {"items": items}

        if item_pk in cart["items"]:
            cart["items"][item_pk] += quantity
        else:
            cart["items"][item_pk] = quantity
        request.session["cart"] = cart
        return redirect("/cart")


# カートから商品を削除する
def remove_from_cart(request, pk):
    cart = request.session.get("cart", None)
    if cart is not None:
        del cart["items"][pk]
        request.session["cart"] = cart
    return redirect("/cart/")
