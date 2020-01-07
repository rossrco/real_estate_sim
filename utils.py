import math
import collections


Payment = collections.namedtuple('Payment', ['fee', 'interest_amount', 'capital_downpayment'])


class Mortgage:
    def __init__(self, service_fee, interest_rate, mortgage_amount, maturity, n_periods=12):
        self.service_fee = service_fee
        self.interest_rate = interest_rate
        self.mortgage_amount = mortgage_amount
        self.maturity = maturity
        self.n_periods = n_periods
        self.remaining_periods = maturity * n_periods
        self.annuity_factor = self.get_annuity_factor()
        self.monthly_payment = self.get_monthly_payment()
    
    def get_annuity_factor(self):
        interest_rate_amount_increase = (math.pow((1 + self.interest_rate
                                                   / self.n_periods),
                                                  self.remaining_periods))
        annuity_factor = ((interest_rate_amount_increase - 1)
                          / ((self.interest_rate/self.n_periods)
                             * interest_rate_amount_increase))
        return annuity_factor

    def get_monthly_payment(self):
        self.annuity_factor = self.get_annuity_factor()
        return self.mortgage_amount / self.annuity_factor
    
    def get_interest_amount(self):
        return self.mortgage_amount * (self.interest_rate / self.n_periods)

    def get_capital_downpayment(self):
        interest_amount = self.get_interest_amount()
        return self.monthly_payment - interest_amount
    
    def update_interest_rate(self, new_interest_rate):
        self.interest_rate = new_interest_rate
        self.annuity_factor = self.get_annuity_factor()
        new_monthly_payment = self.get_monthly_payment()
        self.update_monthly_payment_amount(new_monthly_payment)
        return self
    
    def update_monthly_payment_amount(self, new_monthly_payment):
        self.monthly_payment = new_monthly_payment
        return self

    def update_service_fee(self, new_service_fee):
        self.service_fee = new_service_fee
        return self
    
    def get_next_payment(self):
        interest_amount = self.get_interest_amount()
        capital_downpayment_amount = self.get_capital_downpayment()
        payment = Payment(self.service_fee, interest_amount, capital_downpayment_amount)
        self.remaining_periods -= 1
        self.mortgage_amount -= capital_downpayment_amount
        return payment


class RealEstate:
    def __init__(self, purchase_price, mortgage):
        self.purchase_price = purchase_price
        self.current_price = purchase_price
        self.mortgage = mortgage
        self.history = {'mortgage_amount': [],
                        'price_index': [],
                        'current_price': [],
                        'fee': [],
                        'interest_amount': [],
                        'capital_downpayment': []}
    
    def tick_month(self, price_index):
        self.history['mortgage_amount'].append(self.mortgage.mortgage_amount)
        self.history['price_index'].append(price_index)
        current_price = self.purchase_price * price_index
        self.history['current_price'].append(current_price)
        current_payment = self.mortgage.get_next_payment()._asdict()
        for key in current_payment:
            self.history[key].append(current_payment[key])


class StockPurchase:
    def __init__(self, amount, purchase_price):
        self.amount = amount
        self.purchase_price = purchase_price
        self.current_price = purchase_price
        self.units = self.amount / self.purchase_price
        self.value = self.units * self.current_price
    
    def update_value(self, current_price):
        self.current_price = current_price
        self.value = self.units * self.current_price
        return self
    
    def to_dict(self):
        return {'invested_amount': self.amount,
                'purchase_price_stock': self.purchase_price,
                'current_price': self.current_price,
                'value_stock': self.value}


class Portfolio:
    def __init__(self):
        self.purchases = []
    
    def purchase(self, amount, purchase_price):
        self.purchases.append(StockPurchase(amount, purchase_price))
        return self
    
    def update_values(self, current_price):
        for purchase in self.purchases:
            purchase.update_value(current_price)
        return self
