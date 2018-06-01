
window.onload = function() {

    Array.prototype.sortOnAscending = function(key){
        this.sort(function(a, b){
            if(a[key] < b[key]){
                return -1;
            }else if(a[key] > b[key]){
                return 1;
            }
            return 0;
        });
    }

    Array.prototype.sortOnDescending = function(key){
        this.sort(function(a, b){
            if(a[key] > b[key]){
                return -1;
            }else if(a[key] < b[key]){
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

    var params = {};

    var date_value = document.getElementById("transaction_date").value;
    if (date_value !== "") {
        params["date"] = date_value;
    }
    else {
        alert("Date cannot be empty");
        return;
    }

    var charge_value = document.getElementById("transaction_charge").value;
    if (charge_value !== "") {
        params["charge"] = charge_value;
    }
    else {
        alert("Charge cannot be empty");
        return;
    }

    var account_from_value = document.getElementById("transaction_account_from").value;
    var account_to_value = document.getElementById("transaction_account_to").value;

    if (account_from_value === "None" && account_to_value === "None") {
        alert("Both account from and to cannot both be None");
        return;
    }

    if (account_from_value !== "None") {
        params["account_from"] = account_from_value;
    }

    if (account_to_value !== "None") {
        params["account_to"] = account_to_value;
    }

    var notes_value = document.getElementById("transaction_notes").value;
    if (notes_value !== "") {
        params["notes"] = notes_value;
    }

    var transaction_xhttp = new XMLHttpRequest();

    transaction_xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            console.log("Successfully Completed Transaction")
        }
    };

    transaction_xhttp.open("POST", "transaction", true);
    transaction_xhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
    transaction_xhttp.send(serialize(params));

    document.getElementById("transaction_date").value = "";
    document.getElementById("transaction_charge").value = "";
    document.getElementById("transaction_notes").value = "";

    refreshAccounts();
    refreshHistory();

}

function refreshAccounts() {

    var account_from_box = document.getElementById("transaction_account_from");
    for (var i = account_from_box.options.length - 1; i >=0; i--) {
        account_from_box.remove(i);
    }

    var account_to_box = document.getElementById("transaction_account_to");
    for (var i = account_to_box.options.length - 1; i >=0; i--) {
        account_to_box.remove(i);
    }

    var none_from = document.createElement("option");
    none_from.text = none_from.value = "None";
    account_from_box.add(none_from, 0);

    var none_to = document.createElement("option");
    none_to.text = none_to.value = "None";
    account_to_box.add(none_to, 0);

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

                var from_option = document.createElement("option")
                from_option.text = from_option.value = resp["accounts"][i][0];
                account_from_box.add(from_option);

                var to_option = document.createElement("option")
                to_option.text = to_option.value = resp["accounts"][i][0];
                account_to_box.add(to_option);
            }

            var oldAccountTable = document.getElementById("account_table_body");
            oldAccountTable.parentNode.replaceChild(newAccountTable, oldAccountTable);
        }
    };
    accounts_xhttp.open("GET", "accounts", true);
    accounts_xhttp.send();

}

function refreshHistory() {

    var params = {};

    var accounts_value = document.getElementById("filter_accounts").value;
    if (accounts_value !== "") {
        params["accounts"] = accounts_value;
    }

    var from_to_value = document.getElementById("filter_from_to").value;
    if (from_to_value !== "none") {
        params["from_to"] = from_to_value;
    }

    var date_begin_value = document.getElementById("filter_date_begin").value;
    if (date_begin_value !== "") {
        params["date_begin"] = date_begin_value;
    }

    var date_end_value = document.getElementById("filter_date_end").value;
    if (date_end_value !== "") {
        params["date_end"] = date_end_value;
    }

     var charge_begin_value = document.getElementById("filter_charge_begin").value;
    if (charge_begin_value !== "") {
        params["charge_begin"] = charge_begin_value;
    }

    var charge_end_value = document.getElementById("filter_charge_end").value;
    if (charge_end_value !== "") {
        params["charge_end"] = charge_end_value;
    }

    var notes_contain_value = document.getElementById("filter_notes_contain").value;
    if (notes_contain_value !== "") {
        params["notes_contain"] = notes_contain_value;
    }

    var history_xhttp = new XMLHttpRequest();

    history_xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var resp = JSON.parse(this.responseText);
            var newHistoryTable = document.createElement("tbody");
            newHistoryTable.id = "history_table_body";
            var history = resp["history"];
            history.sortOnDescending("date");
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
    history_xhttp.open("GET", "history?" + serialize(params), true);
    history_xhttp.send();

}

function serialize(obj, prefix) {
  var str = [],
    p;
  for (p in obj) {
    if (obj.hasOwnProperty(p)) {
      var k = prefix ? prefix + "[" + p + "]" : p,
        v = obj[p];
      str.push((v !== null && typeof v === "object") ?
        serialize(v, k) :
        encodeURIComponent(k) + "=" + encodeURIComponent(v));
    }
  }
  return str.join("&");
}
