from tabulate import tabulate
import random

class Account:
    def __init__(self, name, initial_balance):
        self.name = name
        self.__account_number = random.randint(100000, 999999)  # Private attribute
        self.__balance = initial_balance  # Private attribute
        self.transaction_history = []
        self._log_transaction("Account created", initial_balance)
    
    def deposit(self, amount):
        if amount > 0:
            self.__balance += amount
            self._log_transaction("Deposit", amount)
            print(f"Deposited ${amount:.2f}. New balance: ${self.__balance:.2f}")
        else:
            print("Deposit amount must be positive.")

    def withdraw(self, amount):
        if amount > 0 and amount <= self.__balance:
            self.__balance -= amount
            self._log_transaction("Withdrawal", amount)
            print(f"Withdrew ${amount:.2f}. New balance: ${self.__balance:.2f}")
        elif amount > self.__balance:
            print("Insufficient funds.")
        else:
            print("Withdrawal amount must be positive.")

    def check_balance(self):
        print(f"Account Balance: ${self.__balance:.2f}")
    
    def show_transaction_history(self):
        if self.transaction_history:
            print(tabulate(self.transaction_history, headers=["Transaction Type", "Amount ($)"], tablefmt="grid"))
        else:
            print("No transactions yet.")

    def _log_transaction(self, transaction_type, amount):
        self.transaction_history.append([transaction_type, amount])
    
    def get_account_number(self):
        return self.__account_number

class Bank:
    def __init__(self):
        self.accounts = {}
    
    def create_account(self, name, initial_balance):
        if initial_balance < 0:
            print("Initial balance cannot be negative.")
            return None
        new_account = Account(name, initial_balance)
        self.accounts[new_account.get_account_number()] = new_account
        print(f"Account created successfully! Account Number: {new_account.get_account_number()}")
        return new_account
    
    def get_account(self, account_number):
        return self.accounts.get(account_number, None)
    
    def display_accounts(self):
        if self.accounts:
            account_list = [[acc.get_account_number(), acc.name] for acc in self.accounts.values()]
            print(tabulate(account_list, headers=["Account Number", "Name"], tablefmt="grid"))
        else:
            print("No accounts available.")

def main():
    bank = Bank()
    while True:
        print("\n--- Banking System ---")
        print("1. Create Account")
        print("2. Deposit")
        print("3. Withdraw")
        print("4. Check Balance")
        print("5. Transaction History")
        print("6. Display All Accounts")
        print("7. Exit")
        
        choice = input("Enter your choice: ")
        
        if choice == "1":
            name = input("Enter your name: ")
            initial_balance = float(input("Enter initial balance: "))
            bank.create_account(name, initial_balance)
        elif choice in ["2", "3", "4", "5"]:
            account_number = int(input("Enter account number: "))
            account = bank.get_account(account_number)
            if account:
                if choice == "2":
                    amount = float(input("Enter deposit amount: "))
                    account.deposit(amount)
                elif choice == "3":
                    amount = float(input("Enter withdrawal amount: "))
                    account.withdraw(amount)
                elif choice == "4":
                    account.check_balance()
                elif choice == "5":
                    account.show_transaction_history()
            else:
                print("Account not found.")
        elif choice == "6":
            bank.display_accounts()
        elif choice == "7":
            print("Exiting... Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
