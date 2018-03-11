
# coding=utf-8

import sqlite3
import datetime
import os.path
from os import makedirs

DB_NAME = "budget.db"


class BudgetError(RuntimeError):
    pass


class Transaction:

    def __init__(self):

        self.data = {}
        self.fields = ["id", "charge", "date", "account_from", "account_to", "notes",
                       "files"]
        for key in self.fields:
            self.data[key] = None

    def from_new(self, charge, date, account_from="", account_to="",
                 notes="", files=""):

        if account_from == "" and account_to == "":
            raise BudgetError("Account from and account to cannot both be empty")

        self.data["id"] = "NULL"
        self.data["charge"] = charge
        self.data["date"] = date.strftime("%Y-%m-%d")
        self.data["account_from"] = account_from
        self.data["account_to"] = account_to
        self.data["notes"] = notes
        self.data["files"] = files

    def from_db(self, db_tuple):

        for key, value in zip(self.fields, db_tuple):
            self.data[key] = value

    def get_accounts(self):
        return self.data["account_from"], self.data["account_to"]

    def get_charge(self):
        return self.data["charge"]

    def set_charge(self, charge):
        self.data["charge"] = charge

    def get_files(self):
        return [x.strip() for x in self.data["files"].split(",")]

    def get_date(self):
        return self.data["date"]

    def get_year(self):
        return self.data["date"].split("-")[0]

    def get_month(self):
        return self.data["date"].split("-")[1]

    def get_day(self):
        return self.data["date"].split("-")[2]

    def as_tuple(self):

        ret_tuple = ()
        for key in self.fields:
            ret_tuple += (self.data[key],)

        return ret_tuple

    def as_dict(self):
        return self.data

    def __str__(self):
        return "id: %7s, account_from: %20s, account_to: %20s, charge: %7.2f, date: %s, files: %30s, notes: %s"\
               % (self.data["id"], self.data["account_from"], self.data["account_to"], self.data["charge"],
                  self.data["date"], self.data["files"], self.data["notes"])


