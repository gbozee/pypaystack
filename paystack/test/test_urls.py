from django.test import SimpleTestCase
from django.urls import reverse, resolve
from paystack.views import banklist,bankdetail

class TestUrls(SimpleTestCase):

	def test_banklist_url(self):
		url = reverse('paystack:banklist')
		self.assertEquals(resolve(url).func, banklist)

	def test_bankdetail_url(self):
		url = reverse('paystack:bankdetail', args=[1])
		self.assertEquals(resolve(url).func, bankdetail)	