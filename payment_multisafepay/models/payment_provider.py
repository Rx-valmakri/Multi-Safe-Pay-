# -*- coding: utf-8 -*-
from odoo import models, fields, api, service
from odoo.exceptions import UserError, ValidationError

import logging
import requests
from werkzeug import urls


from odoo.addons.payment_multisafepay import const

_logger = logging.getLogger(__name__)


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('multisafepay', "Multi Safe Pay")],
        ondelete={'multisafepay': 'set default'}
    )
    multisafepay_key_id = fields.Char(string="multisafepay key id",
                                      help="The key solely used to identify the account with multisafepay.",)

    @api.onchange('multisafepay_key_id')
    def _onchange_multisafepay_api_key(self):
        if self.multisafepay_key_id and len(self.multisafepay_key_id) != 40:
            raise UserError('An API key must be 40 characters long')

    def _get_supported_currencies(self):
        """ Override of `payment` to return the supported currencies. """
        supported_currencies = super()._get_supported_currencies()
        if self.code == 'multisafepay':
            supported_currencies = supported_currencies.filtered(
                lambda c: c.name in const.SUPPORTED_CURRENCIES
            )
        return supported_currencies

    def _get_default_payment_method_codes(self):
        """ Override of `payment` to return the default payment method codes. """
        default_codes = super()._get_default_payment_method_codes()
        if self.code != 'multisafepay':
            return default_codes
        return const.DEFAULT_PAYMENT_METHODS_CODES

    def _multisafepay_make_request(self, endpoint, data=None, method='POST'):
        """ Make a request at multisafepay endpoint.

                Note: self.ensure_one()

                :param str endpoint: The endpoint to be reached by the request
                :param dict data: The payload of the request
                :param str method: The HTTP method of the request
                :return The JSON-formatted content of the response
                :rtype: dict
                :raise: ValidationError if an HTTP error occurs
                """
        self.ensure_one()
        endpoint = f'/v1/json/{endpoint.strip("/")}'
        url = urls.url_join('https://testapi.multisafepay.com/', endpoint)
        odoo_version = service.common.exp_version()['server_version']
        module_version = self.env.ref('base.module_payment_multisafepay').installed_version

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": f'Odoo/{odoo_version} (MultiSafePayNativeOdoo {module_version})',
        }
        try:
            response = requests.request(method, url, json=data, headers=headers, timeout=60)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            _logger.exception("Unable to reach endpoint at %s", url)
            raise ValidationError("MultiSafePay: Could not establish the connection to the API.")

        return response.json()
