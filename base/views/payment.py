from django.shortcuts import redirect
from django.views.generic import View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.conf import settings
from django.core import serializers
from base.models import Item, Order
import stripe
import json

stripe.api_key = settings.STRIPE_API_SECRET_KEY


# 決済が成功したときの処理
class PaySuccessView(LoginRequiredMixin, TemplateView):
    template_name = "pages/success.html"

    def get(self, request, *args, **kwargs):
        # checkout_sessionで渡したクエリを取得
        order_id = request.GET.get("order_id")

        # idと現userでOrderオブジェクトのリストを取得
        orders = Order.objects.filter(user=request.user, id=order_id)

        # もし要素数が1でなければ、注文情報がない状態でアクセスしているので想定外の操作
        if len(orders) != 1:
            messages.error(self.request, "処理できない決済が試行されました。")
            return redirect("/cart/")

        # １つの要素を変数へ代入
        order = orders[0]

        # 既にis_confirmed=Trueなら以降に進まないようにここでreturn
        if order.is_confirmed:
            messages.error(self.request, "処理できない決済が試行されました。")
            return redirect("/cart/")

        order.is_confirmed = True  # 注文確定
        order.save()

        # カート情報削除
        if "cart" in request.session:
            del request.session["cart"]

        # 注文処理が完了したので、カートを空に戻す
        del request.session["cart"]

        return super().get(request, *args, **kwargs)


# 決済がキャンセルされたときの処理
class PayCancelView(LoginRequiredMixin, TemplateView):
    template_name = "pages/cancel.html"

    def get(self, request, *args, **kwargs):
        # ログイン中のユーザーの仮注文のリストを取得
        orders = Order.objects.filter(user=request.user, is_confirmed=False)

        for order in orders:
            # 在庫数と販売数を元の状態に戻す
            for elem in json.loads(order.items):
                item = Item.objects.get(pk=elem["pk"])
                item.sold_count -= elem["quantity"]
                item.stock += elem["quantity"]
                item.save()

        # 仮注文のレコードを全て削除
        orders.delete()

        return super().get(request, *args, **kwargs)


tax_rate = stripe.TaxRate.create(
    display_name="消費税",
    description="消費税",
    country="JP",
    jurisdiction="JP",
    percentage=settings.TAX_RATE * 100,
    inclusive=False,  # 外税を指定（内税の場合はTrue）
)


# 決済実行の際のSessionに入れる商品情報を作成する処理
def create_line_item(unit_amount, name, quantity):
    return {
        "price_data": {
            "currency": "JPY",
            "unit_amount": unit_amount,
            "product_data": {
                "name": name,
            },
        },
        "quantity": quantity,
        "tax_rates": [tax_rate.id],
    }


def check_profile_filled(profile) -> bool:
    if profile.name is None or profile.name == "":
        return False
    elif profile.zipcode is None or profile.zipcode == "":
        return False
    elif profile.prefecture is None or profile.prefecture == "":
        return False
    elif profile.city is None or profile.city == "":
        return False
    elif profile.address1 is None or profile.address1 == "":
        return False
    return True


# Stripe パッケージの機能を利用して、決済を処理する
class PayWithStripe(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):

        # プロフィールが埋まっているかどうか確認
        if not check_profile_filled(request.user.profile):
            messages.error(self.request, "商品配送のため、プロフィールを入力してください。")
            return redirect("/profile/")

        cart = request.session.get("cart", None)
        if cart is None or len(cart) == 0:
            messages.error(self.request, "カートが空です。")
            return redirect("/")

        # Order オブジェクトに保持するJSONデータ
        ordered_items = []

        # Stripe で処理するオブジェクトデータ
        line_items = []

        for item_pk, quantity in cart["items"].items():
            item = Item.objects.get(pk=item_pk)
            line_item = create_line_item(item.price, item.name, quantity)  # type: ignore
            line_items.append(line_item)

            # Order モデルのitems フィールドに持たせるJSONデータ用
            ordered_items.append(
                {
                    "pk": str(item.pk),
                    "name": item.name,
                    "image": str(item.image),
                    "price": item.price,
                    "quantity": quantity,
                }
            )

            # 注文数超過を防ぐため、在庫をこの時点で引いておく
            # また、在庫数の不整合が起きないように販売数も加算しておく
            # 注文キャンセルの場合は在庫と販売数を戻す
            item.stock -= quantity
            item.sold_count += quantity
            item.save()

        # 仮注文情報として、Order レコードを作成
        # 決済が完了していないので、is_confirmed は False にしておく
        order = Order.objects.create(
            user=request.user,
            uid=request.user.pk,
            items=json.dumps(ordered_items),
            shipping=serializers.serialize("json", [request.user.profile]),
            amount=cart["total"],
            tax_included=cart["tax_included_total"],
        )

        checkout_session = stripe.checkout.Session.create(
            customer_email=request.user.email,
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            # success_urlとcancel_urlには、クエリで注文IDを渡しておく
            success_url=f"{settings.MY_URL}/pay/success/?order_id={order.pk}",
            cancel_url=f"{settings.MY_URL}/pay/cancel/",
        )
        return redirect(checkout_session.url)
