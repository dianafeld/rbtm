# coding=utf-8
from django.test import TestCase
from django.test import Client


class ExpPageTest(TestCase):
	def test_exp_available(self):
    c = Client()
    response = c.get('/experiment/')
    self.assertEquals(response.status_code, 200)
    
if __name__ == '__main__':
    unittest.main(
        testRunner=xmlrunner.XMLTestRunner(output='test-reports'),
        failfast=False, buffer=False, catchbreak=False
    )

