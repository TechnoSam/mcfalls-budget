
# coding=utf-8

import sqlite3
import datetime

DB_NAME = "budget.db"


class BudgetError(RuntimeError):
    pass


class Transaction:

    def __init__(self):

        self.data = {}
        self.fields = ["id", "account_from", "charge", "date", "account_to", "notes",
                       "file_name", "file_size", "file_data"]
        for key in self.fields:
            self.data[key] = None

    def from_new(self, account_from, charge, date,
                 account_to="", notes="", file_name="", file_type="", file_size=0, file_data=""):

        self.data["id"] = "NULL"
        self.data["account_from"] = account_from
        self.data["charge"] = charge
        self.data["date"] = date.strftime("%Y-%m-%d")
        self.data["notes"] = notes
        self.data["account_to"] = account_to
        self.data["file_name"] = file_name
        self.data["file_type"] = file_type
        self.data["file_size"] = file_size
        self.data["file_data"] = file_data

    def from_db(self, db_tuple):

        for key, value in (self.fields, db_tuple):
            print("%s:%s\n" % (key, value))

    def get_accounts(self):
        return self.data["account_from"], self.data["account_to"]

    def get_charge(self):
        return self.data["charge"]

    def as_tuple(self):

        ret_tuple = ()
        for key in self.fields:
            ret_tuple += (self.data[key],)

        return ret_tuple

    def as_dict(self):
        return self.data


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

    def list_all_history(self):
        list_all_history_q = """
        SELECT * FROM history
        """
        self.db_cursor.execute(list_all_history_q)
        return self.db_cursor.fetchall()

    def list_history_filter(self, accounts=None, from_to=None, charge_begin=None, charge_end=None,
                            date_begin=None, date_end=None, has_file=None, notes_contains=None):

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
                    condition += "\"%s\"" % account
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

        if has_file is not None:
            filters += 1
            if filters > 1:
                condition += "AND "
            condition += "file_size <> 0 "

        if notes_contains is not None:
            filters += 1
            if filters > 1:
                condition += "AND "
            condition += "notes LIKE \"%%%s%%\"" % notes_contains.lower()

        if filters != 0:
            condition = "WHERE " + condition

        list_history_q = list_history_q + condition

        print(list_history_q)
        self.db_cursor.execute(list_history_q)
        return self.db_cursor.fetchall()

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

    def make_transaction(self, transaction):

        account_from = transaction.get_accounts()[0]
        account_to = transaction.get_accounts()[1]
        charge = transaction.get_charge()

        if not self.account_exists(account_from):
            raise BudgetError("Account from %s does not exist" % account_from)
        if account_to != "" and not self.account_exists(account_to):
            raise BudgetError("Account to %s does not exist" % account_to)
        if charge == 0.00:
            raise BudgetError("Charge cannot be $0.00")

        account_from_balance = self.get_account_balance(account_from)
        account_from_balance -= charge
        self.__set_account_balance(account_from, account_from_balance)

        if account_to != "":
            account_to_balance = self.get_account_balance(account_to)
            account_to_balance += charge
            self.__set_account_balance(account_to, account_to_balance)

        transaction_cmd_fmt = """
        INSERT INTO history (id, account_from, charge, date, notes, account_to,
        file_name, file_type, file_size, file_data) 
        VALUES ({id}, "{account_from}", "{charge}", "{date}", "{notes}", "{account_to}",
        "{file_name}", "{file_type}", "{file_size}", "{file_data}");
        """

        transaction_cmd = transaction_cmd_fmt.format(**transaction.as_dict())
        self.db_cursor.execute(transaction_cmd)
        self.db_conn.commit()

    def archive(self):
        pass

    def export_ods(self):
        pass

if __name__ == "__main__":

    print("Budget Unit Tests...")

    b = Budget()
    # b.add_account("test5", 500.00)
    print(b.list_accounts())

    t = Transaction()
    # t.from_new("test5", 100.00, datetime.datetime(2017, 07, 8), account_to="test")
    # b.make_transaction(t)
    # print(b.list_accounts())
    print(b.list_all_history())
    # b.db_cursor.execute("SELECT * FROM history WHERE account_from IN ('test3', 'test5') OR account_to IN ('test3', 'test5');")
    # print(b.db_cursor.fetchall())

    print(b.list_history_filter(accounts=['test3', 'test5'], charge_begin=75, charge_end=125, date_begin=datetime.datetime(2017, 1, 1), date_end=datetime.datetime.now()))

