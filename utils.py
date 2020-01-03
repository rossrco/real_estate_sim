import math
import collections


Payment = collections.namedtuple('Payment', ['fee', 'interest_amount', 'capital_downpayment_amount'])


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