
window.onload = function() {

    console.log("Initialized")

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

    var accounts_xhttp = new XMLHttpRequest();

    accounts_xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var resp = JSON.parse(this.responseText);
            console.log(resp);
            var accountsTable = document.getElementById("accounts_table");
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
                accountsTable.appendChild(newRow);
            }
        }
    };
    accounts_xhttp.open("GET", "accounts", true);
    accounts_xhttp.send();

    var history_xhttp = new XMLHttpRequest();

    history_xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var resp = JSON.parse(this.responseText);
            console.log(resp);
            var historyTable = document.getElementById("history_table");
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

                historyTable.appendChild(newRow);
            }
        }
    };
    history_xhttp.open("GET", "history", true);
    history_xhttp.send();

}
