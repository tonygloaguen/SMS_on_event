#!/usr/bin/python3

import sqlite3
import smtplib
import serial
import time
from email.mime.text import MIMEText
import automationhat
import threading
import tkinter
from tkinter import ttk
import datetime
import os,sys

def sendSMS(PhoneNbr,Msg,tx):
    
    global block
    block = 1
    
    try:
        
        dongle = serial.Serial(port1,115200,timeout = 1, rtscts=True)
        
        dongle.write(('ATZ\r').encode('utf-8'))
        time.sleep(1)
        
        dongle.write(('AT+CMGF=1\r').encode())
        time.sleep(2)
        
        print('Envoi SMS vers le numéro',str(PhoneNbr))
        
        dongle.write(('AT+CMGS="'+(PhoneNbr)+'"\r').encode())
        time.sleep(5)

        dongle.write((str(Msg)+"\r").encode())
        time.sleep(5)

        dongle.write((chr(26)).encode())
        time.sleep(5)
                    
        logtext.insert(1.0,'Envoi du message '+str(Msg)+' au numéro '+str(PhoneNbr)+' à '+str(tx)+'\r\n')
        logtext.grid(row=3,column=0)
        
        send = dongle.readlines()
        
        for ack in send:
            ack = (ack.decode('utf-8'))
            ack = ack.rstrip()
            ack = ack.lstrip()
            ack = ack.split(',')
        
        if 'OK' in ack:
            print('SMS envoyé')
        
        send.clear()
        
        dongle.close()
        
        block = 0
    except NameError:
        pass
    block = 0
    
def Test_SMS_entry(msg_SMS,PhoneNbr):
    
    t = datetime.datetime.now()
          
    if msg_SMS == "Test":
        sendSMS(PhoneNbr,'TestOK',t)
        killSMS()

    if msg_SMS == "Contact1On":
        automationhat.relay.one.on()
        killSMS()

    if msg_SMS == "Contact1Off":
        automationhat.relay.one.off()
        killSMS()
        
    if msg_SMS == "Contact2On":
        automationhat.relay.two.on()
        killSMS()

    if msg_SMS == "Contact2Off":
        automationhat.relay.two.off()
        killSMS()
        
    if msg_SMS == "Contact3On":
        automationhat.relay.three.on()
        killSMS()

    if msg_SMS == "Contact3Off":
        automationhat.relay.three.off()
        killSMS()
    
    if msg_SMS == "Param":
        if socket != 25:
            Para_msg = ('Email ='+str(socket)+' , '+smtp+' , '+Login+' , '+Pwd+' , '+AddFrom)
        else:
            Para_msg = ('Email ='+str(socket)+' , '+smtp+' , '+AddFrom)
        Para_msg2 = (' Msg = '+Msg1+' , '+Sbj1+' , '+Msg2+' , '+Sbj2+' , '+Msg3+' , '+Sbj3+' , '+str(Latency))
        sendSMS(PhoneNbr,Para_msg,t)
        sendSMS(PhoneNbr,Para_msg2,t)
        killSMS()
    
    if msg_SMS == "Annu":
        
        t = datetime.datetime.now()

        for Address in Addr:
                    envoi_email(Address[0],"Ceci est un test des paramètres et adresses email","Test général",t)

        for PhoneNbr in Phone:
                    sendSMS(PhoneNbr[0],'Ceci est un test des numeros de telephone',t)

        killSMS()
    
def read():
    try:
        
        dongle = serial.Serial(port1,115200,timeout = 1, rtscts=True)
        
        dongle.write(('ATZ\r').encode('utf-8'))
        time.sleep(1)

        dongle.write(('AT+CMGF=1\r').encode('utf-8'))# put in textmode
        time.sleep(5)

        dongle.write(('AT+CMGL="REC UNREAD"\r').encode('utf-8')) #fetch all sms's
        time.sleep(5)
        
        readstr = dongle.readlines()
        
        dongle.close()
        
        m = 0
        for msg in readstr:
            msg = (msg.decode('utf-8'))
            msg = msg.rstrip()
            msg = msg.lstrip()
            msg = msg.split(',')
            print(msg)
            try:
                print('Message du',msg[2],'le',(msg[4].replace('"',"")),'à',(msg[5].replace('"',"")))
                print((((readstr[m+1]).lstrip()).rstrip()).decode('utf-8'))
                msg_SMS = ((((readstr[m+1]).lstrip()).rstrip()).decode('utf-8'))
                print(msg_SMS)
                PhoneTel = (msg[2]).replace('"',"")
                try:
                    PhoneTel = PhoneTel.replace("+33","0")
                    PhoneTel = (PhoneTel.lstrip()).rstrip()
                except:
                    pass
                Test_SMS_entry(msg_SMS,PhoneTel)       
            except IndexError:
                pass
            m+=1
        readstr.clear()
    except NameError:
        pass
    
