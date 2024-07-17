# -*- coding: utf-8 -*-
{
    'name': "Payment Provider: Multi Safe Pay",
    'category': 'Accounting/Payment Providers',
    'summary': "Multi Safe Pay : A payment provider",
    'description': " ",  # Non-empty string to avoid loading the README file.
    'depends': ['payment'],
    'data': [
             'views/payment_multisafepay_templates.xml',
             'views/payment_provider_views.xml',

             'data/payment_method_data.xml',
             'data/payment_provider_data.xml',
             ],
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
}