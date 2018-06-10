

function getUrlPlayerstats() {
    return "playerstats.json?nickname=" + document.forms.formPlayerstats.nickname.value;
}

function getUrlVehicledb() {
    return "vehicledb.json";
}

function round(number, precision) {
    let shift = function (number, precision, reverseShift) {
        if (reverseShift) {
            precision = -precision;
        }  
        let numArray = ("" + number).split("e");
        return +(numArray[0] + "e" + (numArray[1] ? (+numArray[1] + precision) : precision));
    };
    return shift(Math.round(shift(number, precision, false)), precision, true);
}

function addTdElement(p, className, data) {
    let td = document.createElement("td");
    td.className = className
    td.innerText = data
    p.appendChild(td)
}

function createTableHeader(vehicle) {
    let thead = document.createElement("thead");
    let tr = document.createElement("tr");
    thead.appendChild(tr);
    let headers = { battles: "Battles", winRate: "WinRate", wn8: "WN8" };    
    if (vehicle) {
        headers = { name: "Name", tier: "Tier", nation: "Nation", type: "Type", battles: "Battles", winRate: "WinRate", wn8: "WN8" };
    }
    for (let k in headers) {
        let th = document.createElement("th");
        th.className = "sort";
        th.setAttribute("data-sort", k);
        th.innerText = headers[k];
        tr.appendChild(th);
    }
    return thead;
}

function createTableRow(vehicle, stats) {
    let tr = document.createElement("tr");
    const vehicleType = { lightTank: "LT", mediumTank: "MT", heavyTank: "HT", "AT-SPG": "TD", SPG: "SPG" };
    if (vehicle) {
        addTdElement(tr, 'name', vehicle.name);
        addTdElement(tr, 'tier', vehicle.tier);
        addTdElement(tr, 'nation', vehicle.nation);
        addTdElement(tr, 'type', vehicleType[vehicle.type]);
    }
    addTdElement(tr, 'battles', stats.battles);
    addTdElement(tr, 'winRate', round(stats.wins / stats.battles * 100, 2).toFixed(2));
    addTdElement(tr, 'wn8', round(stats.wn8, 0));
    return tr
}

function fetchVehicleDB() {
    let httpObj = new XMLHttpRequest();
    httpObj.open("get", getUrlVehicledb(), true);
    httpObj.onload = function(){
        vehicleDB = JSON.parse(this.responseText);
    }
    httpObj.send(null);
}

function addTable() {
    let nickname = document.forms.formPlayerstats.nickname.value;
    let httpObj = new XMLHttpRequest();
    httpObj.open("get", getUrlPlayerstats(), true);
    httpObj.onload = function(){
        let data = JSON.parse(this.responseText);
        {
            let p = document.getElementById("total");
            p.textContent = null;
            let div = document.createElement("div");
            p.appendChild(div);
            div.innerText = "player: " + nickname;
            let totalStats = document.createElement("table");
            totalStats.appendChild(createTableHeader(false));
            totalStats.appendChild(createTableRow(null, data.total));
            p.appendChild(totalStats);
        }

        {
            let p = document.getElementById("users");
            p.textContent = null;
            let vehicleStats = document.createElement("table");
            vehicleStats.appendChild(createTableHeader(true));
        
            let tbody = document.createElement("tbody");
            tbody.className = "list";
            vehicleStats.appendChild(tbody);

            for (let k in data.vehicles) {
                tbody.appendChild(createTableRow(vehicleDB.data[k], data.vehicles[k]));
            }
            p.appendChild(vehicleStats);
        }
        let options = {
            valueNames: [ 'name', 'tier', 'nation', 'type', 'battles', 'winrate', 'wn8' ]
        };
        userList = new List('users', options);
    }
    httpObj.send(null);
}

function redirectPlayerstats() {
    window.location.href = getUrlPlayerstats();
}

function redirectVehicledb() {
    window.location.href = getUrlVehicledb();
}

var vehicleDB;

window.onload = function(){
    fetchVehicleDB();
}

