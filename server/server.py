import time
from _controller import ProductController
from _config import Config, generate_log

actions = {
    1: 'update api id database',
    2: 'update brands api'
}


class Application:

    def __init__(self):
        self._product_controller = ProductController()
        self._config = Config()
        self._products_api = None
        self._products_database = None

    def synchronize(self):
        while self._config.system_active:
            try:
                generate_log('start process synchronize')
                self._products_api = self._product_controller.get_products_api()
                self._products_database = self._product_controller.get_products_database()
                self.execute_action(actions[1])
                self.execute_action(actions[2])
                time.sleep(self._config.system_sleep_timer_synchronize)
            except Exception as fail:
                generate_log('crash synchronize, fail: {}'.format(fail))
                break
    
    def execute_action(self, action):
        generate_log('start process {}'.format(action))

        try:
            if action == actions[1]:
                self.update_api_id_database()

            if action == actions[2]:
                self.update_api_brands()

        except Exception as fail:
            generate_log('crash process {}, fail: {}'.format(action, fail))
        
        generate_log('finishing process {}'.format(action))
    
    def update_api_id_database(self):
        values_keys = {}
        for product_database in self._products_database:
            products_api = filter(lambda x: x['erpId'] == product_database['erpId'], self._products_api)
            products_api = list(products_api)

            if len(products_api) == 0:
                generate_log('product {} not found in ciashop'.format(product_database['erpId']))

            for product_api in products_api:
                if product_database['id'] != product_api['id']:
                    generate_log('update database: product {} ciashop_id {}'.format(product_database['erpId'],
                                                                                    product_api['id']))
                    values_keys.update({product_database['erpId']: product_api['id']})

        self._product_controller.update_products_database(values_keys)

    def update_api_brands(self):
        products_database_update = {}
        for product_api in self._products_api:
            products_database = filter(lambda x: x['erpId'] == product_api['erpId'], self._products_database)
            products_database = list(products_database)

            if len(products_database) == 0:
                generate_log('product {} not found in database'.format(product_api['erpId']))

            for product_database in products_database:
                if product_api['brand'] != product_database['brand']:
                    generate_log('update ciashop: product {} brand {}'.format(product_database['erpId'],
                                                                              product_database['brand']['name']))
                    products_database_update.update({product_api['id']: {'brand': product_database['brand']}})

        self._product_controller.update_products_api(products_database_update)


application = Application()
application.synchronize()
