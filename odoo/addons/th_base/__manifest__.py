{
    'name': 'ABS Base',
    'author': "TH Company",
    'summary': 'ABS Base',
    'category': 'AUM Business System/ Base',
    'website': 'https://aum.edu.vn/',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'web',
    ],
    'data': [
        # 'data/mail_template_th.xml',
        'security/ir.model.access.csv',
        'views/th_api.xml',
        'views/res_config_settings.xml',
    ],

    'assets': {
        'web.assets_backend': [
            # 'th_base/static/src/scss/change_css_base.scss',
            'th_base/static/src/js/import_action.js',
            # 'th_base/static/src/js/url_widget.js',
        ],
    },
    'installable': True,
    'auto_install': True,
}
