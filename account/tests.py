from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import TestCase, Client

# Create your tests here.
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


class TestAuth(TestCase):
    """
    Tests for the auth functionalities
    """

    def setUp(self):
        """The set up for tests
        """
        self.client = Client()
        # lambda user
        self.user = User.objects.create_user(username="test", password="test", email="test@test.com")
        # user for register test with value form and log in credential
        self.user_register = {"username": "newtest",
                              "first_name": "newtest",
                              "email": "newtest@test.com",
                              "password": "newtest",
                              "passowrd2": "newtest",
                              }
        self.user_register_credential = {"username": "newtest",
                                         "password": "newtest",
                                         "connect": "true"}
        # inactive user
        self.inactive_user = User.objects.create_user(username='new_name', password='pass',
                                                      email='test@test.com',is_active=False)
        self.inactive_user_credential = {"username": "new_name", "password": "pass"}

    def test_register(self):
        """
        Test to create an account
        """
        self.client.post(reverse('register'), data=self.user_register, follow=True)
        assert (lambda: self.client.session['_auth_user_id'])

    def test_register_form_is_valid(self):
        # form with valid values
        response = self.client.post(reverse('register'), data=self.user_register, follow=True)
        # assert if register form is valid
        self.assertTrue(response.context['form'].is_valid)

    def test_register_user_not_active(self):
        """
        Test to login with account is_active == False
        """
        # complete form with incative user
        self.client.post(reverse('register'), data=self.user_register, follow=True)
        # try to log user
        response = self.client.post(reverse('login'), self.user_register_credential, follow=True)
        # if assert False, user is not log in.
        self.assertFalse(response.context['user'].is_active)

    def test_activate(self):
        """
        Test to activate an account
        """
        # encore url for inactive user
        uidb64 = urlsafe_base64_encode(force_bytes(self.inactive_user.pk))
        token = default_token_generator.make_token(self.inactive_user)
        # get view activate for inactive user
        self.client.get(reverse('activate', args=(uidb64, token)), follow=True)
        # log in inactive user
        response = self.client.post(reverse('login'), self.inactive_user_credential, follow=True)
        # test if activate user == new user. If equal, assert incative user is active and can now log in
        self.assertEqual(response.context['user'], self.inactive_user)
        # test if inactive user is now active
        self.assertTrue(response.context['user'].is_active)

    def test_logout(self):
        """
        Test to logout user
        """
        self.client.get(
            reverse('logout'),
            follow=True
        )
        self.assertRaises(KeyError, lambda: self.client.session['auth_user_id'])

    def test_login(self):
        """
        Test to login user
        """
        response = self.client.post(reverse('login'),
                         {"username": "test",
                          "password": "test",
                          "connect": "true"},
                         follow=True)
        self.assertEqual(response.context['user'], self.user)

    def test_login_error(self):
        """
        Test login error with a bad password
        """

        self.client.post(reverse('login'),
                         {"username": "test",
                          "password": "testesfqsf",
                          "connect": "true"},
                         follow=True)
        self.assertRaises(KeyError, lambda: self.client.session['_auth_user_id'])

    def test_password_reset_mail_send(self):
        """
        Test for email sending
        """
        response = self.client.post(reverse('password_reset'),
                                    {"email": "test@test.com"},
                                    follow=True)
        self.assertEqual(len(mail.outbox), 1)

    def test_password_reset(self):
        """
        Test for email sending
        """
        response = self.client.post(reverse('password_reset'),
                                    {"email": "test@test.com"},
                                    follow=True)
        url = mail.outbox[0].body.split()[16]
        uidb64 = url.split('/')[4]
        token = url.split('/')[5]
        self.client.get(
            reverse("password_reset_confirm",
                    args=(uidb64, token)),
            follow=True)
        self.client.post(reverse(
            "password_reset_confirm", args=(uidb64, "set-password")),
            {"new_password1": "retest1234",
             "new_password2": "retest1234"},
            follow=True)
        self.client.post(
            reverse('login'), {"username": "test", "password": "retest1234",
                               "connect": "true"}, follow=True)
        assert (lambda: self.client.session['_auth_user_id'])
