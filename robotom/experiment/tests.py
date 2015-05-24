# coding=utf-8
from django.test import TestCase
from django.test import Client


class ExpPageTest(TestCase):
	def test_exp_available(self):
    c = Client()
    response = c.get('/experiment/')
    self.assertEquals(response.status_code, 200)


