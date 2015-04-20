from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from main.models import UserProfile

class LoginTest(TestCase):
    def setUp(self):
        self.u_adm = User.objects.create(username='admin', password='admin', is_superuser=True)
        self.up_adm = UserProfile.objects.create(user=self.u_adm, role='ADM')
        
    def test_login_page(self):
        c = Client()
        response = c.post('/accounts/login/', {'username': 'admin', 'password': 'admin'})
        self.assertEqual(response.status_code, 200)

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
        # logged as admin
        c.login(username='admin', password='admin')
        response = c.get('/experiment/')
        self.assertEqual(response.status_code, 302)
        # logged as experimentator
        c.login(username='exprm', password='exprm')
        response = c.get('/experiment/')
        self.assertEqual(response.status_code, 302)
        # logged as admin
        c.login(username='resch', password='resch')
        response = c.get('/experiment/')
        self.assertEqual(response.status_code, 302)
        # logged as admin
        c.login(username='guest', password='guest')
        response = c.get('/experiment/')
        self.assertEqual(response.status_code, 302)

    def tearDown(self):
        self.up_adm.delete()
        self.u_adm.delete()
        self.up_res.delete()
        self.u_res.delete()
        self.up_gst.delete()
        self.u_gst.delete()
        self.up_exp.delete()
        self.u_exp.delete()
