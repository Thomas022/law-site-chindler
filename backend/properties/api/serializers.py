from rest_framework import serializers

from properties.models import Property, PropertyImage


class PublicPropertyImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = PropertyImage
        fields = ("url", "alt_text", "order", "is_cover", "width", "height")

    def get_url(self, image):
        if not image.image:
            return None
        url = image.image.url
        request = self.context.get("request")
        return request.build_absolute_uri(url) if request and url.startswith("/") else url


class PublicPropertySerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="public_id", read_only=True)
    purpose_label = serializers.CharField(source="get_purpose_display", read_only=True)
    property_type_label = serializers.CharField(
        source="get_property_type_display", read_only=True
    )
    price = serializers.SerializerMethodField()
    price_display = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    map = serializers.SerializerMethodField()
    images = PublicPropertyImageSerializer(many=True, read_only=True)

    class Meta:
        model = Property
        fields = (
            "id",
            "title",
            "description",
            "purpose",
            "purpose_label",
            "property_type",
            "property_type_label",
            "price",
            "price_display",
            "condominium_fee",
            "total_area",
            "bedrooms",
            "suites",
            "bathrooms",
            "parking_spaces",
            "address",
            "map",
            "is_featured",
            "images",
        )

    def get_price(self, property):
        return property.price if property.show_price else None

    def get_price_display(self, property):
        if not property.show_price:
            return "Sob consulta"
        value = f"{property.price:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
        return f"R$ {value}"

    def get_address(self, property):
        address = {
            "neighborhood": property.neighborhood,
            "city": property.city,
            "state": property.state,
            "display": property.public_address,
        }
        if property.address_visibility == Property.AddressVisibility.FULL:
            address.update(
                {
                    "street": property.street,
                    "number": property.number,
                    "complement": property.complement,
                    "postal_code": property.postal_code,
                }
            )
        return address

    def get_map(self, property):
        if property.map_visibility != Property.MapVisibility.APPROXIMATE:
            return {"visible": False}
        return {
            "visible": True,
            "latitude": property.public_latitude,
            "longitude": property.public_longitude,
            "precision": "approximate",
        }

