from pydc27 import *
import re
import json
import urllib
import sqlite3
import os
import time

# Python 2.7
# Salesbot V0.3.1
# A bot which connects to a nmdc hub uses an SQLite database to save a list of items people want to sell
# people can want sell and list an interest in an item

def funForsale(self,msg,user):
    """Lists items currently in the database that are for sale"""
    c = conn.cursor()
    info = "Items currently for sale:\n"
    messages = 0
    for row in c.execute('SELECT * FROM sales ORDER BY ID'):
        
        ID , USER, ITEM, PRICE, INTEREST = row
        if PRICE == "None":
            info += "\n" + "ID:" + str(ID).ljust(4) + " " + str(USER) + ":".ljust(10) + str(ITEM)
        else:
            info += "\n" + "ID:" + str(ID).ljust(4) + " " + str(USER) + ":".ljust(10) + str(ITEM) + " $" + str(PRICE)
         
        if messages < 8:
            messages += 1
        else:
            self.pm(user,info)
            info = "\n"
            messages = 0
    
    info += "\n"        
    self.pm(user,info)             
    conn.commit()    
    return True
    
def funWanted(self,msg,user):
    """Returns a list of items people want"""
    info = "Items people are currently looking to buy:\n"
    messages = 0
    for row in c.execute('SELECT * FROM wanting ORDER BY ID'):
        
        ID , USER, ITEM = row
        info += "ID:" + str(ID).rjust(4) + " " + str(USER) + ":" + str(ITEM) + "\n"   
        
        if messages < 8:
            messages += 1
        else:
            self.pm(user,info)
            info = "\n"
            messages = 0
            
    self.pm(user,info)             
    conn.commit()  
    return True    
    
def funSaleshelp(self,msg,user):
    """Returns a list of valid commands which can be used"""
    #beware the doc string look alike below is just a nromal string
    self.pm(user,"""all available commands are as follows:
    !sell <Item> <Price>: List an item for sale
    !forsale            : Returns a list of items currently for sale
    !want <Item>        : Add an item you are looking for or would like to buy
    !wanted             : Returns a list of items people would like
    !notwanted <ID>     : Remove an item from the wanted list
    !sold <ID>          : Mark an item as sold
    !interested <ID>    : Shows your interest to the seller by adding your name next to the item
    !saleshelp          : Ask for this to be sent to you again
    """) 
    return True  

def funWant(self,msg,user):
    """Adds an item to the list of wanted items (!want <Item>)"""
    Item = " "
    c = conn.cursor()
    wanting = msg.split("!want")[1].strip()
    # Insert a row of data
    Newline = user, wanting
    c.execute("INSERT INTO wanting(USER, ITEM) VALUES (?,?)",Newline)      
    conn.commit() 
    return True        
    
def funNotwanted(self,msg,user):
    """Removes an item from the wanted list (!notwanted <ID>)"""
    c = conn.cursor()
    ID = msg.split("!notwanted")[1].strip()
    #delete Row of Data
    c.execute("Delete FROM wanting WHERE ID = ?",(ID,))                  
    conn.commit()  
    return True 
    
    
    
def funSell(self,msg,user):
    """Adds an item to the database of items for sale (!sell <Item> <Price>)"""
    Item = " "
    Price = " "
    c = conn.cursor()
    ssellingwant = msg.split("!sell")[1].strip()
    
    if "&#36;" not in msg.lower():
        Price = "None"
        Item = ssellingwant
    else:
        Item,Price = ssellingwant.rsplit("&#36;",1)
    interest = "[]"
    # Insert a row of data
    Newline = user, Item, Price, interest
    c.execute("INSERT INTO sales(USER, ITEM, PRICE, INTEREST) VALUES (?,?,?,?)",Newline)      
    conn.commit()    
    return True

    
    
def funSold(self,msg,user):
    """removes an item for sale from the database (!Sold <ID>)"""
    c = conn.cursor()
    ID = msg.split("!sold")[1].strip()
    #delete Row of Data
    c.execute("Delete FROM sales WHERE ID = ?",(ID,))                  
    conn.commit()    
    return True

def funInterested(self,msg,user):
    """Lists that a user is interested in an item being sold and adds their name
    to a list which only the seller can see"""
    ID = msg.split("!interested")[1].strip()
    c = conn.cursor()
    interestList = c.execute('SELECT INTEREST FROM sales WHERE ID = ?',(ID,))
    interestList.append(user)
    c.execute("INSERT INTO sales(INTEREST) WHERE ID = ? VALUES (?)",(ID,interestList))      
    conn.commit() 
    return True

 
