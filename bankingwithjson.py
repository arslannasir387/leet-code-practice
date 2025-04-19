from tabulate import tabulate
import random
import json

DATA_FILE = "bank_data.json"

def load_data():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"accounts": {}, "users": {}}

def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

class Account:
    def __init__(self, name, username, password, pin, initial_balance=0, account_number=None, transaction_history=None,  locked=False, login_attempts=0, pin_attempts=0):
        self.name = name
        self.username = username
        self.password = password
        self.pin = pin
        self.__account_number = account_number if account_number else random.randint(100000, 999999)
        self.__balance = initial_balance
        self.transaction_history = transaction_history if transaction_history else []
        self.locked = locked
        self.login_attempts = login_attempts
        self.pin_attempts = pin_attempts
        if not transaction_history:
            self._log_transaction("Account created", initial_balance)

    def is_locked(self):
        return self.locked
    
    def reset_attempts(self):
        self.login_attempts = 0
        self.pin_attempts = 0
    
    def deposit(self, amount):
        if amount > 0:
            self.__balance += amount
            self._log_transaction("Deposit", amount, 0.0)
            print(f"Deposited ${amount:.2f}. New balance: ${self.__balance:.2f}")
        else:
            print("Deposit amount must be positive.")


    def withdraw(self, amount):
        if amount > 0 and amount <= self.__balance:
            fee = amount * 0.015  # 1.5% withdrawal fee
            total_amount = amount + fee
            if total_amount <= self.__balance:
                self.__balance -= total_amount
                self._log_transaction("Withdrawal", amount, fee)
                print(f"Withdrew ${amount:.2f} + ${fee:.2f} fee. New balance: ${self.__balance:.2f}")
            else:
                print("Insufficient funds including fee.")
        elif amount > self.__balance:
            print("Insufficient funds.")
        else:
            print("Withdrawal amount must be positive.")

    def transfer(self, recipient, amount, pin):
        # if pin != self.pin:
        #     print("Incorrect PIN. Transfer denied.")
        #     return
        if pin != self.pin:
            self.pin_attempts += 1
            if self.pin_attempts >= 3:
                self.locked = True
                print("Too many wrong PIN entries. Account has been locked.")
            else:
                print(f"Incorrect PIN,Transfer denied. {3 - self.pin_attempts} attempts left.")
            return
        else:
            self.pin_attempts = 0
        
        if recipient == self:
            print("You cannot transfer funds to your own account.")
            return
        
        if amount > 0 and amount <= self.__balance:
            fee = amount * 0.035  # 3.5% transfer fee
            total_amount = amount + fee
            if total_amount <= self.__balance:
                self.__balance -= total_amount
                recipient.__balance += amount
                self._log_transaction(f"Transfer to {recipient.name}", amount, fee)
                recipient._log_transaction(f"Received from {self.name}", amount, 0.0)
                self._log_transaction("Transfer Fee", fee, fee)
                print(f"Transferred ${amount:.2f} to {recipient.name} + ${fee:.2f} fee. New balance: ${self.__balance:.2f}")
            else:
                print("Insufficient funds including fee.")
        else:
            print("Insufficient funds or invalid amount.")

    def check_balance(self):
        print(f"Account Balance: ${self.__balance:.2f}")
    
    def show_transaction_history(self):
        if self.transaction_history:
            print(tabulate(self.transaction_history, headers=["Transaction Type", "Amount ($)", "Fee ($)"], tablefmt="grid"))
            print(f"\nCurrent Balance: ${self.__balance:.2f}")
        else:
            print("No transactions yet.")

    def _log_transaction(self, transaction_type, amount, fee=0.0):
        self.transaction_history.append([transaction_type, amount, fee])
    
    def get_account_number(self):
        return self.__account_number
    
    def to_dict(self):
        return {
            "name": self.name,
            "username": self.username,
            "password": self.password,
            "pin": self.pin,
            "account_number": self.__account_number,
            "balance": self.__balance,
            "transaction_history": self.transaction_history,
            "locked": self.locked,
            "login_attempts": self.login_attempts,
            "pin_attempts": self.pin_attempts
        }

