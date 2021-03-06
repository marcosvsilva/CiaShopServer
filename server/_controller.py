import json
from _request import Request
from _config import Config, generate_log
from _connection import Connection


class Controller:

    def __init__(self):
        self.__request = Request()
        self.__connection = Connection()

    def _get_api(self, table):
        try:
            return self.__request.get_list(table)
        except Exception as fail:
            raise Exception(fail)

    def _update_api(self, table, products_update):
        try:
            return self.__request.put_list(table, products_update)
        except Exception as fail:
            raise Exception(fail)

    def _get_database(self, sql_table, sql_query, table_columns):
        try:
            json_file = self.__connection.sql_query(sql_query, table_columns)
            self._export_json('database_{}'.format(sql_table), json_file)
            return json_file
        except Exception as fail:
            raise Exception(fail)

    def _update_database(self, sql_update, list_update):
        try:
            self.__connection.sql_update(sql_update, list_update)
        except Exception as fail:
            raise Exception(fail)

    def _update_database_with_script(self, sql_update):
        try:
            self.__connection.sql_execute(sql_update)
        except Exception as fail:
            raise Exception(fail)

    def _get_sql(self, file_sql):
        try:
            return self.__connection.get_file_sql(file_sql)
        except Exception as fail:
            raise Exception('fail find sql file, fail: {}'.format(fail))

    @staticmethod
    def _export_json(archive_name, archive):
        try:
            config = Config()
            if config.get_key('export_requests_json') == 'yes':
                if len(archive) > 1:
                    with open('{}.json'.format(archive_name), 'w') as file:
                        json.dump(archive, file)
                else:
                    raise Exception('archive {} is empty'.format(archive_name))
        except Exception as fail:
            raise Exception('fail to export json request, archive: {}, fail: {}'.format(archive_name, fail))


class ProductController(Controller):

    def __init__(self):
        super().__init__()

    def get_products_api(self):
        try:
            return self._get_api('products')    
        except Exception as fail:
            raise Exception('fail get products to api, fail: {}'.format(fail))

    def update_products_api(self, products_update):
        try:
            if len(products_update) > 0:
                return self._update_api('products', products_update)
            else:
                return None
        except Exception as fail:
            raise Exception('fail update products to api, fail: {}'.format(fail))

    def get_products_database(self):
        try:
            columns_products = ['erpId', 'id', 'variantId', 'mainDepartmentId', 'brand']
            columns_filters = ['erpId', 'name', 'values']
            products = self._get_database('products', self._get_sql('get_products.sql'), columns_products)
            filters_products = self._get_database('filter', self._get_sql('get_filters.sql'), columns_filters)

            if (len(products) > 0) and (len(filters_products) > 0):
                for product in products:
                    product = self.__add_brand_product(product)
                    filters = filter(lambda x: x['erpId'] == product['erpId'], filters_products)
                    for filter_product in filters:
                        self.__add_filter_product(product, filter_product)

            self._export_json('database_products_final', products)
            return products
        except Exception as fail:
            raise Exception('fail to database request products, fail: {}'.format(fail))

    def update_products_database(self, keys_values):
        for key, value in keys_values.items():
            try:
                list_update = [(value, key)]
                sql_update = self._get_sql('update_csi_id_products.sql')
                self._update_database(sql_update, list_update)
                generate_log('update database: product {} ciashop_id {}'.format(key, str(value)))
            except Exception as fail:
                raise Exception('fail to database update product {}, fail: {}'.format(key, fail))

    def update_variants_database(self, keys_values):
        for key, value in keys_values.items():
            try:
                list_update = [(value, key)]
                sql_update = self._get_sql('update_csi_id_variants.sql')
                self._update_database(sql_update, list_update)
                generate_log('update database: product {} variants_id {}'.format(key, str(value)))
            except Exception as fail:
                raise Exception('fail to database update product variants {}, fail: {}'.format(key, fail))

    def update_department_id(self):
        try:
            sql_script = self._get_sql('script_update_deparment_products.sql')
            self._update_database_with_script(sql_script)
        except Exception as fail:
            raise Exception('fail to execute script update deparment products, fail: {}'.format(fail))

    @staticmethod
    def __add_filter_product(product, filter_product):
        list_filters = []
        if 'filters' in product:
            list_filters = product['filters']

        list_filters.append({'name': filter_product['name'], 'values': [filter_product['values']]})
        product['filters'] = list_filters
        return product

    @staticmethod
    def __add_brand_product(product):
        brand_value = product['brand']
        product['brand'] = {'name': brand_value}
        return product


class DepartmentController(Controller):
    
    def __init__(self):
        super().__init__()

    def get_departments_api(self):
        try:
            return self._get_api('departments')    
        except Exception as fail:
            raise Exception('fail get departments to api, fail: {}'.format(fail))

    def update_departments_api(self, departments_update):
        try:
            return self._update_api('departments', departments_update)
        except Exception as fail:
            raise Exception('fail update departments to api, fail: {}'.format(fail))

    def get_departments_database(self):
        try:
            columns_departments = ['erpId', 'id']
            departments = self._get_database('departments', self._get_sql('get_departments.sql'), columns_departments)

            self._export_json('database_departments', departments)
            return departments
        except Exception as fail:
            raise Exception('fail to database request departments, fail: {}'.format(fail))

    def update_departments_database(self, keys_values):
        for key, value in keys_values.items():
            try:
                list_update = [(value, key)]
                sql_update = self._get_sql('update_csi_id_departments.sql')                
                self._update_database(sql_update, list_update)
                generate_log('update database: departments {} ciashop_id {}'.format(str(key), str(value)))
            except Exception as fail:
                raise Exception('fail to database update departments {}, fail: {}'.format(key, fail))

    def update_departments_products_database(self, keys_values):
        for key, value in keys_values.items():
            try:
                list_update = [(value, key)]
                sql_update = self._get_sql('update_csi_id_departament_products.sql')
                self._update_database(sql_update, list_update)
                generate_log('update database: departments {} ciashop_id {}'.format(key, str(value)))
            except Exception as fail:
                raise Exception('fail to database update departments {}, fail: {}'.format(key, fail))
