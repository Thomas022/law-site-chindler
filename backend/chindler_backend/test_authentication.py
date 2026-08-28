from django.contrib.auth import authenticate, get_user_model
from django.core.cache import cache
from django.test import RequestFactory, TestCase
from django.urls import reverse


class AuthenticationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="auth-user",
            email="usuario@chindler.com.br",
            password="Uma-Senha-Segura-123",
            is_staff=True,
        )

    def setUp(self):
        cache.clear()
        self.request = RequestFactory().post(
            "/admin/login/", REMOTE_ADDR="127.0.0.10"
        )

    def test_login_accepts_username(self):
        user = authenticate(
            self.request, username="auth-user", password="Uma-Senha-Segura-123"
        )
        self.assertEqual(user, self.user)

    def test_login_accepts_email(self):
        user = authenticate(
            self.request,
            username="usuario@chindler.com.br",
            password="Uma-Senha-Segura-123",
        )
        self.assertEqual(user, self.user)

    def test_login_is_temporarily_blocked_after_five_failures(self):
        for _ in range(5):
            authenticate(self.request, username="auth-user", password="incorreta")

        user = authenticate(
            self.request, username="auth-user", password="Uma-Senha-Segura-123"
        )
        self.assertIsNone(user)

    def test_successful_login_clears_previous_failures(self):
        for _ in range(4):
            authenticate(self.request, username="auth-user", password="incorreta")

        self.assertEqual(
            authenticate(
                self.request,
                username="auth-user",
                password="Uma-Senha-Segura-123",
            ),
            self.user,
        )

        self.assertIsNone(
            authenticate(self.request, username="auth-user", password="incorreta")
        )
        self.assertEqual(
            authenticate(
                self.request,
                username="auth-user",
                password="Uma-Senha-Segura-123",
            ),
            self.user,
        )

    def test_admin_login_shows_email_label_and_password_reset(self):
        response = self.client.get(reverse("admin:login"))

        self.assertContains(response, "Usuário ou e-mail")
        self.assertContains(response, reverse("admin_password_reset"))

    def test_password_reset_page_is_available(self):
        response = self.client.get(reverse("admin_password_reset"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Recuperar senha")
