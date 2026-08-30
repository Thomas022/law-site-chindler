from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.forms.models import inlineformset_factory
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from tempfile import TemporaryDirectory

from leads.admin import LeadAdmin
from leads.models import Lead

from .admin import PropertyAdmin, PropertyImageInlineFormSet
from .models import Property, PropertyImage
from .roles import ADMINISTRATOR_GROUP, EDITOR_GROUP
from .test_images import make_uploaded_image


class AdminPermissionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.editor = get_user_model().objects.create_user(
            username="editor-admin-test", password="test-password", is_staff=True
        )
        cls.editor.groups.add(Group.objects.get(name=EDITOR_GROUP))
        cls.administrator = get_user_model().objects.create_user(
            username="administrator-admin-test", password="test-password", is_staff=True
        )
        cls.administrator.groups.add(Group.objects.get(name=ADMINISTRATOR_GROUP))

    def setUp(self):
        self.factory = RequestFactory()
        self.property_admin = PropertyAdmin(Property, admin.site)
        self.lead_admin = LeadAdmin(Lead, admin.site)

    def request_for(self, user):
        request = self.factory.get("/admin/")
        request.user = user
        return request

    def test_editor_cannot_use_permanent_delete_action(self):
        actions = self.property_admin.get_actions(self.request_for(self.editor))
        self.assertNotIn("delete_permanently", actions)

    def test_administrator_can_use_permanent_delete_action(self):
        actions = self.property_admin.get_actions(self.request_for(self.administrator))
        self.assertIn("delete_permanently", actions)

    def test_only_administrator_can_delete_leads(self):
        self.assertFalse(
            self.lead_admin.has_delete_permission(self.request_for(self.editor))
        )
        self.assertTrue(
            self.lead_admin.has_delete_permission(self.request_for(self.administrator))
        )

    def test_editor_can_open_property_and_lead_panels(self):
        self.client.force_login(self.editor)

        property_response = self.client.get(
            reverse("admin:properties_property_changelist")
        )
        lead_response = self.client.get(reverse("admin:leads_lead_changelist"))

        self.assertEqual(property_response.status_code, 200)
        self.assertEqual(lead_response.status_code, 200)

    def test_editor_cannot_open_user_management(self):
        self.client.force_login(self.editor)

        response = self.client.get(reverse("admin:auth_user_changelist"))

        self.assertEqual(response.status_code, 403)

    def test_administrator_can_open_user_management(self):
        self.client.force_login(self.administrator)

        response = self.client.get(reverse("admin:auth_user_changelist"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Filtrar usuários")
        self.assertContains(response, "Filtros dos usuários")
        rendered = response.content.decode()
        self.assertLess(
            rendered.index('class="paginator"'),
            rendered.index('class="user-filter-panel user-filter-panel--below"'),
        )

    def test_user_change_page_hides_password_hash_details(self):
        self.client.force_login(self.administrator)

        response = self.client.get(
            reverse("admin:auth_user_change", args=(self.administrator.pk,))
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alterar senha")
        self.assertNotContains(response, "pbkdf2_sha256")
        self.assertNotContains(response, "iterações")
        self.assertNotContains(response, "salt")
        self.assertNotContains(response, "hash")

    def test_property_form_contains_image_gallery(self):
        self.client.force_login(self.editor)

        response = self.client.get(reverse("admin:properties_property_add"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Informações principais")
        self.assertContains(response, "Imagem")

    def test_property_list_uses_operational_dashboard_search_and_filters(self):
        property_item = Property.objects.create(
            title="Apartamento de teste no Leblon",
            description="Imóvel criado para validar o painel.",
            purpose=Property.Purpose.SALE,
            property_type=Property.PropertyType.APARTMENT,
            status=Property.Status.PUBLISHED,
            price="1250000.00",
            total_area="95.00",
            street="Rua Dias Ferreira",
            number="100",
            neighborhood="Leblon",
            city="Rio de Janeiro",
            created_by=self.editor,
            updated_by=self.editor,
        )
        self.client.force_login(self.editor)

        response = self.client.get(reverse("admin:properties_property_changelist"))
        search = self.client.get(
            reverse("admin:properties_property_changelist"), {"q": "Leblon"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Imóveis</h1>", html=True)
        self.assertContains(response, "Resumo dos imóveis")
        self.assertContains(response, "Pesquisar por título, descrição, rua, bairro ou cidade")
        self.assertContains(response, "Filtros dos imóveis")
        self.assertContains(response, "Filtrar imóveis")
        self.assertContains(response, "Publicados")
        self.assertContains(response, "Abrir")
        self.assertEqual(response.context["property_counts"]["active"], 1)
        self.assertEqual(response.context["property_counts"]["published"], 1)
        self.assertContains(search, property_item.title)

    def test_property_change_filters_follow_the_same_bottom_layout(self):
        self.client.force_login(self.editor)

        response = self.client.get(
            reverse("admin:properties_propertychange_changelist")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Filtrar alterações")
        self.assertContains(response, "Filtros das alterações dos imóveis")
        rendered = response.content.decode()
        self.assertLess(
            rendered.index('class="paginator"'),
            rendered.index('class="property-filter-panel property-filter-panel--below"'),
        )

    def test_new_image_with_repeated_default_order_receives_next_free_order(self):
        media_directory = TemporaryDirectory()
        self.addCleanup(media_directory.cleanup)
        media_override = override_settings(MEDIA_ROOT=media_directory.name)
        media_override.enable()
        self.addCleanup(media_override.disable)
        property_item = Property.objects.create(
            title="Imóvel com galeria",
            description="Teste da ordem automática.",
            purpose=Property.Purpose.SALE,
            property_type=Property.PropertyType.APARTMENT,
            price="500000.00",
            total_area="80.00",
            street="Rua Teste",
            number="1",
            neighborhood="Centro",
            city="Rio de Janeiro",
            created_by=self.editor,
            updated_by=self.editor,
        )
        existing = PropertyImage(
            property=property_item,
            image=make_uploaded_image(size=(300, 200)),
            order=0,
            is_cover=True,
        )
        existing.full_clean()
        existing.save()
        FormSet = inlineformset_factory(
            Property,
            PropertyImage,
            formset=PropertyImageInlineFormSet,
            fields=("image", "alt_text", "order", "is_cover"),
            extra=1,
        )
        formset = FormSet(
            data={
                "images-TOTAL_FORMS": "2",
                "images-INITIAL_FORMS": "1",
                "images-MIN_NUM_FORMS": "0",
                "images-MAX_NUM_FORMS": "20",
                "images-0-id": str(existing.pk),
                "images-0-alt_text": "Capa",
                "images-0-order": "0",
                "images-0-is_cover": "on",
                "images-1-id": "",
                "images-1-alt_text": "Segunda foto",
                "images-1-order": "0",
            },
            files={"images-1-image": make_uploaded_image(size=(300, 200))},
            instance=property_item,
            prefix="images",
        )

        self.assertTrue(formset.is_valid(), formset.errors)
        self.assertEqual(formset.forms[1].cleaned_data["order"], 1)