class Budget:

    def __init__(self):

        self.db_conn = sqlite3.connect(DB_NAME)
        self.db_cursor = self.db_conn.cursor()

    def add_account(self, name, balance):

        if len(name) == 0:
            raise BudgetError("Account name cannot be empty")
        if self.account_exists(name):
            raise BudgetError("Account '%s' already exists" % name)

        add_account_cmd_fmt = """
        INSERT INTO accounts (name, balance) VALUES ("{name}", "{balance}");
        """
        add_account_cmd = add_account_cmd_fmt.format(name=name, balance=balance)
        self.db_cursor.execute(add_account_cmd)
        self.db_conn.commit()

    def list_accounts(self):

        list_accounts_q = """
        SELECT * FROM accounts
        """
        self.db_cursor.execute(list_accounts_q)
        return self.db_cursor.fetchall()

    def list_history_filter(self, accounts=None, from_to=None, charge_begin=None, charge_end=None,
                            date_begin=None, date_end=None, notes_contains=None):

        list_history_q = "SELECT * FROM history "

        filters = 0

        condition = ""

        if accounts is not None:
            filters += 1
            if filters > 1:
                condition += "AND "

            if from_to is None:
                condition += "(account_from IN ("
                for account in accounts:
                    condition += "\"%s\", " % account
                condition = condition[:-2]
                condition += ") OR account_to IN ("
                for account in accounts:
                    condition += "\"%s\", " % account
                condition = condition[:-2]
                condition += ")) "
            elif from_to == "from":
                condition += "account_from IN ("
                for account in accounts:
                    condition += "\"%s\", " % account
                condition = condition[:-2]
                condition += ") "
            elif from_to == "to":
                condition += "account_to IN ("
                for account in accounts:
                    condition += "\"%s\", " % account
                condition = condition[:-2]
                condition += ") "

        if charge_begin is not None:
            filters += 1
            if filters > 1:
                condition += "AND "
            condition += "charge >= %s " % charge_begin

        if charge_end is not None:
            filters += 1
            if filters > 1:
                condition += "AND "
            condition += "charge <= %s " % charge_end

        if date_begin is not None:
            filters += 1
            if filters > 1:
                condition += "AND "
            condition += "date >= \"%s\" " % date_begin.strftime("%Y-%m-%d")

        if date_end is not None:
            filters += 1
            if filters > 1:
                condition += "AND "
            condition += "date <= \"%s\" " % date_end.strftime("%Y-%m-%d")

        if notes_contains is not None:
            filters += 1
            if filters > 1:
                condition += "AND "
            condition += "notes LIKE \"%%%s%%\"" % notes_contains.lower()

        if filters != 0:
            condition = "WHERE " + condition

        list_history_q = list_history_q + condition

        self.db_cursor.execute(list_history_q)
        results = self.db_cursor.fetchall()
        transactions = []
        for result in results:
            transaction = Transaction()
            transaction.from_db(result)
            transactions.append(transaction)

        return transactions

    def account_exists(self, name):

        account_exists_q_fmt = """
        SELECT * FROM accounts WHERE ("name" = "{name}")
        """
        account_exists_q = account_exists_q_fmt.format(name=name)
        self.db_cursor.execute(account_exists_q)
        result = self.db_cursor.fetchall()
        return len(result) != 0

    def get_account_balance(self, account):

        if not self.account_exists(account):
            raise BudgetError("Account %s does not exist" % account)

        account_balance_q_fmt = """
        SELECT * FROM accounts WHERE ("name" = "{account}");
        """
        account_balance_q = account_balance_q_fmt.format(account=account)
        self.db_cursor.execute(account_balance_q)
        result = self.db_cursor.fetchall()
        if len(result) != 1:
            raise BudgetError("Sam sucks! Somehow there are two accounts with the same name! (%s)" % account)

        return result[0][1]

    def __set_account_balance(self, account, balance):

        if not self.account_exists(account):
            raise BudgetError("Account %s does not exist" % account)

        account_balance_cmd_fmt = """
        UPDATE accounts
        SET "balance" = "{balance}"
        WHERE "name" = "{account}";
        """
        account_balance_cmd = account_balance_cmd_fmt.format(account=account, balance=balance)
        self.db_cursor.execute(account_balance_cmd)
        self.db_conn.commit()

    def make_transaction(self, transaction, file_data=list()):

        account_from = transaction.get_accounts()[0]
        account_to = transaction.get_accounts()[1]
        charge = transaction.get_charge()

        # Both accounts cannot be empty, guaranteed by transaction creation, but we can recheck
        if account_from == "" and account_to == "":
            raise BudgetError("Sam sucks! Somehow we have a transaction with no accounts!")

        if account_from != "" and not self.account_exists(account_from):
            raise BudgetError("Account from %s does not exist" % account_from)
        if account_to != "" and not self.account_exists(account_to):
            raise BudgetError("Account to %s does not exist" % account_to)
        if charge == 0.00:
            raise BudgetError("Charge cannot be $0.00")

        # Save the files
        if len(transaction.get_files()) != len(file_data):
            raise BudgetError("Mismatch between file names and data")
        if len(transaction.get_files()) != 0:
            path = "files/" + transaction.get_year() + "/" + transaction.get_month() + "/" + transaction.get_day() + "/"
            if not os.path.isdir(path):
                makedirs(path)

            for name in transaction.get_files():
                if os.path.isfile(path + "/" + name):
                    raise BudgetError("File already exists")

            for name, data in zip(transaction.get_files(), file_data):
                with open(path + "/" + name, "w") as f:
                    f.write(data)

        if account_from != "":
            account_from_balance = self.get_account_balance(account_from)
            account_from_balance -= charge
            self.__set_account_balance(account_from, account_from_balance)

        if account_to != "":
            account_to_balance = self.get_account_balance(account_to)
            account_to_balance += charge
            self.__set_account_balance(account_to, account_to_balance)

        transaction_cmd_fmt = """
        INSERT INTO history (id, account_from, charge, date, notes, account_to, files)
        VALUES ({id}, "{account_from}", "{charge}", "{date}", "{notes}", "{account_to}", "{files}");
        """

        transaction_cmd = transaction_cmd_fmt.format(**transaction.as_dict())
        self.db_cursor.execute(transaction_cmd)
        self.db_conn.commit()

    @staticmethod
    def get_file(date, name):

        date_str = date.strftime("%Y-%m-%d")
        year = date_str.split("-")[0]
        month = date_str.split("-")[1]
        day = date_str.split("-")[2]

        path = "files/" + year + "/" + month + "/" + day + "/" + name
        if not os.path.isfile(path):
            raise BudgetError("File does not exist")

        with open(path, "r") as f:
            file_data = f.read()

        return file_data

    def archive(self):
        pass

    def export_ods(self):
        pass

    def undo_last(self):
        pass

