# coding=utf-8
from django.test import TestCase


class StorageIndexTest(TestCase):
    def LogInTest(self):
        response = self.client.get("/storage/")
        self.assertEqual(response.status_code, 201)

    def PaginationTest(self):
        response = self.client.post("/storage/",
                                    {"KeyWords": "KeyWords", "SinceDate": "2015-04-08", "ToDate": "2015-04-16",
                                     "Finished": "Завершен", "Owner": "Owner"})
        self.assertEqual(response.status_code, 200)