class Bank:
    def __init__(self):
        data = load_data()
        self.admin_credentials = {"admin": "admin123"}
        self.accounts = {
            int(acc_num): Account(
                name=acc_data["name"],
                username=acc_data["username"],
                password=acc_data["password"],
                pin=acc_data["pin"],
                initial_balance=acc_data["balance"],
                account_number=acc_num,
                transaction_history=acc_data.get("transaction_history", [])
            )
            for acc_num, acc_data in data["accounts"].items()
        }
        self.users = data["users"]
    
    def create_account(self, name, username, password, pin, initial_balance):
        if username in self.users:
            print("Username already exists. Choose a different username.")
            return None
        new_account = Account(name, username, password, pin, initial_balance)
        self.accounts[new_account.get_account_number()] = new_account
        self.users[username] = (password, new_account.get_account_number())
        self.save()
        print(f"Account created successfully! Account Number: {new_account.get_account_number()}")
        return new_account
    
    # def login(self, username, password):
    #     if username in self.users and self.users[username][0] == password:
    #         account_number = self.users[username][1]
    #         return self.accounts.get(account_number, None)
    #     else:
    #         print("Invalid username or password.")
    #         return None
    def login(self, username, password):
        if username in self.users:
            account_number = self.users[username][1]
            account = self.accounts.get(account_number)

            if account.is_locked():
                print("Account is locked. Contact admin to unlock.")
                return None

            if account.password == password:
                account.reset_attempts()
                self.save()
                return account
            else:
                account.login_attempts += 1
                if account.login_attempts >= 3:
                    account.locked = True
                    print("Too many failed login attempts. Account has been locked.")
                else:
                    print(f"Invalid password. {3 - account.login_attempts} attempts left.")
                self.save()
                return None
        else:
            print("Username not found.")
            return None
    
    def admin_menu(self):
        while True:
            print("\n--- Admin Menu ---")
            print("1. Unlock User Account")
            print("2. View All Accounts")
            print("3. Exit Admin Menu")
            choice = input("Enter your choice: ")

            if choice == "1":
                acc_num = int(input("Enter account number to unlock: "))
                account = self.get_account(acc_num)
                if account and account.is_locked():
                    account.locked = False
                    account.reset_attempts()
                    self.save()
                    print("Account unlocked successfully.")
                else:
                    print("Account not found or not locked.")
            elif choice == "2":
                self.display_all_accounts()
            elif choice == "3":
                print("Exiting admin menu.")
                break
            else:
                print("Invalid choice.")
    def admin_login(self):
        username = input("Enter admin username: ")
        password = input("Enter admin password: ")
        if self.admin_credentials.get(username) == password:
            print("Admin logged in.")
            self.admin_menu()
        else:
            print("Invalid admin credentials.")


    def get_account(self, account_number):
        return self.accounts.get(account_number, None)
    
    def display_all_accounts(self):
        if not self.accounts:
            print("No accounts found.")
            return
        account_list = [[acc.get_account_number(), acc.name, acc.username, acc.to_dict()["balance"],"Locked" if acc.is_locked() else "Active"] for acc in self.accounts.values()]
        print(tabulate(account_list, headers=["Account Number", "Name", "Username", "Balance", "Status"], tablefmt="grid"))
    
    def save(self):
        data = {
            "accounts": {acc_num: acc.to_dict() for acc_num, acc in self.accounts.items()},
            "users": self.users
        }
        save_data(data)

def main():
    bank = Bank()
    while True:
        print("\n--- Banking System ---")
        print("1. Create Account")
        print("2. Login")
        print("3. Display All Accounts")
        print("4. Admin Login")
        print("5. Exit")
        
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
                        bank.save()
                    elif action == "2":
                        amount = float(input("Enter withdrawal amount: "))
                        account.withdraw(amount)
                        bank.save()
                    elif action == "3":
                        recipient_number = int(input("Enter recipient account number: "))
                        recipient = bank.get_account(recipient_number)
                        if recipient:
                            amount = float(input("Enter transfer amount: "))
                            pin = input("Enter your PIN: ")
                            account.transfer(recipient, amount, pin)
                            bank.save()
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
            bank.display_all_accounts()
        elif choice == "4":
            bank.admin_login()
        elif choice == "5":
            print("Exiting... Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
