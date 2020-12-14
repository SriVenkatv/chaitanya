#!/usr/bin/python
import easysnmp
import time
from datetime import datetime
import sqlite3
from easysnmp import Session
from sqlite3 import Error


VL = 'DEFAULT_VLAN(1)'
def create_tables(conn):
    create_table_reports = """ CREATE TABLE IF NOT EXISTS reports (
                                Device VARCHAR (255) null,
                                VLANS VARCHAR (255) NULL,
                                port VARCHAR (255) NOT NULL,
                                MACS VARCHAR (255) NOT NULL
                            ); """
    try:
        c = conn.cursor()
        c.execute(create_table_reports)
    except Error as e:
        print(e)
        
def get_connection(db_file):
    result = None
    try:
        result = sqlite3.connect(db_file)
    except Error as e:
        print(e)
        result = None
    return result

def start():
    conn = get_connection('./report.db')
    conn_switch = get_connection('./device.db')
    
    if conn and conn_switch:
        create_tables(conn)
        data = conn_switch.execute('Select * from switches')
        for items in data:
            ip = items[0]; port=int(items[1]); community=items[2]; version=int(items[3])
            probe_device(ip, port, community, version, conn, conn_switch)
        
    if conn:
        conn.close()
    if conn_switch:
        conn_switch.close()

            
def probe_device(ip, port, community, version, conn, conn_switch):
    oids = {'dot1dTpFdbEntryAddress':'1.3.6.1.2.1.17.4.3.1.1',
            'dot1dTpFdbEntryPort':'1.3.6.1.2.1.17.4.3.1.2',
            'dot1qTpFdbEntryStatus':'1.3.6.1.2.1.17.4.3.1.3',
            'dot1qTpFdbAddress':'1.3.6.1.2.17.7.1.2.2.1.1',
            'dot1qTpFdbPort':'1.3.6.1.2.1.17.7.1.2.2.1.2',
            'dot1qTpFdbStatus':'1.3.6.1.2.1.17.7.1.2.2.1.3',
            'dot1qVlanStaticName':'1.3.6.1.2.1.17.7.1.4.3.1.1',
            'sysDescr':'1.1.3.6.1.2.1.1.1',
            'dot1dBasePortIfIndex':'1.3.6.1.2.1.17.1.4.1.2',
            'vlans':'1.3.6.1.2.1.17.7.1.4.3.1.4'}
    
    print('probe_device= %s %s' % (ip, port))
    try:
        session = Session(hostname=ip, remote_port=port, version=version, community=community)
    except Exception as e:
        print(e)
        update_failed_attempts(ip, port, conn_switch)
        return

    start = str(datetime.fromtimestamp(int(time.time())))
    try:
        macs = session.walk(oids['dot1dTpFdbEntryAddress'])
        ports = session.walk(oids['dot1dTpFdbEntryPort'])
        for m,p in zip(macs, ports):
            oid = m.oid; oid_index = m.oid_index; snmp_type=m.snmp_type
            mac = ':'.join('{:02x}'.format(ord(a)) for a in m.value)
            portval = p.value
            print(ip,mac,portval)
            
            data = conn.execute("SELECT * from reports where (port=? and Device=?)",(portval,ip))
            fetch_data = data.fetchall()
            for connected_macs in fetch_data:
                m = connected_macs[3]
            
            if len(fetch_data)==0:
                print(ip,mac,portval)
                conn.execute('''INSERT INTO reports(Device, VLANS, port, MACS) values (?,?,?,?)''',(ip,VL,portval,mac))
                conn.commit()
            elif len(fetch_data)==1 and m.find(mac)==-1:
                finalmac = m+","+mac
                conn.execute("UPDATE reports set MACS=? where port=?",(finalmac,portval))
                conn.commit()

        vlansnum = []
        vlanname = []
        vlans = session.walk(oids['vlans'])
        vlanindex = session.walk(oids['dot1qVlanStaticName'])
        values = []
        vlan_oids = []
        
        for index, vlan in zip(vlanindex, vlans):
            value = ':'.join('{:02x}'.format(ord(x)) for x in vlan.value)
            values = value.split(':')
            oid = vlan.oid
            vlan_oids.append(oid)
            vname = index.value
            vnums = oid.split('.')
            vnum = str(vnums[-1])
            combine = ''
            if vname != VL:
                for i in range(len(values)):
                    hexlist = values
                    mac_hex = hexlist[i]
                    scale = 16
                    no_of_bits = 8
                    orghex = bin(int(mac_hex, scale))[2:].zfill(no_of_bits)
                    combine = combine + str(orghex)
                    orghex = ''
                    listvls = list(combine)
                for i in range(len(listvls)):
                    if listvls[i] == '1':
                        num = i + 1
                        vlanname.append(str(vname) + '(' + vnum + ')')
                        vlansnum.append(num)
        for i in range(len(vlansnum)):
            portlan = '1'
            conn.execute("update reports set VLANS = ? where port=?", (vlanname[i],vlansnum[i]))
            conn.commit()
    except Exception as e:
        print(str(e)+' '+str(ip)+":"+str(port))

    finish = str(datetime.fromtimestamp(int(time.time())))
    print('ok!')
    conn_switch.execute("update switches set first_probetime=?, latest_probetime=? where (ip=? and port=?)",(start, finish, ip, port))
    conn_switch.commit()


def update_failed_attempts(ip, port, conn):
    ddata = conn.execute("select failed_attempts from switches where ip=? and port=?", (ip, port))
    fetch_data = data.fetchall()
    
    failed_attempts = 1
    if len(fetch_data) > 0:
        failed_attempts = int(fetch_data[0][0]) + 1

    conn.execute("update switches set failed_attempts=? where (ip=? and port=?)", (failed_attempts, ip, port))
    conn.commit()

  #  print("Database updated!")
if  __name__=='__main__':
    while True:
        start()
        print('sleeping')
        time.sleep(60)
