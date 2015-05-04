from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from main.models import UserProfile
from bootstrap3.exceptions import BootstrapError

class LoginTest(TestCase):
    def setUp(self):
        self.u_adm = User.objects.create(username='admin', password='admin')
        self.up_adm = UserProfile.objects.create(user=self.u_adm, role='ADM')
        
        self.u_exp = User.objects.create(username='exprm', password='exprm')
        self.up_exp = UserProfile.objects.create(user=self.u_exp, role='EXP')
        
        self.u_res = User.objects.create(username='resch', password='resch')
        self.up_res = UserProfile.objects.create(user=self.u_res, role='RES')
        
        self.u_gst = User.objects.create(username='guest', password='guest')
        self.up_gst = UserProfile.objects.create(user=self.u_gst, role='GST')

    def test_login_page(self):
        c = Client()
        response = c.post('/accounts/login/', {'username': 'admin', 'password': 'admin'})
        self.assertEqual(response.status_code, 200)
        response = c.post('/accounts/login/', {'username': 'guest', 'password': 'guest'})
        self.assertEqual(response.status_code, 200)
        response = c.post('/accounts/login/', {'username': 'guest', 'password': 'wrongpass'})
        self.assertEqual(response.status_code, 200)
        
    def test_register(self):
        c = Client()
        response = c.post('/accounts/register/', {'username': 'admin2', 'password1': 'admin2', 'password2': 'admin2', 'email': 'mail@mail.ru', 'full_name': 'FIO'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'http://testserver/accounts/register/complete/')
        
        # existing user
        with self.assertRaises(BootstrapError):
            c.post('/accounts/register/', {'username': 'guest', 'password1': 'admin2', 'password2': 'admin2', 'email': 'email@mail.ru', 'full_name': 'FIO'})
        # wrong pass
        with self.assertRaises(BootstrapError):
            c.post('/accounts/register/', {'username': 'admin3', 'password1': 'admin2', 'password2': 'not_admin2', 'email': 'email@mail.ru', 'full_name': 'FIO'})  
        # wrong mail
        with self.assertRaises(BootstrapError):
            c.post('/accounts/register/', {'username': 'admin3', 'password1': 'admin2', 'password2': 'admin2', 'email': 'email@mail', 'full_name': 'FIO'})
        # wrong mail
        with self.assertRaises(BootstrapError):
            c.post('/accounts/register/', {'username': 'admin3', 'password1': 'admin2', 'password2': 'admin2', 'email': '@mail.ru', 'full_name': 'FIO'})
        '''# duplicate mail
        with self.assertRaises(BootstrapError):
            c.post('/accounts/register/', {'username': 'admin3', 'password1': 'admin2', 'password2': 'admin2', 'email': 'mail@mail.ru', 'full_name': 'FIO'})
        # empty full_name
        with self.assertRaises(BootstrapError):
            c.post('/accounts/register/', {'username': 'admin3', 'password1': 'admin2', 'password2': 'admin2', 'email': 'email@mail.ru'})'''
        

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
        self.u_adm = User.objects.create(username='admin', password='admin')
        self.up_adm = UserProfile.objects.create(user=self.u_adm, role='ADM')
        
        self.u_exp = User.objects.create(username='exprm', password='exprm')
        self.up_exp = UserProfile.objects.create(user=self.u_exp, role='EXP')
        
        self.u_res = User.objects.create(username='resch', password='resch')
        self.up_res = UserProfile.objects.create(user=self.u_res, role='RES')
        
        self.u_gst = User.objects.create(username='guest', password='guest')
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
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'http://testserver/accounts/login/?next=/experiment/')
        # logged as experimentator
        c.login(username='exprm', password='exprm')
        response = c.get('/experiment/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'http://testserver/accounts/login/?next=/experiment/')
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