def killSMS():

    print("DELETING ALL MESSAGES")
    dongle = serial.Serial(port1,115200,timeout = 1, rtscts=True)
    dongle.write(("AT+CMGD=4\r").encode('utf-8'))
    time.sleep(2)
    dongle.close()

def envoi_email(Address,Msg,Sbj,tx):
    try:
        logtext.insert(1.0,"Envoi du message "+str(Msg)+" à l'adresse "+str(Address)+" à "+str(tx)+"\r\n")
        logtext.grid(row=3,column=0)
    except NameError:
        pass
    
    message = MIMEText(Msg)
    message['Subject'] = Sbj
    message['From'] = AddFrom
    message['To'] = str(Address)
    print("Envoi du mail à l'adresse "+(str(Address)))
    serveur = smtp+':'+str(socket)
    try:
        server = smtplib.SMTP(serveur)
        if socket == 25:
            try:
                server.send_message(message)
                server.quit()
            except (smtplib.SMTPSenderRefused,smtplib.SMTPAuthenticationError):
                print("Problème dans les paramètres SMTP")
                pass
            except smtplib.SMTPRecipientsRefused:
                print("L'adresse",str(Address),"n'est pas valide")

        else:
            server.starttls()
            server.login(Login,Pwd)
            try:
                server.send_message(message)
            except smtplib.SMTPRecipientsRefused:
                pass
            server.quit()
    except (smtplib.SMTPAuthenticationError,TimeoutError):
        print("Pb réseau")
        pass
    except:
        print("Problème dans les paramètres SMTP")
        pass
    

