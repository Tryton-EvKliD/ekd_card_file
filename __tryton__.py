# -*- coding: utf-8 -*-
#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
{
    'name': 'Card File',
    'name_ru_RU': 'Картотека',
    'version': '1.8.0',
    'author': 'Dmitry Klimanov',
    'email': 'k-dmitry2@narod.ru',
    'website': 'http://www.tryton.org/',
    'description': '''Card File:
''',
    'description_ru_RU': '''Картотека:
    - Основных средст
    - Материалов
    - Заказчиков
    - Поставщиков
''',
    'depends': [
        'ir',
        'res',
        'party',
        'company',
        'ekd_product',
        'ekd_account',
    ],
    'xml': [
        'xml/ekd_card_file_view.xml',
    ],
    'translation': [
        'ru_RU.csv',
    ],
}
