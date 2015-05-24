# coding=utf-8
from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from main.models import UserProfile


class ExpPageTest(TestCase):
    def setUp(self):
        self.u_exp = User.objects.create(username='exprm', password='exprm')
        self.up_exp = UserProfile.objects.create(user=self.u_exp, role='EXP')
        self.c = Client()
    
    def test_exp_available(self):
        self.c.login(username='exprm', password='exprm')
        response = self.c.get('/experiment/')
        self.assertEquals(response.status_code, 302)

    def test_search_empty(self):
        self.c.login(username='exprm', password='exprm')
        response = self.c.post('/experiment/interface',
                                    {
                                        'experiment id': '0536ba11-548a-4e98-92a7-61f126235332',
                                        'specimen': 'test',
                                        'tags': '',
                                        'experiment parameters':
                                            {
                                                'advanced': False,
                                                'DARK':
                                                    {
                                                        'count': 1,
                                                        'exposure': 1000
                                                    },
                                                'EMPTY':
                                                    {
                                                        'count': 1,
                                                        'exposure': 1000
                                                    },
                                                'DATA':
                                                    {
                                                        'step count': 1,
                                                        'exposure': 1000,
                                                        'angle step': 10,
                                                        'count per step': 1
                                                    }
                                            }
                                    })
        self.assertEqual(response.status_code, 301)
   
if __name__ == '__main__':
    unittest.main(
        testRunner=xmlrunner.XMLTestRunner(output='test-reports'),
        failfast=False, buffer=False, catchbreak=False
    )


