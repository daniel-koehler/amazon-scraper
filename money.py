from decimal import Decimal, ROUND_HALF_UP
from typing import Union
import requests
import json
import locale

locale.setlocale(locale.LC_ALL, '')

#TODO: implement currencies as class/enum
CURRENCY_MAP = {
        '€': 'EUR',
        '$': 'USD',
        '£': 'GBP'
    }

class InvalidCurrencyError(Exception):
    def __init__(self, currency: str):
        super().__init__('Invalid currency ' + currency)

class Money:

    """ Class to handle monetary quantities as Decimal """

    def __init__(self, quantity: Union[str, Decimal], currency: str='€'):
        """ 
        Args
            'quantity' -- amount of money as string or Decimal
            'currency' -- symbol of the corresponding currency
        """
        
        if isinstance(quantity, str):
            self._quantity = Decimal(locale.delocalize(quantity))
        elif isinstance(quantity, Decimal):
            self._quantity = quantity
        else:
            raise(ValueError)

        if currency not in CURRENCY_MAP:
            raise InvalidCurrencyError(currency)
        self._currency = currency

    def __repr__(self) -> str:
        return '{:.2f}{}'.format(self._quantity, self._currency)

    def __lt__(self, other: 'Money'):
        if not isinstance(other, Money):
            raise TypeError
        return self._quantity < other._quantity

    def __gt__(self, other: 'Money'):
        if not isinstance(other, Money):
            raise TypeError
        return self._quantity > other._quantity

    def __le__(self, other: 'Money'):
        if not isinstance(other, Money):
            raise TypeError
        return self._quantity <= other._quantity

    def __ge__(self, other: 'Money'):
        if not isinstance(other, Money):
            raise TypeError
        return self._quantity >= other._quantity

    def __eq__(self, other: 'Money'):
        if not isinstance(other, Money):
            raise TypeError
        return self._quantity == other._quantity

    def __add__(self, other: 'Money') -> 'Money':
        if not isinstance(other, Money):
            raise TypeError
        return self.__class__(str(self._quantity + other._quantity), self.currency)

    def __sub__(self, other: 'Money') -> 'Money':
        if not isinstance(other, Money):
            raise TypeError
        return self.__class__(str(self._quantity - other._quantity), self.currency)

    def __mul__(self, other: 'Money') -> 'Money':
        if not isinstance(other, Money):
            raise TypeError
        return self._round(Money(self._quantity * other._quantity, self.currency))

    @property
    def quantity(self) -> Decimal:
        return self._quantity

    @property
    def currency(self) -> Decimal:
        return self._currency

    @staticmethod
    def _round(m: 'Money') -> 'Money':
        m = Money(m.quantity.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP), m._currency)
        return m

    @staticmethod
    def convert_currency(m: 'Money', currency: 'Money') -> 'Money':
        """ Exchanges 'm' into the given currency """
        if not isinstance(m, Money):
            raise TypeError

        if m.currency == currency:
            return m
        
        try:
            page = requests.get('https://api.ratesapi.io/api/latest?base={}&symbols={}'.format(CURRENCY_MAP[m.currency], CURRENCY_MAP[currency]))
        except KeyError:
            raise InvalidCurrencyError(currency)

        exchange_rate = Decimal(json.loads(page.content)['rates'][CURRENCY_MAP[currency]])
        return Money(m.quantity * exchange_rate, currency)

    

    

    