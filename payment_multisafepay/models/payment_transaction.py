# -*- coding: utf-8 -*-
import logging
from werkzeug import urls
import requests

from odoo import models
from odoo.addons.payment_multisafepay.controllers.main import MultiSafePayController

from odoo.exceptions import ValidationError


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _get_specific_rendering_values(self, processing_values):
        """ Override of payment to return multisafepay-specific rendering values.

        Note: self.ensure_one() from `_get_processing_values`

        :param dict processing_values: The generic and specific processing values of the transaction
        :return: The dict of provider-specific processing values
        :rtype: dict
        """
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'multisafepay':
            return res

        payload = self._multisafepay_prepare_payment_request_payload()
        print("payload : ", payload)
        payment_data = self.provider_id._multisafepay_make_request(f"/orders?api_key={self.provider_id.multisafepay_key_id}", data=payload)
        print("payment data : ", payment_data)
        return {
            'api_url': payment_data['data']['payment_url']
        }

    def _multisafepay_prepare_payment_request_payload(self):
        """ Create the payload for the payment request based on the transaction values.

        :return: The request payload
        :rtype: dict
        """
        amount_in_cents = self.amount * 100
        base_url = self.provider_id.get_base_url()
        return {
            "type": "redirect",
            "order_id": self.reference,
            # "gateway": "",
            "currency": self.currency_id.name,
            "amount": amount_in_cents,
            "description": self.reference,
            "payment_options": {
                "notification_url": urls.url_join(base_url, MultiSafePayController.notification_url),
                "notification_method": "POST",
                "redirect_url": urls.url_join(base_url, MultiSafePayController.redirect_url),
                "cancel_url": urls.url_join(base_url, MultiSafePayController.cancel_url),
            },
            "customer": {
                "first_name": self.partner_name,
                "last_name": self.partner_name,
                "address1": self.partner_address,
                "zip_code": self.partner_zip,
                "city": self.partner_city,
                "country": self.partner_country_id.name,
                "phone": self.partner_phone,
                "email": self.partner_email,
            }
        }

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        """ Override of payment to find the transaction based on multisafepay data.

        :param str provider_code: The code of the provider that handled the transaction
        :param dict notification_data: The notification data sent by the provider
        :return: The transaction if found
        :rtype: recordset of `payment.transaction`
        :raise: ValidationError if the data match no transaction
        """
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != 'multisafepay' or len(tx) == 1:
            return tx
        print("transaction id : ", notification_data.get('transactionid'))
        tx = self.search(
            [('reference', '=', notification_data.get('transactionid')),
             ('provider_code', '=', 'multisafepay')]
        )
        print(tx)
        if not tx:
            raise ValidationError("Multi Safe Pay: No transaction found matching reference %s.", notification_data.get('transactionid'))
        return tx

    def _process_notification_data(self, notification_data):
        """ Override of payment to process the transaction based on MultiSafePay data.

        Note: self.ensure_one()

        :param dict notification_data: The notification data sent by the provider
        :return: None
        """
        super()._process_notification_data(notification_data)
        if self.provider_code != 'multisafepay':
            return

        order_id = notification_data.get('transactionid')
        url = f"https://testapi.multisafepay.com/v1/json/orders/{order_id}?api_key={self.provider_id.multisafepay_key_id}"
        headers = {"accept": "application/json"}
        response = requests.get(url, headers=headers)

        # Update the payment state.
        payment_status = response.json().get("data").get("status")
        print(payment_status)
        if payment_status == 'completed':
            self._set_done()
        elif payment_status in ['expired', 'void', 'declined', 'uncleared', 'initialized']:
            self._set_canceled(f"Multi Safe Pay: Canceled payment with status:   {payment_status}")


