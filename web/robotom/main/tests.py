from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from django.forms import ValidationError
from main.models import UserProfile
from bootstrap3.exceptions import BootstrapError


class LoginTest(TestCase):
    def setUp(self):
        self.u_adm = User.objects.create_user(username='admin', password='admin', email='mailadmin@mail.ru')
        self.up_adm = UserProfile.objects.create(user=self.u_adm, role='ADM')

        self.u_exp = User.objects.create_user(username='exprm', password='exprm')
        self.up_exp = UserProfile.objects.create(user=self.u_exp, role='EXP')

        self.u_res = User.objects.create_user(username='resch', password='resch')
        self.up_res = UserProfile.objects.create(user=self.u_res, role='RES')

        self.u_gst = User.objects.create_user(username='guest', password='guest')
        self.up_gst = UserProfile.objects.create(user=self.u_gst, role='GST')

        self.c = Client()

    def test_login_page(self):
        response = self.c.post('/accounts/login/', {'username': 'admin', 'password': 'admin'})
        self.assertEqual(response.status_code, 302)
        response = self.c.post('/accounts/login/', {'username': 'guest', 'password': 'guest'})
        self.assertEqual(response.status_code, 302)
        response = self.c.post('/accounts/login/', {'username': 'guest', 'password': 'wrongpass'})
        self.assertEqual(response.status_code, 200)

    def test_register_ok(self):
        response = self.c.post('/accounts/register/',
                               {'username': 'admin2', 'password1': 'admin2', 'password2': 'admin2',
                                'email': 'mail@mail.ru', 'full_name': 'FIO', u'degree': '', u'title': u'',
                                u'gender': 'N', u'address': '', u'work_place': '', u'phone_number': ''})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'http://testserver/accounts/done/')

    def test_register_existing_user(self):
        response = self.c.post('/accounts/register/',
                               {'username': 'admin', 'password1': 'admin2', 'password2': 'admin2',
                                'email': 'email@mail.ru', 'full_name': 'FIO', u'degree': '', u'title': u'',
                                u'gender': 'N', u'address': '', u'work_place': '', u'phone_number': ''})
        self.assertEqual(response.status_code, 200)

    def test_register_wrong_pass(self):
        response = self.c.post('/accounts/register/',
                               {'username': 'admin3', 'password1': 'admin2', 'password2': 'not_admin2',
                                'email': 'email@mail.ru', 'full_name': 'FIO', u'degree': '', u'title': u'',
                                u'gender': 'N', u'address': '', u'work_place': '', u'phone_number': ''})
        self.assertEqual(response.status_code, 200)

    def test_register_wrong_mail(self):
        response = self.c.post('/accounts/register/',
                               {'username': 'admin3', 'password1': 'admin2', 'password2': 'admin2',
                                'email': 'email@mail', 'full_name': 'FIO', u'degree': '', u'title': u'', u'gender': 'N',
                                u'address': '', u'work_place': '', u'phone_number': ''})
        self.assertEqual(response.status_code, 200)

        response = self.c.post('/accounts/register/',
                               {'username': 'admin3', 'password1': 'admin2', 'password2': 'admin2', 'email': '@mail.ru',
                                'full_name': 'FIO', u'degree': '', u'title': u'', u'gender': 'N', u'address': '',
                                u'work_place': '', u'phone_number': ''})
        self.assertEqual(response.status_code, 200)

    def test_register_duplicate_mail(self):
        response = self.c.post('/accounts/register/',
                               {'username': 'admin3', 'password1': 'admin2', 'password2': 'admin2',
                                'email': 'mailadmin@mail.ru', 'full_name': 'FIO', u'degree': '', u'title': u'',
                                u'gender': 'N', u'address': '', u'work_place': '', u'phone_number': ''})
        self.assertEqual(response.status_code, 200)

    def test_register_empty_full_name(self):
        response = self.c.post('/accounts/register/',
                               {'username': 'admin3', 'password1': 'admin2', 'password2': 'admin2',
                                'email': 'email@mail.ru', 'full_name': '', u'degree': '', u'title': u'', u'gender': 'N',
                                u'address': '', u'work_place': '', u'phone_number': ''})
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        self.up_adm.delete()
        self.u_adm.delete()
        self.up_res.delete()
        self.u_res.delete()
        self.up_gst.delete()
        self.u_gst.delete()
        self.up_exp.delete()
        self.u_exp.delete()


class ExperimentPermissionTest(TestCase):
    def setUp(self):
        self.u_adm = User.objects.create_user(username='admin', password='admin')
        self.up_adm = UserProfile.objects.create(user=self.u_adm, role='ADM')

        self.u_exp = User.objects.create_user(username='exprm', password='exprm')
        self.up_exp = UserProfile.objects.create(user=self.u_exp, role='EXP')

        self.u_res = User.objects.create_user(username='resch', password='resch')
        self.up_res = UserProfile.objects.create(user=self.u_res, role='RES')

        self.u_gst = User.objects.create_user(username='guest', password='guest')
        self.up_gst = UserProfile.objects.create(user=self.u_gst, role='GST')

    def test_exp_perm(self):
        c = Client()
        # not logged in
        response = c.get('/experiment/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'http://testserver/accounts/login/?next=/experiment/')
        # logged as admin
        c.login(username='admin', password='admin')
        response = c.get('/experiment/')
        self.assertEqual(response.status_code, 200)
        # logged as experimentator
        c.login(username='exprm', password='exprm')
        response = c.get('/experiment/')
        self.assertEqual(response.status_code, 200)
        # logged as admin
        c.login(username='resch', password='resch')
        response = c.get('/experiment/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'http://testserver/accounts/login/?next=/experiment/')
        # logged as admin
        c.login(username='guest', password='guest')
        response = c.get('/experiment/')
        self.assertEqual(response.status_code, 302)
        c.login(username='guest', password='wrongpass')
        response = c.get('/experiment/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'http://testserver/accounts/login/?next=/experiment/')

    def tearDown(self):
        self.up_adm.delete()
        self.u_adm.delete()
        self.up_res.delete()
        self.u_res.delete()
        self.up_gst.delete()
        self.u_gst.delete()
        self.up_exp.delete()
        self.u_exp.delete()
