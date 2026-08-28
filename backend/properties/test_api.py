from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .models import Property, PropertyImage


class PublicPropertyAPITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="editor_api", password="not-used-in-api-tests"
        )
        cls.published = cls.make_property(
            title="Apartamento em Ipanema",
            neighborhood="Ipanema",
            price=Decimal("2000000.00"),
            status=Property.Status.PUBLISHED,
        )
        PropertyImage.objects.create(
            property=cls.published,
            image="properties/test/cover.jpg",
            alt_text="Sala do apartamento",
            order=0,
            is_cover=True,
        )
        cls.draft = cls.make_property(
            title="Imóvel ainda em edição",
            neighborhood="Leblon",
            status=Property.Status.DRAFT,
        )

    @classmethod
    def make_property(cls, **overrides):
        values = {
            "title": "Imóvel de teste",
            "description": "Descrição pública do imóvel",
            "purpose": Property.Purpose.SALE,
            "property_type": Property.PropertyType.APARTMENT,
            "status": Property.Status.PUBLISHED,
            "price": Decimal("750000.00"),
            "show_price": True,
            "total_area": Decimal("90.00"),
            "bedrooms": 2,
            "bathrooms": 2,
            "parking_spaces": 1,
            "street": "Rua Visconde de Pirajá",
            "number": "100",
            "neighborhood": "Copacabana",
            "city": "Rio de Janeiro",
            "state": "RJ",
            "address_visibility": Property.AddressVisibility.NEIGHBORHOOD_CITY,
            "exact_latitude": Decimal("-22.983000"),
            "exact_longitude": Decimal("-43.204000"),
            "public_latitude": Decimal("-22.982000"),
            "public_longitude": Decimal("-43.205000"),
            "map_visibility": Property.MapVisibility.APPROXIMATE,
            "created_by": cls.user,
            "updated_by": cls.user,
        }
        values.update(overrides)
        return Property.objects.create(**values)

    def setUp(self):
        self.client = APIClient()

    def test_list_contains_only_published_properties(self):
        response = self.client.get(reverse("property-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], self.published.title)

    def test_public_payload_hides_private_data(self):
        response = self.client.get(
            reverse("property-detail", kwargs={"property_id": self.published.public_id})
        )
        payload = response.data
        self.assertNotIn("exact_latitude", payload)
        self.assertNotIn("exact_longitude", payload)
        self.assertNotIn("created_by", payload)
        self.assertNotIn("street", payload["address"])
        self.assertEqual(payload["map"]["precision"], "approximate")
        self.assertEqual(payload["images"][0]["alt_text"], "Sala do apartamento")

    def test_full_address_is_only_exposed_when_authorized_on_property(self):
        self.published.address_visibility = Property.AddressVisibility.FULL
        self.published.save(update_fields=["address_visibility"])
        response = self.client.get(
            reverse("property-detail", kwargs={"property_id": self.published.public_id})
        )
        self.assertEqual(response.data["address"]["street"], "Rua Visconde de Pirajá")

    def test_hidden_price_returns_consultation_message(self):
        self.published.show_price = False
        self.published.save(update_fields=["show_price"])
        response = self.client.get(reverse("property-list"))
        property_data = response.data["results"][0]
        self.assertIsNone(property_data["price"])
        self.assertEqual(property_data["price_display"], "Sob consulta")

    def test_filters_and_search(self):
        response = self.client.get(
            reverse("property-list"),
            {
                "purpose": "sale",
                "property_type": "apartment",
                "neighborhood": "IPANEMA",
                "bedrooms": "2",
                "min_price": "1000000",
                "search": "ipanema",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

    def test_invalid_filter_returns_400(self):
        response = self.client.get(reverse("property-list"), {"min_price": "abc"})
        self.assertEqual(response.status_code, 400)

    def test_draft_detail_is_not_public(self):
        response = self.client.get(
            reverse("property-detail", kwargs={"property_id": self.draft.public_id})
        )
        self.assertEqual(response.status_code, 404)

    def test_filter_options_use_only_public_properties(self):
        response = self.client.get(reverse("property-filters"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("Ipanema", response.data["neighborhoods"])
        self.assertNotIn("Leblon", response.data["neighborhoods"])

