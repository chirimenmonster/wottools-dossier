

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


const RES = {
    PLAYER_STATS: 'playerstats.json',
    VEHICLE_LIST: 'vehicledb.json'
};

class PlayerTotalStats {
    constructor(stats) {
        this.stats = stats;
        this.battles = stats.battles;
        this.winRate = round(stats.wins / stats.battles * 100, 2).toFixed(2);
        this.wn8 = round(stats.wn8, 0);
    }
}

class PlayerVehicleStats {
    constructor(stats, vehicle) {
        const vehicleType = { lightTank: 'LT', mediumTank: 'MT', heavyTank: 'HT', 'AT-SPG': 'TD', SPG: 'SPG', '': '' };
        this.stats = stats;
        this.vehicle = vehicle;
        this.tier = vehicle.tier;
        this.nation = vehicle.nation;
        this.type = vehicleType[vehicle.type];
        this.name = vehicle.name;
        this.battles = stats.battles;
        this.winRate = round(stats.wins / stats.battles * 100, 2).toFixed(2);
        this.wn8 = round(stats.wn8, 0);
    }
}

class PlayerStats {
    constructor() {
        this.database = {};
        this.vehicleType = { lightTank: 'LT', mediumTank: 'MT', heavyTank: 'HT', 'AT-SPG': 'TD', SPG: 'SPG', '': '' };
        const unknown = '(unknown)';
        this.sortOrder = {
            tier: (a, b) => (a.tier === '') ? 1 : (b.tier === '') ? -1 : (b.tier - a.tier) * this.order['tier'],
            nation: (a, b) => (a.nation === '') ? 1 : (b.nation === '') ? -1 : (a.nation - b.nation) * this.order['nation'],
            type: (a, b) => (a.type === '') ? 1 : (b.type === '') ? -1 : (a.type - b.type) * this.order['type'],
            name: (a, b) => (a.name === unknown) ? 1 : (b.name === unknown) ? -1 : a.name.localeCompare(b.name) * this.order['name'],
            tankId: (a, b) => (a.tankId - b.tankId) * this.order['tankId']
        };
        this.value = {
            tier: (tankId) => this.database[RES.VEHICLE_LIST].data[tankId].tier,
            nation: (tankId) => this.database[RES.VEHICLE_LIST].data[tankId].nation,
            type: (tankId) => this.vehicleType[this.database[RES.VEHICLE_LIST].data[tankId].type],
            name: (tankId) => this.database[RES.VEHICLE_LIST].data[tankId].name,
            battles: (tankId) => {
                let stats = tankId ?
                    this.database[RES.PLAYER_STATS].vehicles[tankId] :
                    this.database[RES.PLAYER_STATS].total;
                return stats.battles
            },
            winRate: (tankId) => {
                let stats = tankId ?
                    this.database[RES.PLAYER_STATS].vehicles[tankId] :
                    this.database[RES.PLAYER_STATS].total;
                return round(stats.wins / stats.battles * 100, 2).toFixed(2);
            },
            wn8: (tankId) => {
                let stats = tankId ?
                    this.database[RES.PLAYER_STATS].vehicles[tankId] :
                    this.database[RES.PLAYER_STATS].total;
                return round(stats.wn8, 0);
            }
        };
    }
    
    redirect(path) {
        window.location.href = this.getURL(path);
    }

    getURL(path) {
        let query = null;
        switch (path) {
            case RES.PLAYER_STATS:
                this.nickname = document.forms.formPlayerstats.nickname.value;
                query = '?nickname=' + this.nickname;
        }
        let url = path + (query || '');
        return url;
    }

    fetch(path) {
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
    }

    fetchAll() {
        this.database[RES.PLAYER_STATS] = null;
        let targets = [ RES.VEHICLE_LIST, RES.PLAYER_STATS ];
        Promise.all(targets.map(target => this.fetch(target)))
            .then(() => this.addTable())
            .catch(error => this.showError(error));
    }

    showError(error) {
        let text = error.message + ', ' + error.description;
        console.log('error: ' + text)
        document.getElementById('total').textContent = text;
        document.getElementById('users').textContent = null;
    }

    createTd(className, data) {
        let td = document.createElement('td');
        td.className = className;
        td.innerText = data;
        return td;
    }

    addTable() {
        let divTotal = document.getElementById('total');
        divTotal.textContent = null;
        divTotal.appendChild(this.createPlayerView());
        divTotal.appendChild(this.createTotalTable());
        let divVehicle = document.getElementById('users');
        divVehicle.textContent = null;
        divVehicle.appendChild(this.createVehicleTable());
        return this;
    }

    createPlayerView() {
        let div = document.createElement('div');
        div.innerText = 'player: ' + this.nickname;
        return div;
    }

    createTotalTable() {
        let table = document.createElement('table');
        table.appendChild(this.createTotalTableHeader());
        table.appendChild(this.createTotalTableBody());
        return table;
    }

