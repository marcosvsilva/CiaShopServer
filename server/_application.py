from _controller import ProductController, DepartmentController
from _config import Config, generate_log, get_list_exclude
import unicodedata
import re

actions = {
    1: 'update database api id products',
    2: 'update database api id departments',
    3: 'update database api id variants',
    4: 'update database products departments',
    5: 'update api departments products',
    6: 'update api brands',
    7: 'update api filters'
}


class Application:

    def __init__(self):
        self._config = Config()

        if self._config.get_key('active') == 'yes':
            self._product_controller = ProductController()
            self._products_api = None
            self._products_database = None

            self._departments_controller = DepartmentController()
            self._departments_api = None
            self._departments_database = None

            self.excludes = []
        else:
            generate_log('application not start because config active = "no"')

    def synchronize(self):
        if self._config.get_key('active') == 'yes':
            try:
                self.excludes = get_list_exclude()

                generate_log('---------------------------------------------------------------')
                generate_log('start process synchronize')

                self._products_api = self._product_controller.get_products_api()
                self._products_database = self._product_controller.get_products_database()

                self._departments_api = self._departments_controller.get_departments_api()
                self._departments_database = self._departments_controller.get_departments_database()

                self.execute_action(actions[1])
                self.execute_action(actions[2])
                self.execute_action(actions[3])
                self.execute_action(actions[4])

                # Finishing process update products database, necessary reload products
                self._products_database = self._product_controller.get_products_database()

                self.execute_action(actions[5])
                self.execute_action(actions[6])
                self.execute_action(actions[7])

                generate_log('end process synchronize')
                generate_log('---------------------------------------------------------------')

                time_to_sleep = int(self._config.get_key('sleep_timer_synchronize'))
                generate_log('application waiting {} seconds to synchronize'.format(time_to_sleep))
            except Exception as fail:
                raise Exception('crash process {}'.format(fail))

    def execute_action(self, action):
        generate_log('start process {}'.format(action))

        if action == actions[1]:
            self.update_database_api_id_products()

        if action == actions[2]:
            self.update_database_api_id_departments()

        if action == actions[3]:
            self.update_database_api_id_variants()

        if action == actions[4]:
            self.update_database_products_departments()

        if action == actions[5]:
            self.update_api_departments_products()

        if action == actions[6]:
            self.update_api_brands()

        if action == actions[7]:
            self.update_api_filters()

        generate_log('finishing process {}'.format(action))

    def update_database_api_id_products(self):
        values_keys = {}
        for product_database in self._products_database:
            if product_database['erpId'] not in self.excludes:
                if product_database['id'] < 0:
                    products_api = filter(lambda x: x['erpId'] == product_database['erpId'], self._products_api)
                    products_api = list(products_api)

                    if len(products_api) == 0:
                        generate_log('product erpId: {} not found in ciashop'.format(product_database['erpId']))

                    for product_api in products_api:
                        if product_database['id'] != product_api['id']:
                            values_keys.update({product_database['erpId']: product_api['id']})

        self._product_controller.update_products_database(values_keys)

    def update_database_api_id_departments(self):
        values_keys = {}
        for departments_database in self._departments_database:
            if departments_database['erpId'] not in self.excludes:
                if departments_database['id'] < 0:
                    departments_api = filter(lambda x: x['erpId'] == departments_database['erpId'],
                                             self._departments_api)
                    departments_api = list(departments_api)

                    if len(departments_api) == 0:
                        generate_log('department erpId: {} not found in ciashop'.format(departments_database['erpId']))

                    for department_api in departments_api:
                        if departments_database['id'] != department_api['id']:
                            values_keys.update({departments_database['erpId']: department_api['id']})

        self._departments_controller.update_departments_database(values_keys)

    def update_database_api_id_variants(self):
        values_keys = {}
        for product_database in self._products_database:
            if product_database['erpId'] not in self.excludes:
                products_api = filter(lambda x: x['erpId'] == product_database['erpId'], self._products_api)
                products_api = list(products_api)

                if len(products_api) == 0:
                    generate_log('product erpId: {} not found in ciashop'.format(product_database['erpId']))

                for product_api in products_api:
                    if product_database['variantId'] != product_api['mainVariantId']:
                        values_keys.update({product_database['erpId']: product_api['mainVariantId']})

        self._product_controller.update_variants_database(values_keys)

    def update_database_products_departments(self):
        self._product_controller.update_department_id()

    def update_api_departments_products(self):
        products_department_update = {}
        for product_api in self._products_api:
            if product_api['erpId'] not in self.excludes:
                products_database = filter(lambda x: x['erpId'] == product_api['erpId'], self._products_database)
                products_database = list(products_database)

                if len(products_database) == 0:
                    generate_log('product erpId: {} not found in database'.format(product_api['erpId']))

                for product_database in products_database:
                    if product_database['mainDepartmentId'] < 0:
                        continue

                    if product_api['mainDepartmentId'] != product_database['mainDepartmentId']:
                        products_department_update.update(
                            {product_api['id']: {'mainDepartmentId': product_database['mainDepartmentId']}})

        self._product_controller.update_products_api(products_department_update)

    def update_api_brands(self):
        products_brands_update = {}
        for product_api in self._products_api:
            if product_api['erpId'] not in self.excludes:
                products_database = filter(lambda x: x['erpId'] == product_api['erpId'], self._products_database)
                products_database = list(products_database)

                if len(products_database) == 0:
                    generate_log('product erpId: {} not found in database'.format(product_api['erpId']))

                for product_database in products_database:
                    if product_database['mainDepartmentId'] < 0:
                        generate_log('product erpId:{} brand not update because mainDepartmentId is null!'.format(
                            product_database['erpId']))
                        continue

                    if 'brand' in product_database:
                        list_update = {}
                        brand = product_database['brand']['name']

                        if product_api['marketplaceManufacturerName'] != brand:
                            name = self.remove_special_char(product_api['name'])
                            list_update.update({'marketplaceProductName': name})
                            list_update.update({'marketplaceDescription': name})
                            list_update.update({'marketplaceManufacturerName': brand})
                            products_brands_update.update({product_api['id']: list_update})

        self._product_controller.update_products_api(products_brands_update)

    def update_api_filters(self):
        products_filters_update = {}
        for product_api in self._products_api:
            if product_api['erpId'] not in self.excludes:
                products_database = filter(lambda x: x['erpId'] == product_api['erpId'], self._products_database)
                products_database = list(products_database)

                if len(products_database) == 0:
                    generate_log('product erpId: {} not found in database'.format(product_api['erpId']))

                for product_database in products_database:
                    if product_database['mainDepartmentId'] < 0:
                        generate_log('product erpId:{} filters not update because mainDepartmentId is null!'.format(
                            product_database['erpId']))
                        continue

                    if ('filters' in product_database) and ('filters' in product_api):
                        database_filters = product_database['filters']
                        api_filters = product_api['filters']

                        for database_field in database_filters:
                            api_field = self.get_field(api_filters, database_field['name'])
                            if api_field is None:
                                products_filters_update.update(
                                    {product_api['id']: {'filters': product_database['filters']}})
                                print('Add field database_fields {} api_fields: {}'.format(database_field, api_filters))
                            else:
                                if api_field['values'] != database_field['values']:
                                    products_filters_update.update(
                                        {product_api['id']: {'filters': product_database['filters']}})
                                    print(
                                        'Add field database_fields {} api_fields: {}'.format(database_field, api_filters))

        self._product_controller.update_products_api(products_filters_update)

    def get_field(self, list_field, name_field):
        result = None
        for field in list_field:
            if self.remove_special_char(field['name'].upper()) == self.remove_special_char(name_field.upper()):
                result = field
                continue

        return result

    @staticmethod
    def remove_special_char(string):
        nfkd = unicodedata.normalize('NFKD', string)
        clean_string = u"".join([c for c in nfkd if not unicodedata.combining(c)])
        return re.sub('[^a-zA-Z0-9 \\\]', '', clean_string)


# application = Application()
# application.synchronize()
