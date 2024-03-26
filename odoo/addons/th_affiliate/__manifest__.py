# -*- coding: utf-8 -*-
{
    'name': 'ABS Affiliate',
    'author': "TH Company",
    'summary': 'ABS Affiliate',
    'category': 'AUM Business System/ Affiliate',
    'website': 'https://aum.edu.vn/',
    'license': 'LGPL-3',
    'depends': [
        'report_xlsx',
        'link_tracker',
        'portal',
        'mail',
        'th_contact',
        'web_domain_field',

    ],
    'data': [

        'data/ir_sequence.xml',
        'data/th_warehouse_data.xml',
        'security/link_tracker_security.xml',
        'security/ir.model.access.csv',
        'views/th_link_seeding.xml',
        'views/link_tracker_views.xml',
        'views/th_pricelist.xml',

        'views/res_config_settings_views.xml',
        'views/th_aff_ownership_unit.xml',
        'views/utm.xml',
        'views/th_product_aff_category.xml',
        'views/th_pay.xml',
        'views/th_post_link.xml',
        'views/th_session_user.xml',
        'views/th_product_line.xml',
        'views/th_popup_res_users.xml',
        'views/th_warehouse_views.xml',
        'views/th_landing_page_view.xml',
        'views/th_opportunity_view.xml',
        'views/th_payment_batch.xml',
        'views/th_collaborator_group.xml',
        
        'views/th_product_aff.xml',
        'views/th_product_image.xml',
        'views/th_aff_order.xml',
        'views/th_module.xml',
        'views/th_date_click.xml',
        # 'wizards/batch_update_create_link.xml',

        # 'wizard/import_opprtunity_view.xml',
        'report/report.xml',
        'views/menus.xml',
    ],

    'qweb': [
        'static/src/xml/*.xml',

    ],
    'assets': {
        'web.assets_frontend': [
            # 'th_affiliate/static/src/scss/main.scss',
        ],
        'web.assets_backend': [
            # 'th_affiliate/static/src/scss/main.scss'
            'th_affiliate/static/src/xml/*.xml',
            'th_affiliate/static/src/js/th_main.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
