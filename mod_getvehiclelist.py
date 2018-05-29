import os
import csv
import nations
from items.vehicles import g_list
from PlayerEvents import g_playerEvents

LOG_FILE = 'mods/logs/vehiclelist.csv'

def init():
    print 'mod getvehiclelist'
    g_playerEvents.onAccountBecomePlayer += getVehicleList


def getVehicleList():
    rows = []
    for nationId in nations.INDICES.values():
        for v in g_list.getList(nationId).values():
            descr = ( v.compactDescr, nationId, v.id, v.name )
            rows.append(descr)
    rows = sorted(rows, key=lambda x: (x[1], x[2]))
    
    try:
        os.makedirs(os.path.dirname(LOG_FILE))
    except:
        pass
    with open(LOG_FILE, 'wb') as f:
        writer = csv.writer(f, dialect='excel')
        writer.writerows(rows)
