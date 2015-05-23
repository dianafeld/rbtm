# coding=utf-8
from unittest import skip
from django.test import TestCase


class StorageIndexTest(TestCase):
    def test_login(self):
        response = self.client.get("/storage/")
        self.assertEqual(response.status_code, 200)

    def test_search_response(self):
        response = self.client.post('/storage/',
                                    {'Specimen': '', 'DarkFromCount': '', 'DarkToCount': '', 'DarkFromExposure': '',
                                     'DarkToExposure': '', 'EmptyFromCount': '', 'EmptyToCount': '',
                                     'EmptyFromExposure': '', 'EmptyToExposure': '', 'Finished': '',
                                     'Advanced': '', 'DataFromExposure': '', 'DataToExposure': '',
                                     'DataFromAngleStep': '', 'DataToAngleStep': '', 'DataFromCountPerStep': '',
                                     'DataToCountPerStep': '', 'DataFromStepCount': '', 'DataToStepCount': ''})
        self.assertEqual(response.status_code, 200)

    def test_record_page(self):
        response = self.client.get('/storage/')
        self.assertEqual(response.status_code, 200)