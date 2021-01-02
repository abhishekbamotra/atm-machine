# -*- coding: utf-8 -*-
"""
Simple ATM Controller
=============================

Author: Abhishek Bamotra
To run: python atm_machine.py

How it does:
    For demo, generates a branch of an imaginary bank, adds two customers and
    opens accounts for them.
    
    Then the ATM operation starts, the customer needs to *insert the card*
    (Enter card no/id and cusomter id which are stored in the magnetic strip
     in real life). Enter the pin to authenticate the user, followed by choosing
    the account user wants to operate. User select the type of transaction to 
    perform.

"""

import uuid

class Bank:
  def __init__(self, bank_name, branch_code, branch_address):
    self.bank_name = bank_name
    self.branch_code = branch_code
    self.branch_address = branch_address
    self.managed_atms = {}
    self.managed_customers = {}
  
  def add_client(self, name, address, dob):
    customer_id = str(uuid.uuid1()).split('-')[0]
    self.managed_customers[customer_id] = Customer(customer_id, 
                                                   name, 
                                                   address, 
                                                   dob)
    return customer_id
  
  def open_account(self, customer_id, initial_balance=0):
    customer_details = self.managed_customers.get(customer_id, None)
    if customer_details is not None:
      new_account_id = str(uuid.uuid1()).split('-')[0]

      # we don't assume ATM cards to have real life 16 digit number
      new_atm_card_id = str(uuid.uuid1()).split('-')[0]
      atm_card = Card(account_id=new_account_id, card_id=new_atm_card_id)
      account = Account(customer_id, self.branch_code, new_account_id, atm_card, initial_balance)
      customer_details.add_account(account)
      # Assumption: We always issue an ATM card for each new account opened

      return new_account_id, new_atm_card_id
    return None
  
  def show_accounts(self):
    for customer_id, customer_details in self.managed_customers.items():
      print(f"Customer id: {customer_details.customer_id}")
      print(f"Showing {customer_details.name}'s accounts: -")
      for account_id, account in customer_details.managed_accounts.items():
        print(f"Account id: {account_id}, account balance: {account.balance}")
        print(f"ATM Card id: {account.atm_card.card_id}")
      print('-' * 100)
    
  def validate_user(self, card_id, customer_id, pin):
    customer = self.managed_customers.get(customer_id, None)
    if customer is None:
      raise Exception("User does not exist in the system")
    customer_accounts = customer.get_accounts()

    for account_id, account_details in customer_accounts.items():
      atm_card = account_details.atm_card
      if atm_card.card_id == card_id and atm_card.pin == pin:
        return customer_accounts
    return None

class Atm:
  def __init__(self, managing_bank_handler, atm_location):
    self.bank = managing_bank_handler
    self.atm_location = atm_location

  def get_card_details(self):
    return input("Please enter card and customer details (seperate by space): ")
  
  def get_pin_number(self):
    return input('Please enter four digit PIN: ')

  def select_account(self):
    return input("Please enter account number: ")
  
  def show_options(self):
    return input("Please choose 1 for Show balance, 2 for Deposit, 3 for withdrawl: ")
  
  def another_txn(self):
    another_txn_flag = ''
    while another_txn_flag not in {'Y', 'N', 'y', 'n'}:
      another_txn_flag = input("Do you want to perform another transaction? (Y or N): ")
    another_txn_flag = another_txn_flag.lower()
    return True if another_txn_flag == 'y' else False
  
  def operate(self):
    card_id, customer_id = self.get_card_details().split(' ')
    pin = self.get_pin_number()
    account_details = self.bank.validate_user(card_id, customer_id, pin)
    if account_details is None:
      print("User verification failed")
    else:
      for account_id, details in account_details.items():
        print(f'Account_id: {account_id}')
      account_id_selected = self.select_account()
      operating_account = account_details.get(account_id_selected, None)
      if operating_account is None:
        raise ValueError("Bad account number was entered.")
      
      txn = True
      while txn:
        selected_txn_type = int(self.show_options())
        while selected_txn_type not in {1, 2, 3}:
          selected_txn_type = int(self.show_options())
        
        if selected_txn_type == 1:
          operating_account.show_balance()
        elif selected_txn_type == 2:
          amount = int(input("Enter deposit amount: "))
          operating_account.deposit(amount)
        elif selected_txn_type == 3:
          amount = int(input("Enter withrawl amount: "))
          operating_account.withdraw(amount)
        
        txn = self.another_txn()
      print('Thank you!')

class Customer:
  def __init__(self, customer_id, name, address, dob):
    self.customer_id = customer_id
    self.name = name
    self.address = address
    self.dob = dob
    self.managed_accounts = {}
  
  def add_account(self, account):
    self.managed_accounts[account.account_id] = account
  
  def get_accounts(self):
    return self.managed_accounts

class Account:
  def __init__(self, customer_id, branch_code, account_id, atm_card, initial_balance=0):
    self.customer_id = customer_id
    self.branch_code = branch_code
    self.account_id = account_id
    self.balance = initial_balance
    self.atm_card = atm_card
  
  def show_balance(self):
    print(f'You balance is: {self.balance}')
  
  def deposit(self, amount):
    if amount < 1:
      raise ValueError("Amount to deposit can not be 0 or negative.")
    
    self.balance += amount
    print(f'Your new balance is: {self.balance}')
  
  def withdraw(self, amount):
    if amount < 1:
      raise ValueError("Amount to withdraw can not be 0 or negative.")
    
    if amount > self.balance:
      raise ValueError("Your account balance is lower than requested withdrawl.")
    
    self.balance -= amount
    print(f'Your new balance is: {self.balance}')

class Card:
  def __init__(self, account_id, card_id, initial_pin='0000'):
    self.account_id = account_id
    self.card_id = card_id
    self.pin = initial_pin
  
  def change_pin(self, new_pin):
    raise NotImplementedError
    
def bank_setup_with_clients():
    branch = Bank(bank_name='SBI', branch_code='SBI001', branch_address='700 Olive Way')

    # Customer goes to bank
    client_id = branch.add_client('A Bamotra', '2720 152nd Ave NE', '1997-07-17')
    new_account_number, new_atm_card_number = branch.open_account(customer_id=client_id, initial_balance=10)
    
    # Another Customer goes to bank
    new_client_id = branch.add_client('B Bamotra', '2720 152nd Ave NE', '1992-12-17')
    next_new_account_number, next_new_atm_card_number = branch.open_account(customer_id=new_client_id, initial_balance=100)
    
    # To print current clients and their information
    branch.show_accounts()
    
    return branch, client_id, new_account_number, new_atm_card_number

if __name__ == '__main__':
    
    branch = bank_setup_with_clients()
    atm_machine = Atm(managing_bank_handler=branch, atm_location='Redmond')
    atm_machine.operate()