def create_base():

    conn = sqlite3.connect('/home/pi/Berthold_Alarm_v2/params.db')
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS params(
        Msg1 TEXT,
        Sbj1 TEXT,
        Msg2 TEXT,
        Sbj2 TEXT,
        Msg3 TEXT,
        Sbj3 TEXT,
        Latency TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Addrmail(
        AddrTo TEXT)
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Phonetel(
        PhoneNbr TEXT)
    """)
    conn.commit()
    conn.close()

def fill_base(param,value):

    conn = sqlite3.connect('/home/pi/Berthold_Alarm_v2/params.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO params("+param+") VALUES (?,?,?,?,?,?,?)",(value))
    conn.commit()
    conn.close()

def maj_base(param,value):
    conn = sqlite3.connect('/home/pi/Berthold_Alarm_v2/params.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE params SET "+param+" = ?",(value,))
    conn.commit()
    conn.close()

def read_value():

    global values_param

    conn = sqlite3.connect('/home/pi/Berthold_Alarm_v2/params.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM params LIMIT 1")
    values_param = cursor.fetchall()
    conn.close()

    lenght = len(values_param)

    if lenght == 0:
        fill_base("Msg1,Sbj1,Msg2,Sbj2,Msg3,Sbj3,Latency",("Msg1","Sbj1","Msg2","Sbj2","Msg3","Sbj3","5"))
        read_value()

def read_value_all():

    global values

    conn = sqlite3.connect('/home/pi/Berthold_Alarm_v2/params.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM params LIMIT 1")
    values = cursor.fetchall()
    conn.close()

def read_value_annuaire():

    global Addr
    global Phone

    conn = sqlite3.connect('/home/pi/Berthold_Alarm_v2/params.db')
    cursor = conn.cursor()
    cursor.execute("SELECT AddrTo FROM Addrmail")
    Addr = list(cursor.fetchall())
    cursor.execute("SELECT PhoneNbr FROM Phonetel")
    Phone = list(cursor.fetchall())
    conn.commit()
    conn.close()

def recup_para_exist():

    global Id, Mdp,Server,Port,AddFrom

    try:
        config = open('/home/pi/Berthold_Alarm_v2/config_email.ini',"r")
        paraemail = config.readline()
        paraemail = paraemail.split(",")
        Server = paraemail[0]
        Port = int(paraemail[1])
        AddFrom = paraemail[2]

        if Port != 25:

            Id = paraemail[3]
            Mdp = paraemail[4]

        config.close()
    except FileNotFoundError:
        pass

def Stockage_para_email():

    config = open('/home/pi/Berthold_Alarm_v2/config_email.ini',"w")
    if Port != 25:
        config.write(Server+","+str(Port)+","+AddFrom+","+Id+","+Mdp)
    if Port == 25:
        config.write(Server+","+str(Port)+","+AddFrom)
    config.close()

def liste_annuaire():

    def Ajouter(table,into,val,Cbliste,liste):

        conn = sqlite3.connect('/home/pi/Berthold_Alarm_v2/params.db')
        cursor = conn.cursor()
        SQL = "INSERT INTO "+table+"("+into+") VALUES (?)"
        cursor.execute(SQL,(val,))
        conn.commit()
        conn.close()

        read_value_annuaire()
        Cbliste = ttk.Combobox(annu_root,values=liste)
        Cbliste.grid(row=0,column=1)

    def delget(table,val,Cbliste,liste):

        Idt = Cbliste.current()
        Id = liste[Idt][0]
        conn = sqlite3.connect('/home/pi/Berthold_Alarm_v2/params.db')
        cursor = conn.cursor()
        SQL = "DELETE FROM "+table+" WHERE "+val+" = ?"
        cursor.execute(SQL,(Id,))
        conn.commit()
        conn.close()

        read_value_annuaire()
        Cbliste = ttk.Combobox(annu_root,values=liste)
        Cbliste.grid(row=0,column=1)

    read_value_annuaire()

    annu_root = tkinter.Toplevel(root)
    annu_root.title('Annuaire des destinataires')
    label1 = tkinter.Label(annu_root,text='Adresses email')
    label1.grid(row=0,column=0)
    Combo_liste1 = ttk.Combobox(annu_root,values=Addr)
    Combo_liste1.grid(row=0,column=1)
    bouton1 = tkinter.Button(annu_root,text="Effacer l'entrée",command=lambda : delget("Addrmail","AddrTo",Combo_liste1,Addr))
    bouton1.grid(row=0,column=2)
    entry1 = tkinter.Entry(annu_root)
    entry1.grid(row=0,column=3)
    bouton11 = tkinter.Button(annu_root,text="Ajouter l'entrée",command=lambda : Ajouter("Addrmail","AddrTo",str(entry1.get()),Combo_liste1,Addr))
    bouton11.grid(row=0,column=4)

    label2 = tkinter.Label(annu_root,text='Numéros de téléphone')
    label2.grid(row=1,column=0)
    Combo_liste2 = ttk.Combobox(annu_root,values=Phone)
    Combo_liste2.grid(row=1,column=1)
    bouton2 = tkinter.Button(annu_root,text="Effacer l'entrée",command=lambda : delget("Phonetel","PhoneNbr",Combo_liste2,Phone))
    bouton2.grid(row=1,column=2)
    entry2 = tkinter.Entry(annu_root)
    entry2.grid(row=1,column=3)
    bouton22 = tkinter.Button(annu_root,text="Ajouter l'entrée",command=lambda : Ajouter("Phonetel","PhoneNbr",str(entry2.get()),Combo_liste2,Phone))
    bouton22.grid(row=1,column=4)

    annu_root.mainloop()

def liste_para_email():

    def MAJ():
        
        global Id, Mdp,Server,Port,AddFrom
        
        Server = str(entryServer.get())
        Port = str(entryPort.get())
        AddFrom = str(entryAddFrom.get())
        Id = str(entryId.get())
        Mdp = str(entryMdp.get())
        Stockage_para_email()
        try:
            global socket,smtp,Login,Pwd
            
            socket = Port
            smtp = Server
            Login = Id
            Pwd = Mdp
        except NameError:
            pass
        param_root.destroy()

    global Id, Mdp,Server,Port,AddFrom

    recup_para_exist()

    param_root = tkinter.Toplevel(root)
    param_root.title('Paramètres emails')
    labelServer = tkinter.Label(param_root,text='Serveur SMTP')
    labelServer.grid(row=0,column=0)
    entryServer = tkinter.Entry(param_root)
    try:
        entryServer.insert(0,Server)
    except NameError:
        pass
    entryServer.grid(row=0,column=1)
    labelPort = tkinter.Label(param_root,text='Port SMTP')
    labelPort.grid(row=1,column=0)
    entryPort = tkinter.Entry(param_root)
    try:
        entryPort.insert(0,Port)
    except NameError:
        pass
    entryPort.grid(row=1,column=1)
    labelAddFrom = tkinter.Label(param_root,text="Adresse d'envoi email")
    labelAddFrom.grid(row=2,column=0)
    entryAddFrom = tkinter.Entry(param_root)
    try:
        entryAddFrom.insert(0,AddFrom)
    except NameError:
        pass
    entryAddFrom.grid(row=2,column=1)
    labelId = tkinter.Label(param_root,text='Identifiant')
    labelId.grid(row=3,column=0)
    entryId = tkinter.Entry(param_root)
    try:
        entryId.insert(0,Id)
    except NameError:
        pass
    entryId.grid(row=3,column=1)
    labelMdp = tkinter.Label(param_root,text='Mot de passe')
    labelMdp.grid(row=4,column=0)
    entryMdp = tkinter.Entry(param_root)
    try:
        entryMdp.insert(0,Mdp)
    except NameError:
        pass
    entryMdp.grid(row=4,column=1)

    boutonMAJ = tkinter.Button(param_root,text="Mettre à jour les paramètres",command=MAJ)
    boutonMAJ.grid(row=5,column=0)

    param_root.mainloop()

def liste_Msg():

    def MAJ_Msg():
        
        global values_param
        
        maj_base("Msg1",str(entryMsg1.get()))
        maj_base("Sbj1",str(entrySbj1.get()))
        maj_base("Msg2",str(entryMsg2.get()))
        maj_base("Sbj2",str(entrySbj2.get()))
        maj_base("Msg3",str(entryMsg3.get()))
        maj_base("Sbj3",str(entrySbj3.get()))
        maj_base("Latency",str(entryLatency.get()))
        
        read_value()
        
        global Msg1,Sbj1,Msg2,Sbj2,Msg3,Sbj3,Latency
        
        values_param = (values_param[0])
        Msg1 = values_param[0]
        Sbj1 = values_param[1]
        Msg2 = values_param[2]
        Sbj2 = values_param[3]
        Msg3 = values_param[4]
        Sbj3 = values_param[5]
        Latency = int(values_param[6])

        msg_root.destroy()


    msg_root = tkinter.Toplevel(root)
    msg_root.title('Messages et objets')

    labelMsg1 = tkinter.Label(msg_root,text='Message1')
    labelMsg1.grid(row=0,column=0)
    entryMsg1 = tkinter.Entry(msg_root)
    entryMsg1.insert(0,Msg1)
    entryMsg1.grid(row=0,column=1)
    labelSbj1 = tkinter.Label(msg_root,text='Objet1/Corps SMS1')
    labelSbj1.grid(row=1,column=0)
    entrySbj1 = tkinter.Entry(msg_root)
    entrySbj1.insert(0,Sbj1)
    entrySbj1.grid(row=1,column=1)
    labelMsg2 = tkinter.Label(msg_root,text="Message2")
    labelMsg2.grid(row=2,column=0)
    entryMsg2 = tkinter.Entry(msg_root)
    entryMsg2.insert(0,Msg2)
    entryMsg2.grid(row=2,column=1)
    labelSbj2 = tkinter.Label(msg_root,text='Objet1/Corps SMS2')
    labelSbj2.grid(row=3,column=0)
    entrySbj2 = tkinter.Entry(msg_root)
    entrySbj2.insert(0,Sbj2)
    entrySbj2.grid(row=3,column=1)
    labelMsg3 = tkinter.Label(msg_root,text='Message3')
    labelMsg3.grid(row=4,column=0)
    entryMsg3 = tkinter.Entry(msg_root)
    entryMsg3.insert(0,Msg3)
    entryMsg3.grid(row=4,column=1)
    labelSbj3 = tkinter.Label(msg_root,text='Objet1/Corps SMS3')
    labelSbj3.grid(row=5,column=0)
    entrySbj3 = tkinter.Entry(msg_root)
    entrySbj3.insert(0,Sbj3)
    entrySbj3.grid(row=5,column=1)
    labelLatency = tkinter.Label(msg_root,text='Latence')
    labelLatency.grid(row=6,column=0)
    entryLatency = tkinter.Entry(msg_root)
    entryLatency.insert(0,Latency)
    entryLatency.grid(row=6,column=1)

    boutonMAJ = tkinter.Button(msg_root,text="Mettre à jour les paramètres",command=MAJ_Msg)
    boutonMAJ.grid(row=7,column=0)

    msg_root.mainloop()

create_base()

read_value()

read_value_annuaire()
recup_para_exist()
try:
    global socket,smtp,Login,Pwd
    socket = Port
    smtp = Server
    Login = Id
    Pwd = Mdp
except NameError:
    pass

##read_value_all()

global Msg1,Sbj1,Msg2,Sbj2,Msg3,Sbj3,Latency

values_param = (values_param[0])

Msg1 = values_param[0]
Sbj1 = values_param[1]
Msg2 = values_param[2]
Sbj2 = values_param[3]
Msg3 = values_param[4]
Sbj3 = values_param[5]
Latency = int(values_param[6])

def main():
    
    timer = 0
    d1,d2,d3 = 0,0,0
    c1,c2,c3 = 0,0,0

    while True:
        
        tboot = datetime.datetime.now()
        h = str(tboot.hour)
        m = tboot.minute
        if h == "02" :
#             if m == 15:
            print('Boot journalier en cours')
            time.sleep(35)
            os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)
                                
        s1 = automationhat.input.one.read()
        if s1 == 1 and d1!=1:
            d1 = 1
            t1 = datetime.datetime.now()
            logtext.insert(1.0,'Déclenchement input 1 à '+str(t1)+'\r\n')
            logtext.grid(row=3,column=0)
            for Address in Addr:
                envoi_email(Address[0],Msg1,Sbj1,t1)
            for PhoneNbr in Phone:
                sendSMS(PhoneNbr[0],Sbj1,t1)

        s2 = automationhat.input.two.read()
        if s2 == 1 and d2!=1:
            d2 = 1
            t2 = datetime.datetime.now()
            logtext.insert(1.0,'Déclenchement input 2 à '+str(t2)+'\r\n')
            logtext.grid(row=3,column=0)
            for Address in Addr:
                envoi_email(Address[0],Msg2,Sbj2,t2)
            for PhoneNbr in Phone:
                sendSMS(PhoneNbr[0],Sbj2,t2)

        s3 = automationhat.input.three.read()
        if s3 == 1 and d3 !=1:
            d3 = 1
            t3 = datetime.datetime.now()
            logtext.insert(1.0,'Déclenchement input 3 à '+str(t3)+'\r\n')
            logtext.grid(row=3,column=0)
            for Address in Addr:
                envoi_email(Address[0],Msg3,Sbj3,t3)
            for PhoneNbr in Phone:
                sendSMS(PhoneNbr[0],Sbj3,t3)
                
        if s1 == 1:
            c1+=1
            if c1 > Latency:
                c1 = 0
                d1 = 0
        else:
            c1 = 0
            d1 = 0
            
        if s2 == 1:
            c2+=1
            if c2 > Latency:
                c2 = 0
                d2 = 0
        else:
            c2 = 0
            d2 = 0
            
        if s3 == 1:
            c3+=1
            if c3 > Latency:
                c3 = 0
                d3 = 0
        else:
            c3 = 0
            d3 = 0
        
        if timer == 60 and block == 0:
            
            print('Lecture des messages')
            timer = 0
            read()
        timer+=1
        
        time.sleep(1)

# init dongle

for x in range (8):
    
    global port1
    
    try:
        port = "/dev/ttyUSB"+str(x)
        dongle = serial.Serial(port,115200,timeout = 1, rtscts=True)
        print('Modem détecté en',port)
        port1 = port        
    except serial.serialutil.SerialException:
        pass

# init com GSM

try:
    print('Initialisation du modem...')
    
    dongle.write(('AT+CFUN=0\r').encode('utf-8'))
    time.sleep(10)
    dongle.write(('AT+CFUN=1\r').encode('utf-8'))
    time.sleep(10)
    
    dongle.write(('ATZ\r').encode('utf-8'))
    time.sleep(1)
    
    dongle.write(('AT+CPIN="0000"\r').encode('utf-8'))
    time.sleep(40)
    
    dongle.write(('ATE0\r').encode('utf-8'))
    time.sleep(1)
    
    dongle.close()
    
    print('Initialisation terminée : vérifier la fréquence de la LED Rouge (Allumée pendant 100ms/1s)')
   
except:
    pass

# Messages de démarrage

t = datetime.datetime.now()

for Address in Addr:
            envoi_email(Address[0],"Vérification du démarrage OK","Boot module alarme",t)

for PhoneNbr in Phone:
            sendSMS(PhoneNbr[0],'Boot module alarme',t)

scrut = threading.Thread(target=main)
scrut.start()

root = tkinter.Tk()

t = datetime.datetime.now()
root.title('Berthold_Alarme_v2')
# root.attributes('-fullscreen', True)
bouton3 = tkinter.Button(root,text="Annuaire de contacts",command=liste_annuaire)
bouton3.grid(row=0,column=0)
bouton4 = tkinter.Button(root,text="Paramètres emails",command=liste_para_email)
bouton4.grid(row=1,column=0)
bouton5 = tkinter.Button(root,text="Messages et objets",command=liste_Msg)
bouton5.grid(row=2,column=0)
logtext = tkinter.Text(root,width=300,height=500)
logtext.insert(1.0,str(t)+'\r\n')
logtext.grid(row=4,column=0)

root.mainloop()