
import datetime

import budget

if __name__ == "__main__":

    account_manager = budget.AccountManager()

    user_charge = 0
    user_date = ""
    user_account_from = ""
    user_account_to = ""
    user_notes = ""
    user_files = []
    user_file_data = []

    filter_accounts = None
    filter_from_to = None
    filter_charge_begin = None
    filter_charge_end = None
    filter_date_begin = None
    filter_date_end = None
    filter_notes_contain = None

    commands = ["list-accounts", "filter", "list-history", "add-account <account>", "transaction"]

    default_prompt = "McFalls Budget > "
    prompt = default_prompt

    state = "top"

    while True:
        cmd = raw_input(prompt)
        cmd = cmd.split()

        if len(cmd) == 0:
            continue

        if state == "top":
            if cmd[0] == "help":
                print("Print this help. Type 'help <command>' for extended info")

            elif cmd[0] == "exit":
                break

            elif cmd[0] == "list-accounts":
                accounts = account_manager.list_accounts()
                print("\n".join(["%-20s %0.2f" % (x[0], x[1]) for x in accounts]))
                print("------------------------------")
                print("Total:               " + str(sum([float(x[1]) for x in accounts])))

            elif cmd[0] == "start-transaction":
                state = "transaction"
                prompt = "McFalls Budget (transaction) > "
                user_charge = 0
                user_date = datetime.datetime.now()
                user_account_from = ""
                user_account_to = ""
                user_notes = ""
                user_files = []
                user_file_data = []

            elif cmd[0] == "undo":
                account_manager.undo_last()

            elif cmd[0] == "start-filter":
                state = "filter"
                prompt = "McFalls Budget (filter) > "

            elif cmd[0] == "list-filter":
                print("Current filter:\nAccounts: %s\nFrom/To: %s\nCharge: [%s, %s]\nDate: [%s, %s]\nNotes: %s" %
                      (filter_accounts, filter_from_to, filter_charge_begin, filter_charge_end, filter_date_begin,
                       filter_date_end, filter_notes_contain))

            elif cmd[0] == "list-history":
                short_history = (cmd[1] == "-s") if len(cmd) > 1 else False
                history = account_manager.list_history_filter(accounts=filter_accounts, from_to=filter_from_to,
                                                              charge_begin=filter_charge_begin,
                                                              charge_end=filter_charge_end,
                                                              date_begin=filter_date_begin,
                                                              date_end=filter_date_end,
                                                              notes_contains=filter_notes_contain)
                history = sorted(history, key=lambda item: item.get_date())
                for transaction in history:
                    print(transaction.as_string(short=short_history))
                print("")

            elif cmd[0] == "add-account":
                try:
                    new_account = " ".join(cmd[1:])
                    account_manager.add_account(new_account, 0.00)
                except Exception as e:
                    print("Failed to add account: " + e.message)

            elif cmd[0] == "edit-charge":
                if len(cmd) < 3:
                    print("usage: edit-charge <id> <charge>")
                    continue
                try:
                    t_id = int(cmd[1])
                except Exception as e:
                    print("Invalid id: " + e.message)
                    continue

                try:
                    charge = float(cmd[2])
                except Exception as e:
                    print("Invalid charge: " + e.message)
                    continue

                try:
                    account_manager.edit_transaction(t_id, charge=charge)
                except Exception as e:
                    print("Failed to edit transaction: " + e.message)
                    continue

            elif cmd[0] == "edit-date":
                if len(cmd) < 3:
                    print("usage: edit-date <id> <YYYY-MM-DD>")
                    continue
                try:
                    t_id = int(cmd[1])
                except Exception as e:
                    print("Invalid id: " + e.message)
                    continue

                try:
                    date = datetime.datetime.strptime(cmd[2], "%Y-%m-%d")
                except Exception as e:
                    print("Invalid date: " + e.message)
                    continue

                try:
                    account_manager.edit_transaction(t_id, date=date)
                except Exception as e:
                    print("Failed to edit transaction: " + e.message)
                    continue

            elif cmd[0] == "edit-notes":
                if len(cmd) < 3:
                    print("usage: edit-notes <id> <notes>")
                    continue

                try:
                    t_id = int(cmd[1])
                except Exception as e:
                    print("Invalid id: " + e.message)
                    continue

                notes = " ".join(cmd[2:])

                try:
                    account_manager.edit_transaction(t_id, notes=notes)
                except Exception as e:
                    print("Failed to edit transaction: " + e.message)
                    continue

            else:
                print("Unrecognized command: %s" % cmd[0])

        elif state == "transaction":
            if cmd[0] == "help":
                print("Print this help.\nlist\ncharge\ndate\naccount-from\naccount-to\nnotes\nadd-file\ncancel\ncommit\n")

            if cmd[0] == "list":
                print("Charge: " + str(user_charge))
                print("Date: " + user_date.strftime("%Y-%m-%d"))
                print("Account from: " + user_account_from)
                print("Account to: " + user_account_to)
                print("Notes: " + user_notes)
                print("Files: " + " ".join(user_files))

            if cmd[0] == "charge":
                if len(cmd) < 2:
                    print("No charge given")
                    continue
                try:
                    user_charge = float(cmd[1])
                except Exception as e:
                    print("Failed to set charge: " + e.message)
                    continue
                print("Set charge to %s" % cmd[1])

            if cmd[0] == "date":
                if len(cmd) < 2:
                    print("No date given")

                if cmd[1] == "today":
                    user_date = datetime.datetime.now()
                else:
                    try:
                        user_date = datetime.datetime.strptime(cmd[1], "%Y-%m-%d")
                    except Exception as e:
                        print("Could not set date: " + e.message)
                        continue

                print("Set date to: " + user_date.strftime("%Y-%m-%d"))

            if cmd[0] == "account-from":
                if len(cmd) < 2:
                    print("No account given")
                    continue
                account_from = " ".join(cmd[1:])
                if not account_manager.account_exists(account_from):
                    print("Account does not exist: " + account_from)
                    continue
                user_account_from = account_from
                print("Set account from: " + user_account_from)

            if cmd[0] == "account-to":
                if len(cmd) < 2:
                    print("No account given")
                    continue
                account_to = " ".join(cmd[1:])
                if not account_manager.account_exists(account_to):
                    print("Account does not exist: " + account_to)
                    continue
                user_account_to = account_to
                print("Set account to: " + user_account_to)

            if cmd[0] == "notes":
                if len(cmd) < 2:
                    print("No notes given")
                    continue
                user_notes = " ".join(cmd[1:])
                print("Set notes to: " + user_notes)

            if cmd[0] == "add-file":
                if len(cmd) < 3:
                    print("No files given")
                    continue
                existing_file_name = cmd[1]
                desired_file_name = cmd[2]

                if desired_file_name in user_files:
                    print("Cannot add duplicate file name: " + desired_file_name)
                    continue

                user_files.append(desired_file_name)

                with open(existing_file_name, "r") as f:
                    user_file_data.append(f.read())

                print("Successfully added file: " + existing_file_name)

            if cmd[0] == "cancel":
                print("Canceled transaction")
                state = "top"
                prompt = default_prompt

            if cmd[0] == "commit":
                try:
                    new_transaction = budget.Transaction()
                    new_transaction.from_new(user_charge, user_date, user_account_from, user_account_to,
                                             user_notes, ",".join(user_files))
                    account_manager.make_transaction(new_transaction, user_file_data)
                except Exception as e:
                    print("Failed to commit transaction: " + e.message)
                    continue
                print("Finished transaction")
                state = "top"
                prompt = default_prompt

        elif state == "filter":
            if cmd[0] == "add_account":
                if len(cmd) < 2:
                    print("No account given")
                    continue
                if filter_accounts is None:
                    filter_accounts = []
                filter_accounts.append(" ".join(cmd[1:]))
                print("Set account to %s" % filter_accounts)

            if cmd[0] == "clear_accounts":
                filter_accounts = None
                print("Cleared accounts")

            if cmd[0] == "from-to":
                if len(cmd) < 2:
                    print("No state given")
                    continue
                if cmd[1] == "from":
                    filter_from_to = "from"
                elif cmd[1] == "to":
                    filter_from_to = "to"
                elif cmd[1] == "none":
                    filter_from_to = None
                else:
                    print("Invalid state")
                print("From_to state: %s" % filter_from_to)

            if cmd[0] == "charge-begin":
                if len(cmd) < 2:
                    print("No charge given")
                    continue
                if cmd[1] == "none":
                    filter_charge_begin = None
                    print("Cleared charge begin")
                else:
                    try:
                        filter_charge_begin = float(cmd[1])
                        print("Set charge begin to %s" % filter_charge_begin)
                    except Exception as e:
                        print(e.message)
                        continue

            if cmd[0] == "charge-end":
                if len(cmd) < 2:
                    print("No charge given")
                    continue
                if cmd[1] == "none":
                    filter_charge_end = None
                    print("Cleared charge end")
                else:
                    try:
                        filter_charge_end = float(cmd[1])
                        print("Set charge end to %s" % filter_charge_end)
                    except Exception as e:
                        print(e.message)
                        continue

            if cmd[0] == "date-begin":
                if len(cmd) < 2:
                    print("No date given")
                    continue
                if cmd[1] == "none":
                    filter_date_begin = None
                    print("Cleared date begin")
                else:
                    try:
                        filter_date_begin = datetime.datetime.strptime(cmd[1], "%Y-%m-%d")
                        print("Set date begin to %s" % filter_date_begin.strftime("%Y-%m-%d"))
                    except Exception as e:
                        print(e.message)
                        continue

            if cmd[0] == "date-end":
                if len(cmd) < 2:
                    print("No date given")
                    continue
                if cmd[1] == "none":
                    filter_date_end = None
                    print("Cleared date end")
                else:
                    try:
                        filter_date_end = datetime.datetime.strptime(cmd[1], "%Y-%m-%d")
                        print("Set date end to %s" % filter_date_end.strftime("%Y-%m-%d"))
                    except Exception as e:
                        print(e.message)
                        continue

            if cmd[0] == "notes":
                if len(cmd) < 2:
                    print("No notes given")
                    continue
                if cmd[1] == "none":
                    filter_notes_contain = None
                    print("Cleared notes")
                else:
                    filter_notes_contain = " ".join(cmd[1:])
                    print("Notes set to: " + filter_notes_contain)

            if cmd[0] == "list":
                print("Current filter:\nAccounts: %s\nFrom/To: %s\nCharge: [%s, %s]\nDate: [%s, %s]\nNotes: %s" %
                      (filter_accounts, filter_from_to, filter_charge_begin, filter_charge_end,
                       filter_date_begin.strftime("%Y-%m-%d") if filter_date_begin else "None",
                       filter_date_end.strftime("%Y-%m-%d") if filter_date_end else "None",
                       filter_notes_contain))

            if cmd[0] == "commit":
                print("Finished filter")
                state = "top"
                prompt = default_prompt

        else:
            print("Unrecognized command: " + cmd[0])
