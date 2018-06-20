

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

PlayerStats.prototype.fetchVehicleList = function(){
    let path = RES.VEHICLE_LIST;
    let url = this.getURL(path);
    fetch(url)
    .then(response => response.json())
    .then(json => this.database[path] = json)
    .catch(error => console.error(error));
};

PlayerStats.prototype.fetchPlayerStats = function(){
    let path = RES.PLAYER_STATS;
    let url = this.getURL(path);
    fetch(url)
    .then(response => {
        if (!response.ok) {
            response.text()
            .then(text => this.showError(text));
        } else {
            response.json()
            .then(json => this.database[path] = json)
            .then(() => this.addTable());
        }
    })
    .catch(error => this.showError(error));
};

PlayerStats.prototype.showError = function(error){
    document.getElementById('total').textContent = error;
    document.getElementById('users').textContent = null;
};

PlayerStats.prototype.addTable = function(){
    let data = this.database[RES.PLAYER_STATS];
    {
        let p = document.getElementById('total');
        p.textContent = null;
        let div = document.createElement('div');
        p.appendChild(div);
        div.innerText = 'player: ' + this.nickname;
        let totalStats = document.createElement('table');
        totalStats.appendChild(createTableHeader(false));
        totalStats.appendChild(createTableRow(null, data.total));
        p.appendChild(totalStats);
    }
    {
        let p = document.getElementById('users');
        p.textContent = null;
        let vehicleStats = document.createElement('table');
        vehicleStats.appendChild(createTableHeader(true));
        
        let tbody = document.createElement('tbody');
        tbody.className = 'list';
        vehicleStats.appendChild(tbody);

        let vehicles = this.database[RES.VEHICLE_LIST].data;
        for (let k in data.vehicles) {
            tbody.appendChild(createTableRow(vehicles[k], data.vehicles[k]));
        }
        p.appendChild(vehicleStats);
    }
    let options = {
        valueNames: [ 'name', 'tier', 'nation', 'type', 'battles', 'winRate', 'wn8' ]
    };
    userList = new List('users', options);
    return this;
};


var playerStats = new PlayerStats();

window.addEventListener('load', () => playerStats.fetchVehicleList());