class SalesBot(PyDC):

    #Setup PyDC Globals

    #address='global.canthub.info'
    address='127.0.0.1'
    port=411
    debug=False
    auto_reconnect = True
    nick = 'SalesBot'
    desc='!saleshelp for more information, I am your Sales Bot V0.3.1'
    #password='123321'
    
    class Sales_Responce(object):
        def __init__(self):
            self.cmd = ""
            self.msg_respond = True     #Will respond to public message
            self.msg_reply = ""
            self.pmsg_reply = ""

        def cmd_action(self):
            return False #must return true for reply or false for no reply

        def reply(self,parent,pm,user):
            if pm:
                parent.pm(user, self.pmsg_reply)
            else:
                if self.msg_respond:
                    parent.say(self.msg_reply)
            print "Replied to", user
            return

    def __init__(self):

        self.COMMANDS = {}

        def add_cmd(name):
            self.COMMANDS[name.cmd] = name
    
        sold = self.Sales_Responce()
        sold.cmd = "!sold"
        sold.msg_respond = True     
        sold.msg_reply = "That item has now been removed from the List"
        sold.pmsg_reply = "That item has now been removed from the List"
        sold.cmd_action = funSold
        add_cmd(sold)

        notwanted = self.Sales_Responce()
        notwanted.cmd = "!notwanted"
        notwanted.msg_respond = True   
        notwanted.msg_reply = "That item has now been removed from the List"
        notwanted.pmsg_reply = "That item has now been removed from the List"
        notwanted.cmd_action = funNotwanted
        add_cmd(notwanted)

        wanted = self.Sales_Responce()
        wanted.cmd = "!wanted"
        wanted.msg_respond = False     
        wanted.msg_reply = "A list has been sent to you via PM"
        wanted.pmsg_reply = "If you have something someone wants add it :)"
        wanted.cmd_action = funWanted
        add_cmd(wanted)

        want = self.Sales_Responce()
        want.cmd = "!want"
        want.msg_respond = True     
        want.msg_reply = "Your request has been added to the list"
        want.pmsg_reply = "Your request has been added to the list"
        want.cmd_action = funWant
        add_cmd(want)

        saleshelp = self.Sales_Responce()
        saleshelp.cmd = "!saleshelp"
        saleshelp.msg_respond = False     
        saleshelp.msg_reply = "I sent you help via PM"
        saleshelp.pmsg_reply = "If you are still stuck PM Gafail for help"
        saleshelp.cmd_action = funSaleshelp
        add_cmd(saleshelp)

        sell = self.Sales_Responce()
        sell.cmd = "!sell"
        sell.msg_respond = True     
        sell.msg_reply = "Thank you for adding another item to sell"
        sell.pmsg_reply = "Thank you for adding another item to sell"
        sell.cmd_action = funSell
        add_cmd(sell)

        forsale = self.Sales_Responce()
        forsale.cmd = "!forsale"
        forsale.msg_respond = False     
        forsale.msg_reply = "A list has been sent to you via PM"
        forsale.pmsg_reply = "If you wish to buy something PM the user and list your interest with !interested <ID>"
        forsale.cmd_action = funForsale
        add_cmd(forsale)
   

    def messageReply(self, user, msg, pm):
        """ if the message needs to be replied to then here is where the
        messages are. If pm = true then private message else public message"""
        #print msg
        cmd = msg.split(' ')[0]
        if cmd in self.COMMANDS.keys():
            if self.COMMANDS[cmd].cmd_action(self,msg,user):
                self.COMMANDS[cmd].reply(self,pm,user)
    
        output = ''
        respond = False
        
        #should be user-op commands here probably
        if user != "SalesBot" and not pm:
            if 'SalesBot' in msg:
                if 'who made you' in msg.lower():
                    output = ("Gafail started making me on the 30/10/2014")        
                    respond = True  
                    
                elif 'help' in msg.lower():
                    saleshelp(self,user)
                    respond = False  

                elif 'night' in msg.lower():
                    output = ("Good night")        
                    respond = True                
    
                else:
                    output = ("hello")        
                    respond = False
                    
            elif 'anyone' in msg.lower():
                if 'sell' in msg.lower():
                    output = ("Please type !forsale to see what is being sold on CantHub or add a buy request with !want <your item here>")        
                    respond = True                
                elif 'buy' in msg.lower():
                    output = ("Trying to sell something? Why not list it on SalesBot with !sell 'your item here'")        
                    respond = True  
                    
            elif 'anybody ' in msg.lower():
                if 'sell' in msg.lower():
                    output = ("Please type !forsale to see what is being sold on CantHub or add a buy request with !want <your item here>")        
                    respond = True                
                elif 'buy' in msg.lower():
                    output = ("Trying to sell something? Why not list it on SalesBot with !sell <your item here>")        
                    respond = True             
            else:
                respond = False 
        else:
            respond = False   
        
        if respond:
            self.say(output)        
             
    
    
    
    def onPrivate(self, user, msg):
        self.messageReply(user, msg, True) #replys to a private message
              
    def onPublic(self, user, msg):
        self.messageReply(user, msg, False) #responds to a public message       

##############################################
#      Start the bot...
##############################################
bot=SalesBot()
if not os.path.isfile('HubSales.db'):
    conn = sqlite3.connect('HubSales.db')
    c = conn.cursor()
    # Create table
    c.execute('''CREATE TABLE sales (ID INTEGER PRIMARY KEY AUTOINCREMENT , USER, ITEM, PRICE, INTEREST)''')
    
    c.execute('''CREATE TABLE wanting (ID INTEGER PRIMARY KEY AUTOINCREMENT , USER, ITEM)''')
else:
    conn = sqlite3.connect('HubSales.db')
    c = conn.cursor()    

print('Connecting to dc hub ' + bot.address + ' using port '+str(bot.port))
bot.connect()
