# coding=utf-8
from unittest import skip
from django.test import TestCase
from django.contrib.auth.models import User
from main.models import UserProfile


class StorageIndexTest(TestCase):
    def setUp(self):
        self.u_gst = User.objects.create_user(username='guest', password='guest')
        self.up_gst = UserProfile.objects.create(user=self.u_gst, role='GST')
        self.client.login(username='guest', password='guest')
    
    def test_login(self):
        response = self.client.get("/storage/")
        self.assertEqual(response.status_code, 200)

    def test_search_empty(self):
        response = self.client.post('/storage/',
                                    {'Specimen': '', 'DarkFromCount': '', 'DarkToCount': '', 'DarkFromExposure': '',
                                     'DarkToExposure': '', 'EmptyFromCount': '', 'EmptyToCount': '',
                                     'EmptyFromExposure': '', 'EmptyToExposure': '', 'Finished': '',
                                     'Advanced': '', 'DataFromExposure': '', 'DataToExposure': '',
                                     'DataFromAngleStep': '', 'DataToAngleStep': '', 'DataFromCountPerStep': '',
                                     'DataToCountPerStep': '', 'DataFromStepCount': '', 'DataToStepCount': ''})
        self.assertEqual(response.status_code, 200)

    def test_search_specimen(self):
        self.client.login(username='guest', password='guest')
        response = self.client.post('/storage/',
                                    {'Specimen': 'unreal object!!!___@#', 'DarkFromCount': '', 'DarkToCount': '',
                                     'DarkFromExposure': '',
                                     'DarkToExposure': '', 'EmptyFromCount': '', 'EmptyToCount': '',
                                     'EmptyFromExposure': '', 'EmptyToExposure': '', 'Finished': '',
                                     'Advanced': '', 'DataFromExposure': '', 'DataToExposure': '',
                                     'DataFromAngleStep': '', 'DataToAngleStep': '', 'DataFromCountPerStep': '',
                                     'DataToCountPerStep': '', 'DataFromStepCount': '', 'DataToStepCount': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTrue("alert alert-danger" in response.content)

    def test_record_page_prohibit_symbols(self):
        response = self.client.get('/storage/storage_record_unreal_record/')
        self.assertEqual(response.status_code, 404)
        response = self.client.get('/storage/storage_record_unreal*record/')
        self.assertEqual(response.status_code, 404)
        response = self.client.get('/storage/storage_record_unreal(record/')
        self.assertEqual(response.status_code, 404)
        response = self.client.get('/storage/storage_record_unreal)record/')
        self.assertEqual(response.status_code, 404)
        response = self.client.get('/storage/storage_record_unreal@record/')
        self.assertEqual(response.status_code, 404)

    def test_record_page(self):
        response = self.client.get('/storage/storage_record_unreal-record/')
        self.assertEqual(response.status_code, 200)

        self.assertTrue("alert alert-danger" in response.content)
