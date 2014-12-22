from pydc import *
import re
import json
import urllib
import sqlite3
import time
import os

# Python 3.4
# A bot which connects to a nmdc hub uses an SQLite database to save a list of items people want to sell
# people can want sell and list an interest in an item

def funForsale(self,msg,user):
    """Lists items currently in the database that are for sale"""
    c = conn.cursor()
    info = "Items currently for sale:\n"
    messages = 0
    for row in c.execute('SELECT * FROM sales ORDER BY ID'):
        
        ID , USER, ITEM, PRICE = row
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
    
def funSaleshelp(self,msg,user):
    """Returns a list of valid commands which can be used"""
    self.pm(user,"""all available commands are as follows:
    !wanted: Returns a list of items people would like
    !want: Add an item you are looking for or would like to buy
    !notwanted: Remove an item from the wanted list
    !sell: List an item for sale
    !forsale: Returns a list of items currently for sale
    !sold: Mark an item as sold
    !saleshelp: Ask for this to be sent to you again
    """)   

def funWant(self,msg,user):
    """Adds an item to the list of wanted items"""
    Item = " "
    c = conn.cursor()
    _,wanting = msg.split("!want")
    # Insert a row of data
    Newline = user, wanting
    c.execute("INSERT INTO wanting(USER, ITEM) VALUES (?,?)",Newline)      
    conn.commit()         
    
def funNotwanted(self,msg,user):
    """Removes an item from the wanted list"""
    c = conn.cursor()
    _,IDsold = msg.split("!notwanted ")
    #delete Row of Data
    c.execute("Delete FROM wanting WHERE ID = ?",(IDsold,))                  
    conn.commit()   
    
    
    
def funSell(self,msg,user):
    """Adds an item to the database of items for sale"""
    Item = " "
    Price = " "
    c = conn.cursor()
    _,ssellingwant = msg.split("!sell")
    
    if "&#36;" not in msg.lower():
        Price = "None"
        Item = ssellingwant
    else:
        Item,Price = ssellingwant.rsplit("&#36;",1)
    # Insert a row of data
    Newline = user, Item, Price
    c.execute("INSERT INTO sales(USER, ITEM, PRICE) VALUES (?,?,?)",Newline)      
    conn.commit()    

    
    
def funSold(self,msg,user):
    """removes an item for sale from the database"""
    c = conn.cursor()
    _,IDsold = msg.split("!sold ")
    #delete Row of Data
    c.execute("Delete FROM sales WHERE ID = ?",(IDsold,))                  
    conn.commit()    


class SalesBot(PyDC):
    
    #address='global.canthub.info'
    address='127.0.0.1'
    port=411
    debug=True
    auto_reconnect = True
    nick = 'SalesBot'
    desc='!saleshelp for more information, I am your Sales Bot V0.2.1'
    #password='123321'
    

    #list commands here
    #please note that order matters! this is an index lookup
    COMMANDS = ('!sold', 
                '!notwanted',
                '!wanted',
                '!want',
                '!saleshelp',
                '!sell',
                '!forsale')
    
    #list the public response messages here (index lookup)
    RESPONCE_MESSAGES = ("That item has now been removed from the List",
                         "That item has now been removed from the List",
                         "A list has been sent to you via PM",
                         "Your request has been added to the list",
                         "I sent you help via PM",
                         "Thank you for adding another item to sell",
                         "A list has been sent to you via PM"
                         )
    
    msgsold, \
    msgnotwanted, \
    msgwanted, \
    msgwant, \
    msgsaleshelp, \
    msgsell, \
    msgforsale =  RESPONCE_MESSAGES 
    
    #list items here that you do not want to be posted to public chat
    NO_RESPONCE = (msgforsale,msgwanted,msgsaleshelp)
    
    #list the private response messages here
    PM_RESPONCE_MESSAGES = ("That item has now been removed from the List",
                            "That item has now been removed from the List",
                            "If you have something someone wants add it :)",
                            "Your request has been added to the list",
                            "If you are still stuck PM Gafail for help",
                            "Thank you for adding another item to sell",
                            "If you wish to buy something PM the user and list your interest with !interested <ID>"
                            )
    pmsgsold, \
    pmsgnotwanted, \
    pmsgwanted, \
    pmsgwant, \
    pmsgsaleshelp, \
    pmsgsell, \
    pmsgforsale =  PM_RESPONCE_MESSAGES     
    
    #list command shortcuts here
    #a command shortcut converts shortname into raw command as string
    sold, \
    notwanted, \
    wanted, \
    want, \
    saleshelp, \
    sell, \
    forsale = COMMANDS
                                                    
                                                         
    #set cammands to funtions lookup here
    # options[command](<variables here>) -> Funtion for command
    options = {sold      : funSold,
               notwanted : funNotwanted,
               wanted    : funWanted,
               want      : funWant,
               saleshelp : funSaleshelp,
               sell      : funSell,
               forsale   : funForsale                
               }   
    
    # private message reply lookup here
    # pm_reply[command] -> private message response
    pm_reply = {sold      : pmsgsold,
                notwanted : pmsgnotwanted,
                wanted    : pmsgwanted,
                want      : pmsgwant,
                saleshelp : pmsgsaleshelp,
                sell      : pmsgsell,
                forsale   : pmsgforsale                
                }
    
    #set public reply message lookup here
    # reply[command] -> public message response
    reply = {sold      : msgsold,
             notwanted : msgnotwanted,
             wanted    : msgwanted,
             want      : msgwant,
             saleshelp : msgsaleshelp,
             sell      : msgsell,
             forsale   : msgforsale                
             }       

    def messageReply(self, user, msg, pm):
        """ if the message needs to be replied to then here is where the
        messages are. If pm = true then private message else public message"""
        
        cmd = msg.split(' ')[0]
        if cmd in self.COMMANDS:
            self.options[cmd](self,msg,user)
            if pm:
                self.pm(user, self.pm_reply[cmd])
            else:
                if self.reply[cmd] not in self.NO_RESPONCE:
                    self.say(self.reply[cmd])
    
    
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
                    output = ("Please Type !forsale to see what is being sold on CantHub or ad a buy request with !want 'your item here'")        
                    respond = True                
                elif 'buy' in msg.lower():
                    output = ("Trying to sell something? Why not list it on SalesBot with !sell 'your item here'")        
                    respond = True  
                    
            elif 'anybody ' in msg.lower():
                if 'sell' in msg.lower():
                    output = ("Please Type !forsale to see what is being sold on CantHub or ad a buy request with !want <your item here>")        
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
    c.execute('''CREATE TABLE sales (ID INTEGER PRIMARY KEY, USER, ITEM, PRICE)''')
    
    c.execute('''CREATE TABLE wanting (ID INTEGER PRIMARY KEY, USER, ITEM)''')
else:
    conn = sqlite3.connect('HubSales.db')
    c = conn.cursor()    

print('Connecting to dc hub ' + bot.address + ' using port '+str(bot.port))
bot.connect()
