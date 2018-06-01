
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import urlparse
import budget
import json
import datetime

BASE_WEB_DIR = "webserver/"


class BudgetHTTPRequestHandler(BaseHTTPRequestHandler):

    def __init__(self, request, client_address, server):
        BaseHTTPRequestHandler.__init__(self, request, client_address, server)
        self.manager = budget.AccountManager()

    def do_GET(self):

        parsed_url = urlparse.urlparse(self.path)
        url_path = parsed_url.path.split("/")
        query_params = urlparse.parse_qs(parsed_url.query)

        if url_path[0] != "":
            self.error("Invalid URL")

        if url_path[1] == "":
            # Root
            self.send_response(200)

            self.send_header('Content-type', 'text/html')
            self.end_headers()

            with open(BASE_WEB_DIR + "index.html", "r") as f:
                self.wfile.write(f.read())
            return

        if url_path[1][-3:] == ".js":
            # JS file
            self.send_response(200)

            self.send_header('Content-type', 'text/javascript')
            self.end_headers()

            with open(BASE_WEB_DIR + url_path[1], "r") as f:
                self.wfile.write(f.read())
            return

        if url_path[1][-4:] == ".css":
            # CSS file
            self.send_response(200)

            self.send_header('Content-type', 'text/css')
            self.end_headers()

            with open(BASE_WEB_DIR + url_path[1], "r") as f:
                self.wfile.write(f.read())
            return

        if url_path[1] == "accounts":
            # Accounts query
            self.manager = budget.AccountManager()
            accounts = self.manager.list_accounts()

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()

            self.wfile.write(bytes(json.dumps({"accounts": accounts})))
            return

        if url_path[1] == "history":
            # History query
            # Get filter from params
            filter_accounts = None
            filter_from_to = None
            filter_charge_begin = None
            filter_charge_end = None
            filter_date_begin = None
            filter_date_end = None
            filter_notes_contain = None

            if "accounts" in query_params:
                filter_accounts = [x.strip() for x in query_params["accounts"][0].split(",")]
            if "from_to" in query_params:
                filter_from_to = query_params["from_to"][0]
            if "charge_begin" in query_params:
                filter_charge_begin = query_params["charge_begin"][0]
            if "charge_end" in query_params:
                filter_charge_end = query_params["charge_end"][0]
            if "date_begin" in query_params:
                filter_date_begin = datetime.datetime.strptime(query_params["date_begin"][0], "%Y-%m-%d")
            if "date_end" in query_params:
                filter_date_end = datetime.datetime.strptime(query_params["date_end"][0], "%Y-%m-%d")
            if "notes_contain" in query_params:
                filter_notes_contain = query_params["notes_contain"][0]

            self.manager = budget.AccountManager()
            history = self.manager.list_history_filter(accounts=filter_accounts, from_to=filter_from_to,
                                                       charge_begin=filter_charge_begin,
                                                       charge_end=filter_charge_end,
                                                       date_begin=filter_date_begin,
                                                       date_end=filter_date_end,
                                                       notes_contains=filter_notes_contain)

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()

            self.wfile.write(bytes(json.dumps({"history": [x.as_dict() for x in history]})))
            return

        self.send_error(404, "That resource can't be found")
        return

    def do_POST(self):
        pass

    def error(self, msg=""):
        self.send_error(500, msg)

if __name__ == "__main__":

    print("Starting server...")

    server_address = ("0.0.0.0", 80)
    httpd = HTTPServer(server_address, BudgetHTTPRequestHandler)
    print("Server running")
    httpd.serve_forever()
