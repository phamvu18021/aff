{
    'name': 'ABS Contact',
    'author': "TH Company",
    'summary': 'ABS Contact',
    'category': 'AUM Business System/ Contact',
    'website': 'https://aum.edu.vn/',
    'license': 'LGPL-3',
    'depends': [
        'contacts',
        'th_base',
    ],
    'data': [
        'data/ir_sequence.xml',
        'security/ir.model.access.csv',
        'views/res_partner.xml',
        'views/th_country_district_view.xml',
        'views/th_country_ward_view.xml',
        'views/th_menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
