import datetime
import re
import logging
import string
import dateutil.parser

class Analyzer():
    """analyze the sms backup and return credit/debit card expenses"""
    #regular expression to match expenses made by creadit/debit card with 'spent' token
    rgxSpent = r'(spent|card|ending(?=[0-9]+)|(?<=xxxxx)[0-9]+)'
    #regular expression to match expenses made by creadit/debit card with 'used' token
    rgxUsed = r'(used|card|ending(?=[0-9]+)|(?<=xxxxx)[0-9]+)'
    #regular expression to match expenses made by creadit/debit card with 'payment' token
    rgxPayment = r'(received|payment|card|ending(?=[0-9]+)|(?<=xxxxx)[0-9]+)'
    #regular exp to check if number token contains str 
    rgxSender = r'(^\W[0-9]*$|(?<=\s)[0-9]*|^[0-9]*$)'
    #regular exp to extract date time
    rgxDateTime = r'\d{4}[-./:]\d{2}[-./:]\d{2}[:]\d{2}[:]\d{2}'
     # rgx to match 03/05/16 03-apr-16 etc
    rgxDateOnly1 = r'(\d{4}|\d{2})[-/.](\d{1}|\d{2}|[a-z]{3})[-/.](\d{4}|\d{2})'
    # rgx to match 03\/05\/16 03\/apr\/16
    rgxDateOnly2 = r'(\d{4}|\d{2})\W\W(\d{1}|\d{2}|[a-z]{3})\W\W(\d{4}|\d{2})'
    #regular exp for card details
    rgxCard = r'((?<=ending\swith\s)[0-9]+|(?<=ending\s)[0-9]+|(?<=xxxxx)[0-9]+)'
    #rgx for transaction amount
    rgxAmount = r'(rs[.\s][0-9]*.[0-9]*(?=\swas\sspent)|(?<=used\sfor\s)inr[.\s][0-9]*.[0-9]*|(?<=payment\sof\s)rs[.\s][0-9]*.[0-9]*)'

    def __init__(self,backupMessages):
        # create iterator using generator
        self.smsGenerator = (message for message in backupMessages['messages'])
        self.expenses = []
    
    def find(self):
        for message in self.smsGenerator:
            #check if sender is person or bank/service provider
            sender = re.findall(Analyzer.rgxSender,str(message['number']))
            if len(sender)==0:
                # checking for tokens 'spent , card' 
                spentStatement = re.findall(Analyzer.rgxSpent,message['text'].lower())
                if set(['spent','card']).issubset(set(spentStatement)):
                    self.expenses.append({
                        'amount':self.getTransactionAmount(message['text']),
                        'sender':message['number'],
                        'card':self.getCardNumber(message['text']),
                        'recivedOn':self.getSmsRecivedDate(message['timestamp']),
                        'timestamp':message['timestamp'],
                        'transaction':self.getTransactionDate(message['text'])
                    })

                # checking for tokens 'used, card' 
                usedStatement = re.findall(Analyzer.rgxUsed,message['text'].lower())
                if set(['used','card']).issubset(set(usedStatement)):
                    self.expenses.append({
                        'amount':self.getTransactionAmount(message['text']),
                        'sender':message['number'],
                        'card':self.getCardNumber(message['text']),
                        'recivedOn':self.getSmsRecivedDate(message['timestamp']),
                        'timestamp':message['timestamp'],
                        'transaction':self.getTransactionDate(message['text'])
                    })
                
                # checking for tokens 'payment, card,received' 
                paymentStatement = re.findall(Analyzer.rgxPayment,message['text'].lower())
                if set(['payment','received','card']).issubset(set(paymentStatement)):
                    self.expenses.append({
                        'amount':self.getTransactionAmount(message['text']),
                        'sender':message['number'],
                        'card':self.getCardNumber(message['text']),
                        'transaction':self.getTransactionDate(message['text']),
                        'recivedOn':self.getSmsRecivedDate(message['timestamp']),
                        'timestamp':message['timestamp']
                    })
        
        #return final results
        return self.expenses


    def getTransactionDate(self,message):
        """get raw text message , use rgx exp to match date formate and retun the date time"""
        
        #matches date time example (2016-04-11:10:14:29) formate
        date = re.findall(Analyzer.rgxDateTime,message.lower())
        if len(date)>0: 
            date = datetime.datetime.strptime(date[0], "%Y-%m-%d:%H:%M")
            return date.strftime('%Y-%b-%d %H:%M %p')

        #matches date time example(01-03-16,01/03/16,01-apr-16,01-apr-2016,01/apr/2016,01-3-16,01/3/16)formate
        dateArry = re.findall(Analyzer.rgxDateOnly1,message.lower())
        if len(dateArry)>0: 
            date = dateArry[0]
            #check if Month as locale’s abbreviated name.
            #or Month as a decimal number.
            if len(date[1])<3:
                dateStr = "%d-%d-%d"%(int(date[0]),int(date[1]),int(date[2]))
            else:
                dateStr = "%d-%s-%d"%(int(date[0]),date[1],int(date[2]))
            date = dateutil.parser.parse(dateStr)
            return date.strftime('%Y-%b-%d %H:%M %p')
            
         #matches date time example(01\/03\/16,01\/03\/16,01\/apr\/2016,01\/3\/16)formate
        dateArry = re.findall(Analyzer.rgxDateOnly2,message.lower())
        if len(dateArry)>0: 
            date = dateArry[0]
            #check if Month as locale’s abbreviated name.
            #or Month as a decimal number.
            if len(date[1])<3:
                dateStr = "%d-%d-%d"%(int(date[0]),int(date[1]),int(date[2]))
            else:
                dateStr = "%d-%s-%d"%(int(date[0]),date[1],int(date[2]))
            date = dateutil.parser.parse(dateStr)
            return date.strftime('%Y-%b-%d %H:%M %p')


    def getCardNumber(self,message):
        """get raw text message , use rgx exp to match card formate and retun the creadit card details"""
        card = re.findall(Analyzer.rgxCard,message.lower())
        return card[0]

    def getTransactionAmount(self,message):
        """get raw text message , use rgx exp to match amount formate and retun the transaction amount involved in (spent/recived/payment)"""
        amount = re.findall(Analyzer.rgxAmount,message.lower())
        return amount[0].capitalize() 
        

    def getSmsRecivedDate(self,timestamp):
        """return sms recived time """
        #convert millisec to sec
        timestamp = timestamp/1000
        date = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%b-%d %H:%M %p')
        return date
    
