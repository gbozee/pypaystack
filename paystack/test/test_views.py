from django.test import SimpleTestCase, Client
from django.urls import reverse, resolve
from paystack.views import banklist,bankdetail
import json

class TestViews(SimpleTestCase):

	def test_banklist_views(self):
		client = Client()
		response =   client.get(reverse('paystack:banklist'))
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'paystack/banklist.html')

	def test_bankdetail_views(self):
		client = Client()
		response =   client.get(reverse('paystack:bankdetail', args=[16]))
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'paystack/bankdetail.html')	

	