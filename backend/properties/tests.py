from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import TestCase

from .models import Property, PropertyImage
from .roles import ADMINISTRATOR_GROUP, EDITOR_GROUP
from .services import (
    change_property_status,
    move_property_to_trash,
    restore_property,
)


class PropertyModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="editor", password="test-password"
        )

    def make_property(self, **overrides):
        data = {
            "title": "Apartamento em Ipanema",
            "description": "Imóvel amplo próximo à praia.",
            "purpose": Property.Purpose.SALE,
            "property_type": Property.PropertyType.APARTMENT,
            "price": Decimal("2500000.00"),
            "total_area": Decimal("120.00"),
            "street": "Rua Visconde de Pirajá",
            "number": "100",
            "neighborhood": "Ipanema",
            "city": "Rio de Janeiro",
            "created_by": self.user,
            "updated_by": self.user,
        }
        data.update(overrides)
        return Property.objects.create(**data)

    def test_public_address_respects_privacy_choice(self):
        property_item = self.make_property()
        self.assertEqual(property_item.public_address, "Ipanema, Rio de Janeiro")

        property_item.address_visibility = Property.AddressVisibility.FULL
        self.assertEqual(
            property_item.public_address,
            "Rua Visconde de Pirajá, 100, Ipanema, Rio de Janeiro",
        )

    def test_approximate_map_requires_private_and_public_coordinates(self):
        property_item = self.make_property(
            map_visibility=Property.MapVisibility.APPROXIMATE
        )

        with self.assertRaises(ValidationError):
            property_item.full_clean()

    def test_featured_property_requires_manual_order(self):
        property_item = self.make_property(is_featured=True)

        with self.assertRaises(ValidationError):
            property_item.full_clean()

    def test_property_accepts_at_most_twenty_images(self):
        property_item = self.make_property()
        for order in range(20):
            PropertyImage.objects.create(
                property=property_item,
                image=f"properties/test/image-{order}.jpg",
                order=order,
                is_cover=order == 0,
            )

        extra_image = PropertyImage(
            property=property_item,
            image="properties/test/image-20.jpg",
            order=20,
        )
        with self.assertRaises(ValidationError):
            extra_image.clean()

    def test_publication_requires_an_image_and_cover(self):
        property_item = self.make_property()
        with self.assertRaises(ValidationError):
            change_property_status(property_item, Property.Status.PUBLISHED, self.user)

        PropertyImage.objects.create(
            property=property_item,
            image="properties/test/cover.jpg",
            order=0,
            is_cover=True,
        )
        change_property_status(property_item, Property.Status.PUBLISHED, self.user)
        property_item.refresh_from_db()

        self.assertEqual(property_item.status, Property.Status.PUBLISHED)
        self.assertIsNotNone(property_item.published_at)
        self.assertEqual(property_item.changes.count(), 1)

    def test_trash_and_restore_are_audited(self):
        property_item = self.make_property()
        move_property_to_trash(property_item, self.user)
        property_item.refresh_from_db()
        self.assertIsNotNone(property_item.deleted_at)

        restore_property(property_item, self.user)
        property_item.refresh_from_db()
        self.assertIsNone(property_item.deleted_at)
        self.assertEqual(property_item.changes.count(), 2)


class DefaultRoleTests(TestCase):
    def test_administrator_and_editor_groups_exist(self):
        self.assertTrue(Group.objects.filter(name=ADMINISTRATOR_GROUP).exists())
        self.assertTrue(Group.objects.filter(name=EDITOR_GROUP).exists())

    def test_editor_can_manage_properties_but_not_users(self):
        editor = Group.objects.get(name=EDITOR_GROUP)
        permission_names = set(editor.permissions.values_list("codename", flat=True))

        self.assertIn("change_property", permission_names)
        self.assertIn("change_lead", permission_names)
        self.assertNotIn("change_user", permission_names)

    @patch(
        "properties.management.commands.create_chindler_user.getpass",
        side_effect=["Senha-Forte-Para-Teste-123", "Senha-Forte-Para-Teste-123"],
    )
    def test_team_user_command_creates_editor(self, _mock_getpass):
        call_command(
            "create_chindler_user",
            "novo-editor",
            "novo-editor@chindler.com.br",
            role=EDITOR_GROUP,
            verbosity=0,
        )

        user = get_user_model().objects.get(username="novo-editor")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.groups.filter(name=EDITOR_GROUP).exists())
