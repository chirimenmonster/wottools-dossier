

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


function addTable() {
    playerStats.fetch.call(playerStats, RES.PLAYER_STATS, function(self){
        let data = self.database[RES.PLAYER_STATS];
        {
            let p = document.getElementById("total");
            p.textContent = null;
            let div = document.createElement("div");
            p.appendChild(div);
            div.innerText = "player: " + self.nickname;
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

            let vehicles = self.database[RES.VEHICLE_LIST].data
            for (let k in data.vehicles) {
                tbody.appendChild(createTableRow(vehicles[k], data.vehicles[k]));
            }
            p.appendChild(vehicleStats);
        }
        let options = {
            valueNames: [ 'name', 'tier', 'nation', 'type', 'battles', 'winRate', 'wn8' ]
        };
        userList = new List('users', options);
    });
}

const RES = {
    PLAYER_STATS: 'playerstats.json',
    VEHICLE_LIST: 'vehicledb.json'
};

PlayerStats = function(){
    this.database = {};
};

PlayerStats.prototype.redirect = function(path){
    window.location.href = this.getURL(path);
};

PlayerStats.prototype.getURL = function(path){
    let query = null;
    switch (path) {
    case RES.PLAYER_STATS:
        this.nickname = document.forms.formPlayerstats.nickname.value;
        query = '?nickname=' + this.nickname;
    }
    let url = path + (query || '');
    return url;
};

PlayerStats.prototype.fetch = function(path, callback){
    let self = this;
    let httpObj = new XMLHttpRequest();
    httpObj.open('get', this.getURL(path), true);
    httpObj.onload = function(){
        self.database[path] = JSON.parse(httpObj.responseText);
        if (callback) {
            callback(self);
        }
    }
    httpObj.send(null);
};


var playerStats = new PlayerStats();

window.addEventListener('load', playerStats.fetch.call(playerStats, RES.VEHICLE_LIST));


