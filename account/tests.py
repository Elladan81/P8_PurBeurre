from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase, Client

# Create your tests here.
from django.urls import reverse


class TestAuth(TestCase):
    """
    Tests for the auth functionalities
    """

    def setUp(self):
        """The set up for tests
        """

        self.client = Client()
        User.objects.create_user(username="test",
                                 password="test",
                                 email="test@test.com")

    def test_create_account(self):
        """
        Test to create an account
        """

        self.client.post(
            '/connexion', {"username": "test", "email": "test@test.com",
                           "password": "test"}, follow=True)
        assert (self.client.session['_auth_user_id'])

    def test_logout(self):
        """
        Test to logout user
        """
        self.client.post(
            '/deconnexion', follow=True
        )
        self.assertRaises(
            KeyError, lambda: self.client.session['_auth_user_id'])

    def test_login(self):
        """
        Test to login user
        """
        self.client.post(
            '/connexion', {"username": "test", "password": "test",
                           "connect": "true"}, follow=True)
        assert (self.client.session['_auth_user_id'])

    def test_login_error(self):
        """
        Test login error with a bad password
        """

        self.client.post(
            '/connexion', {"username": "test", "password": "testesfqsf",
                           "connect": "true"}, follow=True)
        self.assertRaises(
            KeyError, lambda: self.client.session['_auth_user_id'])

    def test_password_reset_mail_send(self):
        """
        Test for email sending
        """
        response = self.client.post('/password_reset/',
                                    {"email": "test@test.com"}, follow=True)
        self.assertContains(response, "mot de passe")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject,
                         'PurBeurre Recuperation du mot de passe')

    def test_password_reset(self):
        """
        Test for email sending
        """
        response = self.client.post('/password_reset/',
                                    {"email": "test@test.com"}, follow=True)
        self.assertEqual(len(mail.outbox), 1)
        url = mail.outbox[0].body.split()[15]
        uidb64 = url.split('/')[4]
        token = url.split('/')[5]
        response = self.client.get(
            reverse(
                "password_reset_confirm", args=(uidb64, token)), follow=True)
        self.assertContains(response, "Changer votre mot de passe")
        response = self.client.post(reverse(
            "password_reset_confirm", args=(uidb64, "set-password")),
            {"new_password1": "retest1234",
             "new_password2": "retest1234"},
            follow=True)
        self.assertContains(response, "mot de passe à été réinitialisé")
        self.client.post(
            '/connexion', {"username": "test", "password": "retest1234",
                           "connect": "true"}, follow=True)
        assert (self.client.session['_auth_user_id'])
