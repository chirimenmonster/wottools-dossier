

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



function createTableRow(vehicle, stats) {
    let tr = document.createElement('tr');
    const vehicleType = { lightTank: 'LT', mediumTank: 'MT', heavyTank: 'HT', 'AT-SPG': 'TD', SPG: 'SPG', '': '' };
    if (vehicle !== null) {
        let data = vehicle.data;
        if (!data) {
            data = { name: '(unknown)', tier: '', nation: '', type: '', tank_id: '' };
        }
        {
            let td = document.createElement('td');
            td.className = 'name';
            tr.appendChild(td);
            let tankId = document.createElement('span');
            tankId.className = 'tankId';
            tankId.innerText = vehicle.id;
            let name = document.createElement('span');
            name.className = 'tankName';
            name.innerText = data.name;
            td.appendChild(tankId);
            td.appendChild(name);
        }
        addTdElement(tr, 'tier', data.tier);
        addTdElement(tr, 'nation', data.nation);
        addTdElement(tr, 'type', vehicleType[data.type]);
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
        totalStats.appendChild(this.createTableHeader(false));
        totalStats.appendChild(createTableRow(null, data.total));
        p.appendChild(totalStats);
    }
    {
        let p = document.getElementById('users');
        p.textContent = null;
        let vehicleStats = document.createElement('table');
        vehicleStats.appendChild(this.createTableHeader(true));
        
        let tbody = document.createElement('tbody');
        tbody.className = 'list';
        vehicleStats.appendChild(tbody);

        let vehicles = this.database[RES.VEHICLE_LIST].data;
        for (let k in data.vehicles) {
            tbody.appendChild(createTableRow({ id: k, data: vehicles[k] }, data.vehicles[k]));
        }
        p.appendChild(vehicleStats);
    }
    let options = {
        valueNames: [ 'name', 'tier', 'nation', 'type', 'battles', 'winRate', 'wn8' ]
    };
    this.order = { tier: -1, nation: 1, type: 1, tankName: 1, tankId: 1 };
    this.sortPrepare();
    this.sortByTankName();
    this.sortByType();
    this.sortByNation();
    this.sortByTier();
    this.sortApply();
    //userList = new List('users', options);
    return this;
};

PlayerStats.prototype.createTableHeader = function(vehicle){
    let thead = document.createElement("thead");
    let tr = document.createElement("tr");
    thead.appendChild(tr);
    let headers = { battles: "Battles", winRate: "WinRate", wn8: "WN8" };    
    if (vehicle) {
        headers = { name: "Name", tier: "Tier", nation: "Nation", type: "Type", battles: "Battles", winRate: "WinRate", wn8: "WN8" };
    }
    for (let k in headers) {
        let th = document.createElement('th');
        th.className = k;
        //th.className = "sort";
        //th.setAttribute("data-sort", k);
        th.innerText = headers[k];
        tr.appendChild(th);
    }
    {
        let e = tr.querySelector('th.name');
        if (e)
            e.addEventListener('click', () => { this.sortByTankName(); this.sortApply(); });
    }
    {
        let e = tr.querySelector('th.tier');
        if (e)
            e.addEventListener('click', () => { this.sortByTier(); this.sortApply(); });
    }
    {
        let e = tr.querySelector('th.nation');
        if (e)
            e.addEventListener('click', () => { this.sortByNation(); this.sortApply(); });
    }
    {
        let e = tr.querySelector('th.type');
        if (e)
            e.addEventListener('click', () => { this.sortByType(); this.sortApply(); });
    }
    return thead;
};

PlayerStats.prototype.sortPrepare = function(){
    const nationOrder = { ussr: 0, germany: 1, usa: 2, china: 3, france: 4, uk: 5, japan: 6, czech: 7, sweden: 8, poland: 9, italy: 10, '': 11 };
    const typeOrder = { LT: 0, MT: 1, HT: 2, TD: 3, SPG: 4, '': 5 };
    this.tbody = document.querySelector('#users tbody.list');
    this.dom = Array.from(this.tbody.querySelectorAll('tr'))
        .map((v) => {
            let tier = v.querySelector('.tier').innerHTML;
            let nation = nationOrder[v.querySelector('.nation').innerHTML];
            let type = typeOrder[v.querySelector('.type').innerHTML];
            let tankId = v.querySelector('.tankId').innerHTML;
            let name = v.querySelector('.tankName').innerHTML;
            return { dom: v, tier: tier, nation: nation, type: type, name: name, tankId: tankId };
        });
};

PlayerStats.prototype.sortApply = function(){
    this.dom.forEach((e) => this.tbody.appendChild(e.dom));
};

PlayerStats.prototype.sortByTier = function(){
    this.dom.sort((a, b) => (a.tier - b.tier) * this.order.tier)
    this.order.tier = - this.order.tier;
};

PlayerStats.prototype.sortByNation = function(){
    this.dom.sort((a, b) => (a.nation - b.nation) * this.order.nation);
    this.order.nation = - this.order.nation;    
};

PlayerStats.prototype.sortByType = function(){
    this.dom.sort((a, b) => (a.type - b.type) * this.order.type);
    this.order.type = - this.order.type;    
};

PlayerStats.prototype.sortByTankName = function(){
    this.dom.sort((a, b) => a.name.localeCompare(b.name) * this.order.tankName);
    this.order.tankName = - this.order.tankName;    
};

PlayerStats.prototype.sortByTankId = function(){
    this.dom.sort((a, b) => (a.tankId - b.tankId) * this.order.tankName);
    this.order.tankId = - this.order.tankId;    
};

var playerStats = new PlayerStats();

//window.addEventListener('load', () => playerStats.fetchVehicleList());
