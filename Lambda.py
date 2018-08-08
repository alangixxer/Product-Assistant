""" 
classes are upper camel
functions are lower camel
variables are lower case

Copyright (C) 2018: Edward Acosta and Alan Newcomer

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>
"""

import time
import json
import boto3
import botocore.vendored.requests.packages.urllib3 as urllib3
from urllib.parse import unquote

class ProductAssistant:
    """Initilize function to set boto3 clients and self variables."""
    def __init__(self, event, context):
        #setting text variables to False
        self.text_1 = False
        self.text_2 = False
        self.text_3 = False
        #rekognition and dynamodb client setup
        rek = boto3.client('rekognition')
        self.dynamodb = boto3.client('dynamodb')
        #converting event to json type
        self.message = json.loads(unquote(str(event)).replace("'","\""))
        print(self.message)
        self.number = self.message['From']
        #dynamodb tables
        self.product_table = "PA_Products"
        self.customer_table = "PA_Customers"
        #grabbing current state of text conversation
        found_product, textCount = self.getCurrentState()
        
        #if a new image comes in and it is the first message
        if 'MediaUrl0' in self.message.keys() and textCount == '0':
            s3_bucket, s3_key =self.uploadS3()
            rek_response = rek.detect_text(Image={
                'S3Object':{
                    'Bucket':s3_bucket,
                    'Name':s3_key
                }
            })
            self.word_list = self.getWords(rek_response)
            for each in self.word_list:
                getProduct = self.dynamodb.get_item(TableName=self.product_table, Key={
                    'product_id':{
                        'S':each.lower()
                    }
                }, ConsistentRead=True)
                if 'Item' in getProduct:
                    theProduct = getProduct['Item']['product_id']['S']
                    self.updateRow(self.number, 'textCount', 'N', str(int(textCount) + 1))
                    self.updateRow(self.number, 'product', 'S', theProduct)
                    productOptions = self.getDBList(each.lower())
                    self.text_1 = '<?xml version=\"1.0\" encoding=\"UTF-8\"?>'\
                        '<Response><Message>{0} {1} {2} .</Message></Response>'\
                        .format(theProduct, "was detected.\nWhould you like to see", productOptions)
                else:
                    print("did not find image")
        elif self.message['Body'] != '' and textCount == '1':
            getLink = self.dynamodb.get_item(TableName=self.product_table, Key={
                'product_id':{
                    'S':found_product.lower()
                }
            }, ConsistentRead=True)
            print(getLink)
            theLink = getLink['Item'][self.message['Body']]['S']
            self.updateRow(self.number, 'textCount', 'N', str(int(textCount) + 1))
            self.text_2 = '<?xml version=\"1.0\" encoding=\"UTF-8\"?>'\
                '<Response><Message>{0}</Message></Response>'.format(theLink)
        elif textCount == '2':
            self.text_3 = '<?xml version=\"1.0\" encoding=\"UTF-8\"?>'\
                '<Response><Message>{0}</Message></Response>'\
                .format("Send an image of a product so I can help you.")
        else:
            self.text_3 = '<?xml version=\"1.0\" encoding=\"UTF-8\"?>'\
                '<Response><Message>{0}</Message></Response>'\
                .format("Please re-send the text. No product found.")
    
    """Responds with the desired text message"""
    def textResponse(self):
        if self.text_1:
            return self.text_1
        elif self.text_2:
            return self.text_2
        elif self.text_3:
            return self.text_3

    """Creates a string list from the dynamodb options list"""
    def getDBList(self, product):
        getRow = self.dynamodb.get_item(TableName=self.product_table, Key={
            'product_id':{
                'S':product
            }
        }, ConsistentRead=True)
        getList = getRow['Item']['options']['L']
        for i in range(len(getList)):
            if i == 0:
                cleanList = '"' + getList[i]['S'] + '"'
            elif i < len(getList) -1:
                cleanList = cleanList + ", " + '"' + getList[i]['S'] + '"'
            else:
                cleanList = cleanList + " or " + '"' + getList[i]['S'] + '"'
        
        return cleanList
            
    """updates a row in dynamodb by getting and then putting"""     
    def updateRow(self, fromNum, key, kType, newValue):
        getJson = self.dynamodb.get_item(TableName=self.customer_table, Key={
            'from_number':{
                'S':fromNum
            }
        }, ConsistentRead=True)
        getJson['Item'][key][kType] = newValue
        self.dynamodb.put_item(TableName=self.customer_table, Item=getJson['Item'])
        return "Count Added"
    
    """Puts the words found by rekognition and appends to a list"""
    def getWords(self, response):   
        words = []
        textDetections=response['TextDetections']
        #print(response)
        print('Matching faces')
        for text in textDetections:
            print('Id: {}'.format(text['Id']))
            print('Detected text:' + text['DetectedText'])
            words.append(text['DetectedText'])
            print('Confidence: ' + "{:.2f}".format(text['Confidence']) + "%")
            print('')
            if 'ParentId' in text:
                print('Parent Id: {}'.format(text['ParentId']))
            print('Type:' + text['Type'])
            
        return words
    
    """uploads images to s3"""
    def uploadS3(self):
        s3 = boto3.client('s3')
        url = self.message['MediaUrl0']
        http = urllib3.PoolManager()
        bucket = 'sns-pictures' #your s3 bucket
        key = '{0}-{1}/{2}.jpg'.format(self.message['To'].replace('+',''),self.number.replace('+',''),url.split('/')[-1]) #your desired s3 path or filename
        s3_response = s3.upload_fileobj(http.request('GET', url,preload_content=False), bucket, key)
        return bucket, key
    
    """Inserts new row into dynamodb table"""
    def createRow(self, table_name, cell_number):
        response = self.dynamodb.put_item(TableName=table_name, Item={
            'from_number':{
                'S':cell_number
            },
            'textCount':{
                'N':'0'
            },
            'product':{
                'S':'none'
            },
            'timeStamp':{
                'N':str(time.time())
            }
        })
        count = '0'
        product = "none"
        return response, count, product

    """Gets information from dynamodb table to find current message state"""
    def getCurrentState(self):
        row_json = self.dynamodb.get_item(TableName=self.customer_table, Key={
            'from_number':{
                'S':self.number
            }
        }, ConsistentRead=True)
        #if a new image is sent then new information will be sent to dynamodb
        if 'MediaUrl0' in self.message.keys():
            _,count, product = self.createRow(self.customer_table, self.number)
        elif 'Item' not in row_json:
            #creating row if 'From' doesnt exist
            _,count, product = self.createRow(self.customer_table, self.number)
        elif float(row_json['Item']['timeStamp']['N']) < time.time() - 300:
            #creating new row in time is longer than five minutes
            _,count, product = self.createRow(self.customer_table, self.number)
        else:
            print(row_json)
            count = row_json['Item']['textCount']['N']
            product = row_json['Item']['product']['S']
            
        return product, count
        

def lambda_handler(event, context):
    print(event)
    twr = ProductAssistant(event, context)
    print(twr.textResponse())
    return twr.textResponse()


