from decimal import Decimal, InvalidOperation

from django.db.models import Q
from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from properties.models import Property

from .pagination import PropertyPagination
from .serializers import PublicPropertySerializer


def public_properties():
    return (
        Property.objects.filter(
            status=Property.Status.PUBLISHED,
            deleted_at__isnull=True,
        )
        .prefetch_related("images")
    )


def parse_non_negative_integer(params, name):
    value = params.get(name)
    if value in (None, ""):
        return None
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise ValidationError({name: "Informe um número inteiro válido."})
    if parsed < 0:
        raise ValidationError({name: "O valor não pode ser negativo."})
    return parsed


def parse_non_negative_decimal(params, name):
    value = params.get(name)
    if value in (None, ""):
        return None
    try:
        parsed = Decimal(value)
    except (InvalidOperation, TypeError):
        raise ValidationError({name: "Informe um valor numérico válido."})
    if parsed < 0:
        raise ValidationError({name: "O valor não pode ser negativo."})
    return parsed


class PublicPropertyListView(generics.ListAPIView):
    serializer_class = PublicPropertySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = PropertyPagination

    def get_queryset(self):
        queryset = public_properties()
        params = self.request.query_params

        purpose = params.get("purpose")
        if purpose:
            if purpose not in Property.Purpose.values:
                raise ValidationError({"purpose": "Finalidade inválida."})
            queryset = queryset.filter(purpose=purpose)

        property_type = params.get("property_type")
        if property_type:
            if property_type not in Property.PropertyType.values:
                raise ValidationError({"property_type": "Tipo de imóvel inválido."})
            queryset = queryset.filter(property_type=property_type)

        for field in ("city", "neighborhood"):
            value = params.get(field)
            if value:
                queryset = queryset.filter(**{f"{field}__iexact": value.strip()})

        bedrooms = parse_non_negative_integer(params, "bedrooms")
        if bedrooms is not None:
            queryset = queryset.filter(bedrooms__gte=bedrooms)

        parking_spaces = parse_non_negative_integer(params, "parking_spaces")
        if parking_spaces is not None:
            queryset = queryset.filter(parking_spaces__gte=parking_spaces)

        minimum = parse_non_negative_decimal(params, "min_price")
        maximum = parse_non_negative_decimal(params, "max_price")
        if minimum is not None:
            queryset = queryset.filter(price__gte=minimum)
        if maximum is not None:
            queryset = queryset.filter(price__lte=maximum)
        if minimum is not None and maximum is not None and minimum > maximum:
            raise ValidationError({"max_price": "Deve ser maior ou igual ao preço mínimo."})

        featured = params.get("featured")
        if featured:
            if featured.lower() not in ("true", "false"):
                raise ValidationError({"featured": "Use true ou false."})
            queryset = queryset.filter(is_featured=featured.lower() == "true")

        search = params.get("search", "").strip()
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search)
                | Q(neighborhood__icontains=search)
                | Q(city__icontains=search)
            )

        orderings = {
            "featured": ("-is_featured", "featured_order", "-published_at"),
            "newest": ("-published_at",),
            "price_asc": ("price",),
            "price_desc": ("-price",),
        }
        ordering = params.get("ordering", "featured")
        if ordering not in orderings:
            raise ValidationError({"ordering": "Ordenação inválida."})
        return queryset.order_by(*orderings[ordering])


class PublicPropertyDetailView(generics.RetrieveAPIView):
    serializer_class = PublicPropertySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "public_id"
    lookup_url_kwarg = "property_id"

    def get_queryset(self):
        return public_properties()


class PropertyFilterOptionsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, _request):
        queryset = public_properties()
        return Response(
            {
                "purposes": [
                    {"value": value, "label": label}
                    for value, label in Property.Purpose.choices
                ],
                "property_types": [
                    {"value": value, "label": label}
                    for value, label in Property.PropertyType.choices
                ],
                "cities": list(
                    queryset.order_by("city").values_list("city", flat=True).distinct()
                ),
                "neighborhoods": list(
                    queryset.order_by("neighborhood")
                    .values_list("neighborhood", flat=True)
                    .distinct()
                ),
            }
        )

