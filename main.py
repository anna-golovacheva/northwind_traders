import json

def prepare_data(data_list: list) -> list:
    """
    Готовит данные для записи в sql файл: экранирует апострофы будущих значений.
    Возвращает список словарей с экранированными апострофами в значениях.
    """
    refactored_data = []
    for data in data_list:
        refactored_suppliers_data = {k: v.replace("'", "''") for k, v in data.items() if k != 'products'}
        refactored_data.append(refactored_suppliers_data)

    return refactored_data


def convert_data_for_request(list_of_data: list) -> list:
    """
    Собирает из списка словарей нужные значения для дальнейшей записи в поля
    таблицы. Преобразует их в строковый вид. Возвращает список строк.
    """
    list_of_values_strings = []
    for data in list_of_data:
        list_to_upload = []

        company_name = data['company_name']
        list_to_upload.append(company_name)

        contact = data['contact'].split(', ')
        contact_name, contact_job_title = contact[0], contact[1]
        list_to_upload.extend([contact_name, contact_job_title])

        address = data['address'].split('; ')
        address_country, address_state, address_index, address_city, address_local = address[0], address[1], address[2], address[3], address[4]
        list_to_upload.extend([address_country, address_state, address_index, address_city, address_local])

        phone, fax, homepage = data['phone'], data['fax'], data['homepage']
        list_to_upload.extend([phone, fax, homepage])

        list_to_upload = ["'" + val + "'" for val in list_to_upload]
        values = ",".join(list_to_upload)

        list_of_values_strings.append(values)

    return list_of_values_strings


def create_and_fill_new_table(file_name: str, val_list: list) -> str:
    """
    Записывает код в sql файл для создания таблицы и заполнения ее данными.
    """
    with open(file_name, 'w', encoding='utf-8') as sql_file_1:
        settings = f"SET statement_timeout = 0;\n" \
                   f"SET lock_timeout = 0;\n" \
                   f"SET client_encoding = 'UTF8';\n" \
                   f"SET standard_conforming_strings = on;\n" \
                   f"SET check_function_bodies = false;\n" \
                   f"SET client_min_messages = warning;\n" \
                   f"SET default_tablespace = '';\n" \
                   f"SET default_with_oids = false;\n\n"
        sql_file_1.write(settings)

        create_table = f"CREATE TABLE IF NOT EXISTS suppliers (" \
                       f"id_supplier SERIAL PRIMARY KEY, " \
                       f"company_name VARCHAR(60), " \
                       f"contact_name VARCHAR(30), " \
                       f"contact_job_title VARCHAR(30), " \
                       f"address_country VARCHAR(30), " \
                       f"address_state VARCHAR(30), " \
                       f"address_index VARCHAR(10), " \
                       f"address_city VARCHAR(30), " \
                       f"address_local VARCHAR(100), " \
                       f"phone VARCHAR(20), " \
                       f"fax VARCHAR(20), " \
                       f"homepage VARCHAR(100)" \
                       f");\n"
        sql_file_1.write(create_table)

        for val in val_list:
            insert_val = f"INSERT INTO suppliers (company_name, contact_name, contact_job_title, " \
                         f"address_country, address_state, address_index, address_city, address_local, " \
                         f"phone, fax, homepage) " \
                         f"VALUES ({val});\n"
            sql_file_1.write(insert_val)

    return 'Code sent to sql file'


def refactor_existing_table(file_name: str, data_list: list):
    """
    Записывает код в sql файл для создания нового поля уже существующей таблицы и
    заполнения ее данными.
    """
    with open(file_name, 'w', encoding='utf-8') as sql_file_2:
        settings = f"SET statement_timeout = 0;\n" \
                   f"SET lock_timeout = 0;\n" \
                   f"SET client_encoding = 'UTF8';\n" \
                   f"SET standard_conforming_strings = on;\n" \
                   f"SET check_function_bodies = false;\n" \
                   f"SET client_min_messages = warning;\n" \
                   f"SET default_tablespace = '';\n" \
                   f"SET default_with_oids = false;\n\n"
        sql_file_2.write(settings)

        create_column = """ALTER TABLE products ADD COLUMN supplier_id INTEGER;\n"""
        sql_file_2.write(create_column)

        count = 1
        for data in data_list:
            data['id'] = count
            refactored_products = [product.replace("'", "''") for product in data['products']]
            update_products = f"""UPDATE products SET supplier_id = {data['id']} WHERE product_name IN ('{"', '".join(refactored_products)}');\n"""
            sql_file_2.write(update_products)
            count += 1

        foreign_key_set = f"\nALTER TABLE products ADD FOREIGN KEY (supplier_id) " \
                      f"REFERENCES suppliers(id_supplier);\n"
        sql_file_2.write(foreign_key_set)

    return 'Code sent to sql file'


def main():
    with open('suppliers.json', 'r', encoding='utf-8') as file:
        suppliers_data = json.load(file)

    prepared_data = prepare_data(suppliers_data)

    list_of_values = convert_data_for_request(prepared_data)

    sql_file_1 = 'create_and_fill_table.sql'
    print(create_and_fill_new_table(sql_file_1, list_of_values))

    sql_file_2 = 'update_table.sql'
    print(refactor_existing_table(sql_file_2, suppliers_data))


if __name__ == '__main__':
    main()
