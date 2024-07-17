# Part of Odoo. See LICENSE file for full copyright and licensing details.

# currencies supported by PayPal
# See https://docs.multisafepay.com/docs/currencies.

SUPPORTED_CURRENCIES = (
    'AUD',
    'CAD',
    'CHF',
    'USD',
    'EUR',
    'DKK',
    'GBP',
    'HKD',
    'NOK',
    'PLN',
    'SEK',
)

# The codes of the payment methods to activate when MultiSafePay is activated.
DEFAULT_PAYMENT_METHODS_CODES = [
    # Primary payment methods.
    'multisafepay',
]
