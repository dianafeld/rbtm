# coding=utf-8
from unittest import skip
from django.contrib.auth.models import User
from django.test import TestCase
from django.test import Client
from main.models import UserProfile


class RequestTest(TestCase):
    def test_login(self):
        response = self.client.get("/experiment/")
        self.assertEqual(response.status_code, 200)

    def test_on(self):
        response = self.client.post('/experiment/')
        self.assertEqual(response.status_code, 200)


class LoginTest(TestCase):
    def setUp(self):
        self.u_adm = User.objects.create(username='admin', password='admin', email='mailadmin@mail.ru')
        self.up_adm = UserProfile.objects.create(user=self.u_adm, role='ADM')

        self.u_exp = User.objects.create(username='exprm', password='exprm')
        self.up_exp = UserProfile.objects.create(user=self.u_exp, role='EXP')

    def test_login_page(self):
        response = self.client.post('/accounts/login/', {'username': 'admin', 'password': 'admin'})
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/accounts/login/', {'username': 'exprm', 'password': 'exprm'})

    def tearDown(self):
        self.up_adm.delete()
        self.u_adm.delete()
        self.up_exp.delete()
        self.u_exp.delete()
