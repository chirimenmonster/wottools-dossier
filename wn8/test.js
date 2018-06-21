

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
    let td = document.createElement('td');
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
    let tr = document.createElement('tr');
    const vehicleType = { lightTank: 'LT', mediumTank: 'MT', heavyTank: 'HT', 'AT-SPG': 'TD', SPG: 'SPG', '': '' };
    if (vehicle !== null) {
        if (!vehicle) {
            vehicle = { name: '(unknown)', tier: '', nation: '', type: '' };
        }
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

PlayerStats.prototype.fetch = function(path){
    let url = this.getURL(path);
    if (this.database[path]) {
        return this.database[path];
    }
    return fetch(url)
        .then(response => {
            if (response.ok) {
               return response.json()
                    .then(json => this.database[path] = json.result);
            } else {
                return response.json()
                    .then(json => Promise.reject(json.error));
            }
        });
};

PlayerStats.prototype.fetchAll = function(){
    this.database[RES.PLAYER_STATS] = null;
    let targets = [ RES.VEHICLE_LIST, RES.PLAYER_STATS ];
    Promise.all(targets.map(target => this.fetch(target)))
        .then(() => this.addTable())
        .catch(error => this.showError(error));
};

PlayerStats.prototype.showError = function(error){
    let text = error.message + ', ' + error.description;
    console.log('error: ' + text)
    document.getElementById('total').textContent = text;
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
    this.sort();
    //userList = new List('users', options);
    return this;
};

PlayerStats.prototype.sort = function(){
    const nationOrder = { ussr: 0, germany: 1, usa: 2, china: 3, france: 4, uk: 5, japan: 6, czech: 7, sweden: 8, poland: 9, italy: 10, '': 11 };
    const typeOrder = { LT: 0, MT: 1, HT: 2, TD: 3, SPG: 4, '': 5 };
    let tbody = document.querySelector('#users tbody.list');
    let a = Array.from(tbody.querySelectorAll('tr'))
    .map(function(v){
        let tier = v.querySelector('.tier').innerHTML;
        let nation = nationOrder[v.querySelector('.nation').innerHTML];
        let type = typeOrder[v.querySelector('.type').innerHTML];
        let name = v.querySelector('.name').innerHTML;
        return { dom: v, tier: tier, nation: nation, type: type, name: name };
    })
    .sort(function(a, b){ return (b.tier - a.tier) * 100000 + (a.nation - b.nation) * 1000 + (a.type - b.type) * 10 })
    .forEach(function(v){ tbody.appendChild(v.dom) });
};

var playerStats = new PlayerStats();

//window.addEventListener('load', () => playerStats.fetchVehicleList());
