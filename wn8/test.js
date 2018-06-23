

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

const vehicleType = { lightTank: 'LT', mediumTank: 'MT', heavyTank: 'HT', 'AT-SPG': 'TD', SPG: 'SPG', '': '' };

class PlayerStats {
    constructor() {
        this.database = {};
        const unknown = '(unknown)';
        this.sortOrder = {
            tier: (a, b) => (a.tier === '') ? 1 : (b.tier === '') ? -1 : (b.tier - a.tier) * this.order['tier'],
            nation: (a, b) => (a.nation === '') ? 1 : (b.nation === '') ? -1 : (a.nation - b.nation) * this.order['nation'],
            type: (a, b) => (a.type === '') ? 1 : (b.type === '') ? -1 : (a.type - b.type) * this.order['type'],
            name: (a, b) => (a.name === unknown) ? 1 : (b.name === unknown) ? -1 : a.name.localeCompare(b.name) * this.order['name'],
            tankId: (a, b) => (a.tankId - b.tankId) * this.order['tankId']
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

    createVehicleStats() {
        const nationOrder = { ussr: 0, germany: 1, usa: 2, china: 3, france: 4,
            uk: 5, japan: 6, czech: 7, sweden: 8, poland: 9, italy: 10, '': '' };
        const typeOrder = { LT: 0, MT: 1, HT: 2, TD: 3, SPG: 4, '': '' };
        this.order = { tier: 1, nation: 1, type: 1, name: 1, tankId: 1 };
        this.dom = [];
        let stats = this.database[RES.PLAYER_STATS].vehicles;
        let infos = this.database[RES.VEHICLE_LIST].data;
        for (let k in stats) {
            let vehicle = infos[k];
            if (!vehicle) {
                vehicle = { name: '(unknown)', tier: '', nation: '', type: '', tank_id: '' };
            }
            let row = createTableRow({ id: k, data: vehicle }, stats[k]);
            this.dom.push({
                dom: row,
                tier: vehicle.tier,
                nation: nationOrder[vehicle.nation],
                type: typeOrder[vehicleType[vehicle.type]],
                tankId: vehicle.tank_id,
                name: vehicle.name
            });
        }
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

PlayerStats.prototype.addTable = function(){
    let data = this.database[RES.PLAYER_STATS];
    {
        let p = document.getElementById('total');
        p.textContent = null;
        let div = document.createElement('div');
        p.appendChild(div);
        div.innerText = 'player: ' + this.nickname;
        let totalStats = document.createElement('table');
        totalStats.appendChild(this.createTotalTableHeader());
        totalStats.appendChild(createTableRow(null, data.total));
        p.appendChild(totalStats);
    }
    {
        let p = document.getElementById('users');
        p.textContent = null;
        let vehicleStats = document.createElement('table');
        vehicleStats.appendChild(this.createVehicleTableHeader());
        
        let tbody = document.createElement('tbody');
        tbody.className = 'list';
        vehicleStats.appendChild(tbody);
        this.tbody = tbody;
        p.appendChild(vehicleStats);
    }
    this.createVehicleStats();
    [ 'name', 'type', 'nation', 'tier' ]
        .map(k => this.sort(k, false));
    this.sort(null, true);
    return this;
};

var playerStats = new PlayerStats();
