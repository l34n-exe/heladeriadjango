from django.contrib.auth import get_user_model
from django.test import TestCase


class AuthTokenTests(TestCase):
    def test_token_endpoint_emite_tokens_para_usuario_valido(self):
        user_model = get_user_model()
        user_model.objects.create_user(
            username="token-user",
            password="secure-pass-123",
            is_staff=True,
        )

        response = self.client.post(
            "/heladerias/auth/token/",
            {"username": "token-user", "password": "secure-pass-123"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.json())
        self.assertIn("refresh", response.json())

    def test_token_endpoint_rechaza_credenciales_invalidas(self):
        response = self.client.post(
            "/heladerias/auth/token/",
            {"username": "missing-user", "password": "wrong-password"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)
