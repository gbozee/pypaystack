from datetime import datetime
from .base import BaseClass


class PlanAndSubscription(BaseClass):
    def create_plan(self, data):
        path = "/plan"
        new_data = {
            "name": data['name'],
            'interval': data['interval'],
            'amount': data['amount'] * 100,
            'currency': data['currency'].upper()
        }
        response = self.make_request("POST", path, json=new_data)
        return self.result_format(response)

    def create_plans(self, data):
        params = [{
            'amount': data['amount'][x],
            'currency': x.upper(),
            'name': data['name'],
            'interval': data['interval']
        } for x in data['amount'].keys()]
        results = [self.create_plan(x) for x in params]
        if all([x[0] for x in results]):
            plans = {
                x[2]['currency'].lower(): x[2]['plan_code']
                for x in results
            }
            plan_id = {x[2]['currency'].lower(): x[2]['id'] for x in results}
            return True, {
                'name': data['name'],
                'plan': plans,
                'interval': data['interval'],
                'plan_id': plan_id
            }
        return False, "Could not create plans"

    def update_plans(self, existing_data, new_data):
        params = [{
            'plan': existing_data['plan'][x],
            'name': new_data['name'],
            'amount': new_data['amount'][x]
        } for x in existing_data['plan'].keys()]
        results = [self.update_plan(y) for y in params]
        if all([x[0] for x in results]):
            results = [
                self.get_plan(x) for x in existing_data['plan'].values()
            ]
            if all([x[0] for x in results]):
                data_only = [x[2] for x in results]
                return True, {
                    'name': results[0][2]['name'],
                    'interval': results[0][2]['interval'],
                    'plan': {
                        key['currency'].lower(): key['plan_code']
                        for key in data_only
                    },
                    'plan_id':
                    {key['currency'].lower(): key['id']
                     for key in data_only}
                }
        return False, "Could not update plans"

    def list_plans(self, params):
        new_params = params.copy()
        if params.get('amount'):
            new_params['amount'] = new_params['amount'] * 100
        path = "/plan"
        response = self.make_request('GET', path, params=new_params)
        return self.result_format(response)

    def get_plan(self, plan_code):
        path = "/plan/{}".format(plan_code)
        response = self.make_request('GET', path)
        return self.result_format(response)

    def update_plan(self, data):
        new_data = data.copy()
        path = "/plan/{}".format(new_data.pop('plan'))
        if 'amount' in new_data.keys():
            new_data['amount'] = new_data['amount'] * 100
        response = self.make_request('PUT', path, json=new_data)

        def callback(rr):
            return rr['status'], rr['message']

        return self.result_format(response, callback)

    def create_subscription(self, data):
        path = "/subscription"
        new_data = data.copy()
        response = self.make_request('POST', path, json=new_data)
        return self.result_format(response)

    def get_all_subscriptions(self, data):
        path = '/subscription'
        response = self.make_request('GET', path, params=data)
        return self.result_format(response)

    def activate_subscription(self, data, activate=True):
        path = "/subscription/enable"
        if not activate:
            path = '/subscription/disable'
        response = self.make_request('POST', path, json=data)

        def callback(rr):
            return rr['status'], rr['message']

        return self.result_format(response, callback)

    def get_subscription(self, subscription_code):
        path = '/subscription/{}'.format(subscription_code)
        response = self.make_request('GET', path)
        return self.result_format(response)
