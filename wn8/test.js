
var parsedUrl = new URL(window.location.href);
nickname = parsedUrl.searchParams.get("nickname");

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

function addTable() {
    let form = document.forms.test;
    let nickname = form.nickname.value;
    httpObj = new XMLHttpRequest();
    httpObj.open("get", "playerstats.json?nickname=" + nickname, true);
    httpObj.onload = function(){
        let data = JSON.parse(this.responseText);
        let p = document.getElementById("test");
        p.textContent = null;
        let div = document.createElement("p");
        p.appendChild(div);
        div.innerText = "player=" + nickname;
        let table = document.createElement("table");
        p.appendChild(table);
        {
            let tr = document.createElement("tr");
            table.appendChild(tr);
            let headers = { tankId: "tank_id", battles: "battles", winRate: "winRate", wn8: "WN8" }
            for (let k in headers) {
                let th = document.createElement("th");
                th.className = k;
                th.innerText = headers[k];
                tr.appendChild(th);
            }
        }
        for (let k in data.vehicles) {
            let tr = document.createElement("tr");
            table.appendChild(tr);
            let battles = data.vehicles[k].battles
            addTdElement(tr, 'tankId', k);
            addTdElement(tr, 'battles', battles);
            addTdElement(tr, 'winRate', round(data.vehicles[k].wins / battles * 100, 1).toFixed(1));
            addTdElement(tr, 'wn8', round(data.vehicles[k].wn8, 0));
        }
    }
    httpObj.send(null);
}
