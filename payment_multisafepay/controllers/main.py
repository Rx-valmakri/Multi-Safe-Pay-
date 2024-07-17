# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class MultiSafePayController(http.Controller):
    redirect_url = '/payment/multisafepay/return'
    cancel_url = '/payment/multisafepay/cancel'
    notification_url = '/payment/multisafepay/webhook'

    @http.route(
        redirect_url, type='http', auth='public', methods=['GET', 'POST'],
        csrf=False,
        save_session=False
    )
    def multisafepay_return_from_checkout(self, **data):
        request.env['payment.transaction'].sudo()._handle_notification_data(
            'multisafepay', data)
        return request.redirect('/payment/status')

    @http.route(cancel_url, type='http', auth='public', csrf=False, save_session=False)
    def multisafepay_cancel_from_payment(self, **data):
        request.env['payment.transaction'].sudo()._handle_notification_data(
            'multisafepay', data)
        return request.redirect('/payment/status')

    @http.route(notification_url, type='http', auth='public', csrf=False)
    def multisafepay_notification(self, **data):
        print("multisafepay_notification_url : data = ", data)
