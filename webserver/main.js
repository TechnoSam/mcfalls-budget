
window.onload = function() {

    Array.prototype.sortOn = function(key){
        this.sort(function(a, b){
            if(a[key] < b[key]){
                return -1;
            }else if(a[key] > b[key]){
                return 1;
            }
            return 0;
        });
    }

    document.getElementById("refresh_btn").onclick = function() { refreshAccounts(); refreshHistory(); };
    document.getElementById("make_transaction_btn").onclick = function() { makeTransaction(); };

    refreshAccounts();
    refreshHistory();

}

function makeTransaction() {

    var date = document.getElementById("transaction_date").value

    var transaction_xhttp = new XMLHttpRequest();

    transaction_xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            console.log("Successfully Completed Transaction")
        }
    };

    refreshAccounts();
    refreshHistory();

}

function refreshAccounts() {

    var accounts_xhttp = new XMLHttpRequest();

    accounts_xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var resp = JSON.parse(this.responseText);


            var newAccountTable = document.createElement("tbody");
            newAccountTable.id = "account_table_body";
            var i;
            for (i = 0; i < resp["accounts"].length; i++) {
                var newRow = document.createElement("tr");
                var newAccount = document.createElement("td");
                newAccount.className = "account_cell"
                newAccount.innerHTML = resp["accounts"][i][0];
                newRow.appendChild(newAccount);
                var newBalance = document.createElement("td");
                newBalance.className = "account_cell"
                newBalance.innerHTML = "$" + resp["accounts"][i][1];
                newRow.appendChild(newBalance);
                newAccountTable.appendChild(newRow);
            }

            var oldAccountTable = document.getElementById("account_table_body");
            oldAccountTable.parentNode.replaceChild(newAccountTable, oldAccountTable);
        }
    };
    accounts_xhttp.open("GET", "accounts", true);
    accounts_xhttp.send();

}

function refreshHistory() {

    var history_xhttp = new XMLHttpRequest();

    history_xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var resp = JSON.parse(this.responseText);
            var newHistoryTable = document.createElement("tbody");
            newHistoryTable.id = "history_table_body";
            var history = resp["history"];
            history.sortOn("date");
            var i;
            for (i = 0; i < history.length; i++) {
                record = history[i];
                var newRow = document.createElement("tr");

                var newID = document.createElement("td");
                newID.className = "history_cell";
                newID.innerHTML = record["id"];
                newRow.appendChild(newID);

                var newDate = document.createElement("td");
                newDate.className = "history_cell";
                newDate.innerHTML = record["date"];
                newRow.appendChild(newDate);

                var newAccountFrom = document.createElement("td");
                newAccountFrom.className = "history_cell";
                newAccountFrom.innerHTML = record["account_from"];
                newRow.appendChild(newAccountFrom);

                var newAccountTo = document.createElement("td");
                newAccountTo.className = "history_cell";
                newAccountTo.innerHTML = record["account_to"];
                newRow.appendChild(newAccountTo);

                var newCharge = document.createElement("td");
                newCharge.className = "history_cell";
                newCharge.innerHTML = "$" + record["charge"];
                newRow.appendChild(newCharge);

                var newNotes = document.createElement("td");
                newNotes.className = "history_cell";
                newNotes.innerHTML = record["notes"];
                newRow.appendChild(newNotes);

                newHistoryTable.appendChild(newRow);
            }

            var oldHistoryTable = document.getElementById("history_table_body");
            oldHistoryTable.parentNode.replaceChild(newHistoryTable, oldHistoryTable);
        }
    };
    history_xhttp.open("GET", "history", true);
    history_xhttp.send();

}
