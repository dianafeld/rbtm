# coding=utf-8
from django.test import TestCase
from django.test import Client


class ExpPageTest(TestCase):
	def test_exp_available(self):
    c = Client()
    response = c.get('/experiment/')
    self.assertEquals(response.status_code, 200)

    def test_search_empty(self):
        response = self.client.post('/experiment/interface',
									{
										'experiment id': '0536ba11-548a-4e98-92a7-61f126235332',
										'specimen': 'test',
										'tags': ,
										'experiment parameters':
											{
												'advanced': False,
												'DARK':
												    {
												        'count': 1,
												        'exposure': 1000,0
												    },
												'EMPTY':
												    {
												        'count': 1,
												        'exposure': 1000,0
												    },
												'DATA':
												    {
												        'step count': 1,
												        'exposure': 1000,0,
												        'angle step': 10,0,
												        'count per step': 1
												    }
											}
									})
        self.assertEqual(response.status_code, 200)
   
if __name__ == '__main__':
    unittest.main(
        testRunner=xmlrunner.XMLTestRunner(output='test-reports'),
        failfast=False, buffer=False, catchbreak=False
    )