    createTotalTableHeader() {
        let thead = document.createElement('thead');
        let tr = document.createElement('tr');
        thead.appendChild(tr);
        let headers = { battles: 'Battles', winRate: 'WinRate', wn8: 'WN8' };
        for (let k in headers) {
            let th = document.createElement('th');
            th.className = k;
            th.innerText = headers[k];
            tr.appendChild(th);
        }
        return thead;
    }

    createTotalTableBody() {
        let tbody = document.createElement('tbody');
        let stats = new PlayerTotalStats(this.database[RES.PLAYER_STATS].total);
        tbody.appendChild(this.createTotalTableRow(stats));
        return tbody;
    }

    createVehicleTable() {
        let table = document.createElement('table');
        table.appendChild(this.createVehicleTableHeader());
        table.appendChild(this.createVehicleTableBody());
        return table;
    }
    
    createVehicleTableHeader() {
        let thead = document.createElement('thead');
        let tr = document.createElement('tr');
        thead.appendChild(tr);
        let headers = { name: 'Name', tier: 'Tier', nation: 'Nation', type: 'Type',
                battles: 'Battles', winRate: 'WinRate', wn8: 'WN8' };
        this.vehicleTableHeader = {};
        for (let k in headers) {
            let th = document.createElement('th');
            th.className = k;
            th.innerText = headers[k];
            tr.appendChild(th);
            this.vehicleTableHeader[k] = th;
        }
        [ 'name', 'tier', 'nation', 'type' ]
            .map(k => this.vehicleTableHeader[k].addEventListener('click', () => this.sort(k, true)));
        return thead;
    }

    createVehicleTableBody() {
        let tbody = document.createElement('tbody');
        this.tbody = tbody;
        this.createVehicleStats();
        [ 'name', 'nation', 'type', 'tier' ]
            .map(k => this.sort(k, false));
        this.sort(null, true);
        return tbody;
    }
    
    createVehicleStats() {
        const nationOrder = { ussr: 0, germany: 1, usa: 2, china: 3, france: 4,
            uk: 5, japan: 6, czech: 7, sweden: 8, poland: 9, italy: 10, '': '' };
        const typeOrder = { HT: 0, MT: 1, LT: 2, TD: 3, SPG: 4, '': '' };
        this.order = { tier: 1, nation: 1, type: 1, name: 1, tankId: 1 };
        this.dom = [];
        let stats = this.database[RES.PLAYER_STATS].vehicles;
        let infos = this.database[RES.VEHICLE_LIST].data;
        for (let k in stats) {
            let vehicle = infos[k];
            if (!vehicle) {
                vehicle = { name: '(unknown)', tier: '', nation: '', type: '', tank_id: '' };
            }
            let playerVehicleStats = new PlayerVehicleStats(stats[k], vehicle);
            let row = this.createVehicleTableRow(playerVehicleStats);
            this.dom.push({
                dom: row,
                tier: vehicle.tier,
                nation: nationOrder[vehicle.nation],
                type: typeOrder[this.vehicleType[vehicle.type]],
                tankId: vehicle.tank_id,
                name: vehicle.name
            });
        }
    }

    createVehicleTableRow(stats) {
        let tr = document.createElement('tr');
        tr.appendChild(this.createTd('name', stats.name));
        tr.appendChild(this.createTd('tier', stats.tier));
        tr.appendChild(this.createTd('nation', stats.nation));
        tr.appendChild(this.createTd('type', stats.type));
        tr.appendChild(this.createTd('battles', stats.battles));
        tr.appendChild(this.createTd('winRate', stats.winRate));
        tr.appendChild(this.createTd('wn8', stats.wn8));
        return tr;
    }

    createTotalTableRow(stats) {
        let tr = document.createElement('tr');
        tr.appendChild(this.createTd('battles', stats.battles));
        tr.appendChild(this.createTd('winRate', stats.winRate));
        tr.appendChild(this.createTd('wn8', stats.wn8));
        return tr;
    }

    sort(key, isApply) {
        if (key) {
            this.dom.sort((a, b) => this.sortOrder[key](a, b));
            this.order[key] = - this.order[key];
            this.lastSortKey = key;
            let e = this.vehicleTableHeader[key];
            if (e) {
                if (this.order[key] > 0) {
                    e.classList.remove('desc');
                    e.classList.add('asc');
                } else {
                    e.classList.remove('asc');
                    e.classList.add('desc');
                }
            }
        }
        if (isApply) {
            this.dom.forEach((e) => this.tbody.appendChild(e.dom));
            [ 'name', 'tier', 'nation', 'type' ]
                .map(k => {
                    let e = this.vehicleTableHeader[k];
                    if (k !== this.lastSortKey) {
                        e.classList.remove('asc');
                        e.classList.remove('desc');
                    } else {
                        if (this.order[key] > 0) {
                            e.classList.remove('desc');
                            e.classList.add('asc');
                        } else {
                            e.classList.remove('asc');
                            e.classList.add('desc');
                        }
                    }
                });
        }
    }

}

var playerStats = new PlayerStats();
