# coding=utf-8
from unittest import skip
from django.test import TestCase


class StorageIndexTest(TestCase):
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
