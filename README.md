## Django Paystack

[![Build Status](https://travis-ci.org/gbozee/django-paystack.svg?branch=master
)](https://travis-ci.org/gbozee/django-paystack.svg?branch=master
)


This is a reusable django library that makes it very easy to hook up [Paystack]() purchase button to your site/app. It helps with the verification of the transaction and is highly conifgurable.

Usage:

1. Install `django-paystack`
```
pip install -e https://github.com/gbozee/django-paystack.git@master#egg=paystack
```

2. Add `paystack` to your `settings` module
```
INSTALLED_APPS = [
    ...,
    paystack,

]
```

3. Add `url(r'^paystack/', include('paystack.urls',namespace='paystack'))` to your base `urls.py` file
```
urlpatterns = [
    ...,
    url(r'^paystack/', include('paystack.urls',namespace='paystack')),
]
```

4. Login to [Paystack settings Dashboard](https://dashboard.paystack.com/#/settings/developer) and fetch your `PUBLIC_KEY` and `SECRET_KEY`. paste these keys in your `settings.py`

```
# settings.py

PAYSTACK_PUBLIC_KEY=******,
PAYSTACK_SECRET_KEY=******
```

![alt text](./docs/key.png)

5. In the html where you want to insert the payment button

```
{% load paystack %}
...
{% paystack_button amount=3000 email="j@example.com" %}

```

6. A `signal` is provided with the verified  reference as well as the amount

```
from hubspot.signals import payment_verified

from django.dispatch import receiver

@receiver(payment_verified)
def on_payment_verified(sender, ref,amount, **kwargs):
    """
    ref: paystack reference sent back.
    amount: amount in Naira.
    """
    pass
```

### Configurations

**Required**

`PAYSTACK_PUBLIC_KEY`

`PAYSTACK_SECRET_KEY`

_Optional_

`PAYSTACK_FAILED_URL` # Redirect url when payment fails, default is `paystack:failed_url`

`PAYSTACK_SUCCESS_URL` # Redirect url when payment is successful, default is `paystack:success_url`

`PAYSTACK_LIB_MODULE` # module directory to overide default implemenation of library that calls paystack api, default is `paystack.utils`


### Template Tag Usage

the template tag `paystack_button` takes the following argument

`button_style`: css class to style the button

`button_id`: id name for the button: default is "django-paystack-button"

`email`: a required field representing the email

`amount`: a required the amount to be paid in Naira. `

`ref`: an optional field representing the reference of the transaction`

`redirect_url`: an optional field representing the redirect url after payment has been made, defaults to `paystack:verify_payment`

**NB**: *If you prefer using css to style html tags, the id of the button is *


**To view the sample test project, do the following**
```
$ git clone https://github.com/gbozee/django-paystack.git
$ git checkout develop
$ pip install -r requirements.txt
$ pip install -e .

```

**NB:** If you use [pipenv](), do the following
```
$ pipenv install

```

To run the project
```
$ cd django_paystack
$ python manage.py runserver

```

![alt text](./docs/home_page.PNG)


![alt text](./docs/page2.PNG)


![alt text](./docs/page3.PNG)

## Extending
The default templates used can be extended to include your custom content.

1. Create a `paystack` directory in your `templates` folder.

The templates used are as follows.

```
paystack/failed-page.html
paystack/success-page.html
```