# coding=utf-8
from django.test import TestCase


class StorageIndexTest(TestCase):
    def test_login(self):
        response = self.client.get("/storage/")
        self.assertEqual(response.status_code, 200)

    def test_pagination(self):
        response = self.client.post("/storage/",
                                    {"KeyWords": "KeyWords", "SinceDate": "2015-04-08", "ToDate": "2015-04-16",
                                     "Finished": "---", "Owner": "Owner"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(int(response.context["current_page"]), 1)
        response = self.client.get("/storage/?page=4")
        self.assertEqual(int(response.context["current_page"]), 4)