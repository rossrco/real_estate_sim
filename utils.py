import math
import collections
import pandas as pd
from IPython.display import clear_output


def get_price_index(year_growth_rate, month):
    return math.pow(1 + year_growth_rate/12, month)


Payment = collections.namedtuple('Payment', ['interest_amount',
                                             'capital_downpayment'])


class Mortgage:
    def __init__(self, interest_rate, mortgage_amount, maturity,
                 n_periods=12):
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
    
    def get_next_payment(self):
        if self.mortgage_amount > 0:
            interest_amount = self.get_interest_amount()
            capital_downpayment_amount = self.get_capital_downpayment()
            payment = Payment(interest_amount,
                              capital_downpayment_amount)
            self.remaining_periods -= 1
            self.mortgage_amount -= capital_downpayment_amount
            self.mortgage_amount = max(self.mortgage_amount, 0)
        else:
            payment = Payment(0, 0)
            self.remaining_periods -= 1
        return payment


class RealEstate:
    def __init__(self, purchase_price, mortgage):
        self.purchase_price = purchase_price
        self.current_price = purchase_price
        self.mortgage = mortgage
        self.history = {'mortgage_amount': [],
                        'price_index': [],
                        'current_price': [],
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
                'purchase_price_stocks': self.purchase_price,
                'current_price': self.current_price,
                'value_stocks': self.value}


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


class Scenario:
    def __init__(self, real_estate, portfolio, growth_rate_real_estate,
                 growth_rate_stocks, initial_price_stocks,
                 mortgage_overpayment_amount, investment_amount, name=None):
        self.real_estate = real_estate
        self.portfolio = portfolio
        self.growth_rate_real_estate = growth_rate_real_estate
        self.growth_rate_stocks = growth_rate_stocks
        self.initial_price_stocks = initial_price_stocks
        self.mortgage_overpayment_amount = mortgage_overpayment_amount
        self.investment_amount = investment_amount
        if name is None:
            self.name = '{}_{}_{}_{}'.format(self.growth_rate_real_estate,
                                             self.growth_rate_stocks,
                                             self.mortgage_overpayment_amount,
                                             self.investment_amount)
        else:
            self.name = name
        self.history = None
        self.profit_real_estate = 0,
        self.profit_stocks = 0


    def update_profit(self):
        self.profit_real_estate = (self.history['current_price_real_est'].iloc[-1]
                                   - self.history['current_price_real_est'].iloc[0]
                                   - self.history['interest_amount'].sum())
        self.profit_stocks = self.history['profit_stocks'].sum()



    def update_history(self):
        real_estate_hist = pd.DataFrame(self.real_estate.history)
        portfolio_purchases = [row.to_dict()
                               for row in self.portfolio.purchases]
        portfolio_hist = pd.DataFrame.from_records(portfolio_purchases).drop('invested_amount', axis=1)
        self.history = real_estate_hist.join(portfolio_hist,
                                             lsuffix='_real_est',
                                             rsuffix='_stocks')
        self.history['scenario_name'] = self.name
        self.history['growth_rate_real_estate'] = self.growth_rate_real_estate
        self.history['growth_rate_stocks'] = self.growth_rate_stocks
        self.history['mortgage_overpayment_amount'] = self.mortgage_overpayment_amount
        self.history['investment_amount'] = self.investment_amount
        self.history['month'] = [i for i in range(len(self.history))]
        self.history['profit_stocks'] = (self.history['value_stocks']
                                         - self.history['investment_amount'])
        self.history['cumulative_interest_amount'] = self.history['interest_amount'].cumsum()
        self.history['cumulative_profit_stocks'] = self.history['profit_stocks'].cumsum()
        self.history['current_profit_real_estate'] =\
            ([self.history['current_price_real_est'].iloc[i]
             - self.history['current_price_real_est'].iloc[0]
             - self.history['cumulative_interest_amount'].iloc[i]
             for i in range(len(self.history))])
        self.history['profit_ratio'] = (self.history['current_profit_real_estate']
                                        / self.history['cumulative_profit_stocks'])
        self.history['profit_diff'] = (self.history['current_profit_real_estate']
                                       - self.history['cumulative_profit_stocks'])
        return self

    def run(self):
        month = 0
        maturity = self.real_estate.mortgage.maturity
        n_periods = self.real_estate.mortgage.n_periods
        max_periods = maturity * n_periods
        new_monthly_payment_amount = (self.real_estate.mortgage.monthly_payment
                                      + self.mortgage_overpayment_amount)
        self.real_estate\
            .mortgage.update_monthly_payment_amount(new_monthly_payment_amount)
        while month <= max_periods:
            real_estate_price_index = get_price_index(self.growth_rate_real_estate, month)
            self.real_estate.tick_month(real_estate_price_index)
            stock_price = (get_price_index(self.growth_rate_stocks, month)
                           * self.initial_price_stocks)
            self.portfolio.purchase(self.investment_amount, stock_price)
            self.portfolio.update_values(stock_price)
            month += 1
        self.update_history()
        self.update_profit()


class Simulation:
    def __init__(self, scenarios):
        self.scenarios = scenarios
        self.history = pd.DataFrame()
        self.profit = pd.DataFrame()

    def simulate(self):
        profit_data = []
        profit_cols = ['scenario_name', 'profit_real_estate', 'profit_stocks',
                       'growth_rate_real_estate', 'growth_rate_stocks',
                       'mortgage_overpayment_amount', 'investment_amount']

        for i, scenario in enumerate(self.scenarios):
            scenario.run()
            self.history = self.history.append(scenario.history, ignore_index=True)
            profit_data.append([scenario.name, scenario.profit_real_estate,
                                scenario.profit_stocks, scenario.growth_rate_real_estate,
                                scenario.growth_rate_stocks, scenario.mortgage_overpayment_amount,
                                scenario.investment_amount])
            clear_output()
            print(f'Completed scenario {i}.')

        self.profit = pd.DataFrame(profit_data, columns=profit_cols)
