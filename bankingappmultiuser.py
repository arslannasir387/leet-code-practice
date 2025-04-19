from tabulate import tabulate
import random

class Account:
    def __init__(self, name, username, password, pin, initial_balance):
        self.name = name
        self.username = username
        self.password = password  # Store securely in production
        self.pin = pin  # Store securely in production
        self.__account_number = random.randint(100000, 999999)
        self.__balance = initial_balance
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

    def transfer(self, recipient, amount, pin):
        if pin != self.pin:
            print("Incorrect PIN. Transfer denied.")
            return
        
        if amount > 0 and amount <= self.__balance:
            self.__balance -= amount
            recipient.__balance += amount
            self._log_transaction(f"Transfer to {recipient.name}", -amount)
            recipient._log_transaction(f"Received from {self.name}", amount)
            print(f"Transferred ${amount:.2f} to {recipient.name}. New balance: ${self.__balance:.2f}")
        else:
            print("Insufficient funds or invalid amount.")

    def check_balance(self):
        print(f"Account Balance: ${self.__balance:.2f}")
    
    def show_transaction_history(self):
        if self.transaction_history:
            print(tabulate(self.transaction_history, headers=["Transaction Type", "Amount ($)"], tablefmt="grid"))
            print(f"\nCurrent Balance: ${self.__balance:.2f}")
        else:
            print("No transactions yet.")

    def _log_transaction(self, transaction_type, amount):
        self.transaction_history.append([transaction_type, amount])
    
    def get_account_number(self):
        return self.__account_number

class Bank:
    def __init__(self):
        self.accounts = {}
        self.users = {}  # Stores username-password pairs
    
    def create_account(self, name, username, password, pin, initial_balance):
        if username in self.users:
            print("Username already exists. Choose a different username.")
            return None
        new_account = Account(name, username, password, pin, initial_balance)
        self.accounts[new_account.get_account_number()] = new_account
        self.users[username] = (password, new_account.get_account_number())
        print(f"Account created successfully! Account Number: {new_account.get_account_number()}")
        return new_account
    
    def login(self, username, password):
        if username in self.users and self.users[username][0] == password:
            account_number = self.users[username][1]
            return self.accounts[account_number]
        else:
            print("Invalid username or password.")
            return None

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
        print("2. Login")
        print("3. Exit")
        
        choice = input("Enter your choice: ")
        
        if choice == "1":
            name = input("Enter your name: ")
            username = input("Choose a username: ")
            password = input("Choose a password: ")
            pin = input("Enter a 4-digit PIN: ")
            initial_balance = float(input("Enter initial balance: "))
            bank.create_account(name, username, password, pin, initial_balance)
        elif choice == "2":
            username = input("Enter your username: ")
            password = input("Enter your password: ")
            account = bank.login(username, password)
            if account:
                while True:
                    print("\n--- Account Menu ---")
                    print("1. Deposit")
                    print("2. Withdraw")
                    print("3. Transfer Funds")
                    print("4. Check Balance")
                    print("5. Transaction History")
                    print("6. Logout")
                    
                    action = input("Enter your choice: ")
                    if action == "1":
                        amount = float(input("Enter deposit amount: "))
                        account.deposit(amount)
                    elif action == "2":
                        amount = float(input("Enter withdrawal amount: "))
                        account.withdraw(amount)
                    elif action == "3":
                        recipient_number = int(input("Enter recipient account number: "))
                        recipient = bank.get_account(recipient_number)
                        if recipient:
                            amount = float(input("Enter transfer amount: "))
                            pin = input("Enter your PIN: ")
                            account.transfer(recipient, amount, pin)
                        else:
                            print("Recipient account not found.")
                    elif action == "4":
                        account.check_balance()
                    elif action == "5":
                        account.show_transaction_history()
                    elif action == "6":
                        print("Logging out...")
                        break
                    else:
                        print("Invalid choice. Please try again.")
        elif choice == "3":
            print("Exiting... Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
