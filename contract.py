"""
CSC148, Winter 2025
Assignment 1

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

All of the files in this directory and all subdirectories are:
Copyright (c) 2025 Bogdan Simion, Diane Horton, Jacqueline Smith
"""
import datetime
from math import ceil
from typing import Optional
from bill import Bill
from call import Call


# Constants for the month-to-month contract monthly fee and term deposit
MTM_MONTHLY_FEE = 50.00
TERM_MONTHLY_FEE = 20.00
TERM_DEPOSIT = 300.00

# Constants for the included minutes and SMSs in the term contracts (per month)
TERM_MINS = 100

# Cost per minute and per SMS in the month-to-month contract
MTM_MINS_COST = 0.05

# Cost per minute and per SMS in the term contract
TERM_MINS_COST = 0.1

# Cost per minute and per SMS in the prepaid contract
PREPAID_MINS_COST = 0.025


class Contract:
    """ A contract for a phone line

    This is an abstract class and should not be directly instantiated.

    Only subclasses should be instantiated.

    === Public Attributes ===
    start:
         starting date for the contract
    bill:
         bill for this contract for the last month of call records loaded from
         the input dataset
    """
    start: datetime.date
    bill: Optional[Bill]

    def __init__(self, start: datetime.date) -> None:
        """ Create a new Contract with the <start> date, starts as inactive
        """
        self.start = start
        self.bill = None

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ Advance to a new month in the contract, corresponding to <month> and
        <year>. This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.

        DO NOT CHANGE THIS METHOD
        """
        raise NotImplementedError

    def bill_call(self, call: Call) -> None:
        """ Add the <call> to the bill.

        Precondition:
        - a bill has already been created for the month+year when the <call>
        was made. In other words, you can safely assume that self.bill has been
        already advanced to the right month+year.
        """
        self.bill.add_billed_minutes(ceil(call.duration / 60.0))

    def cancel_contract(self) -> float:
        """ Return the amount owed in order to close the phone line associated
        with this contract.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancelation is requested.
        """
        self.start = None
        return self.bill.get_cost()


# TODO: Implement the MTMContract, TermContract, and PrepaidContract


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'datetime', 'bill', 'call', 'math'
        ],
        'disable': ['R0902', 'R0913'],
        'generated-members': 'pygame.*'
    })


class MTMContract(Contract): 
    def __init__(self, start: datetime.date):
        super().__init__(start)
        self.monthly_fee = MTM_MONTHLY_FEE
        self.min_cost = MTM_MINS_COST
        
    def new_month(self, month: int, year: int, bill: Bill) -> None:
        self.bill = bill
        self.bill.add_fixed_cost(self.monthly_fee)
        self.bill.set_rates("MTM", self.min_cost)
    
class TermContract(Contract):
    def __init__(self, start: datetime.date, end: datetime.date):
        super().__init__(start)
        self.term_min_cost = TERM_MINS_COST
        self.term_deposit = TERM_DEPOSIT
        self.monthly_fee = TERM_MONTHLY_FEE
        self.free_mins_left = TERM_MINS
        self.end = end
        
    def new_month(self, month: int, year: int, bill: Bill) -> None:
        self.period = datetime.date(year, month, 1)
        self.bill = bill
        self.bill.set_rates("TERM", self.term_min_cost)
        self.bill.add_fixed_cost(self.monthly_fee)
        if self.period.month == self.start.month and self.period.year == self.start.year: 
            self.bill.add_fixed_cost(self.term_deposit)
        
    def bill_call(self, call: Call) -> None:
        # use free minute before charging 
        if self.free_mins_left == 0: 
            return super().bill_call(call)
            
        minutes = ceil(call.duration/60)
        self.free_mins_left -= minutes  
        if self.free_mins_left < 0: 
            duration = abs(self.free_mins_left)
            self.bill.add_free_minutes(minutes - duration)
            self.free_mins_left = 0 
            return self.bill.add_billed_minutes(duration)
        else: 
            self.bill.add_free_minutes(minutes)

    def cancel_contract(self) -> float:
        if self.period < self.end:
            return self.bill.get_cost()
        elif self.period > self.end: 
            return self.term_deposit - self.bill.get_cost()
        else: # assume self.period == self.end 
            return self.term_deposit
            
        
class PrepaidContract(Contract):
    def __init__(self, start: datetime, balance: float) -> None:
        super().__init__(start)
        self.balance = -balance
        self.topup = 25
        self.bill = Bill()
        
    def new_month(self, month, year, bill) -> None:
        self.previous_bill = self.bill
        self.balance += self.previous_bill.get_cost()
        while self.balance > -10: 
            self.balance -= self.topup
            
        self.bill = bill
        self.bill.set_rates("PREPAID", PREPAID_MINS_COST)
        self.bill.add_fixed_cost(self.balance)
        
    def cancel_contract(self) -> float:
        if self.balance > 0: 
            return self.balance
        return float(0)
        
        