if __name__ == "__main__":

    print("Budget Unit Tests...")

    b = Budget()
    try:
        b.add_account("Bank", 0.00)
        b.add_account("Groceries", 0.00)
        b.add_account("Sam Allowance", 0.00)
        b.add_account("Amanda Allowance", 0.00)

        print(b.list_accounts())

        t = Transaction()
        t.from_new(1983.03, datetime.datetime(2016, 12, 15), account_to="Bank", notes="Paycheck 1232")
        b.make_transaction(t)

        t = Transaction()
        t.from_new(1983.03, datetime.datetime(2017, 1, 1), account_to="Bank", notes="Paycheck 1233")
        b.make_transaction(t)

        t.from_new(300, datetime.datetime(2017, 1, 1), account_from="Bank", account_to="Groceries")
        b.make_transaction(t)

        t = Transaction()
        t.from_new(300, datetime.datetime(2017, 1, 1), account_from="Bank", account_to="Sam Allowance")
        b.make_transaction(t)

        t = Transaction()
        t.from_new(300, datetime.datetime(2017, 1, 1), account_from="Bank", account_to="Amanda Allowance")
        b.make_transaction(t)

        print(b.list_accounts())

        t = Transaction()
        t.from_new(39.99, datetime.datetime(2017, 1, 4), account_from="Sam Allowance", notes="Overwatch Lootboxes")
        b.make_transaction(t)

        t = Transaction()
        t.from_new(29.99, datetime.datetime(2017, 1, 8), account_from="Amanda Allowance", notes="Makeup from Ulta")
        b.make_transaction(t)

        t = Transaction()
        t.from_new(142.78, datetime.datetime(2017, 1, 14), account_from="Groceries", notes="Food Lion")
        b.make_transaction(t)

        t = Transaction()
        t.from_new(1983.03, datetime.datetime(2017, 1, 15), account_to="Bank", notes="Paycheck 1234")
        b.make_transaction(t)

        t = Transaction()
        t.from_new(12.99, datetime.datetime(2017, 1, 22), account_from="Sam Allowance", notes="RWBY Vol 5 Soundtrack")
        b.make_transaction(t)

        t = Transaction()
        t.from_new(158.25, datetime.datetime(2017, 1, 28), account_from="Groceries", notes="Giant Food")
        b.make_transaction(t)

        t = Transaction()
        t.from_new(1983.03, datetime.datetime(2017, 2, 1), account_to="Bank", notes="Paycheck 1235")
        b.make_transaction(t)

        t.from_new(300, datetime.datetime(2017, 2, 1), account_from="Bank", account_to="Groceries")
        b.make_transaction(t)

        t = Transaction()
        t.from_new(300, datetime.datetime(2017, 2, 1), account_from="Bank", account_to="Sam Allowance")
        b.make_transaction(t)

        t = Transaction()
        t.from_new(300, datetime.datetime(2017, 2, 1), account_from="Bank", account_to="Amanda Allowance")
        b.make_transaction(t)

        t = Transaction()
        t.from_new(149.99, datetime.datetime(2017, 2, 3), account_from="Amanda Allowance", notes="Kate Spade Purse")
        b.make_transaction(t)

        print(b.list_accounts())

    except BudgetError as e:
        print(e)

    print(b.list_accounts())

    # t = Transaction()
    # _data = []
    # with open("../March Rent Lake Village.pdf") as _f:
    #     _data.append(_f.read())
    # with open("../home-server-issues.txt") as _f:
    #     _data.append(_f.read())
    # t.from_new(1624.00, datetime.datetime(2018, 4, 1), account_from="Bank",
    #            files="April (Fake) Rent Receipt.pdf, issues.txt")
    # b.make_transaction(t, file_data=_data)

    _transactions = b.list_history_filter()
    for _transaction in _transactions:
        print(str(_transaction))
