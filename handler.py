import urllib3
import json
import os
http = urllib3.PoolManager()
import textwrap

def lambda_handler(event, context):

    url = os.environ['TEAMS_URL']
    channel = os.environ['TEAMS_CHANNEL']
    
    for record in event['Records']:

        #Message details from SNS event
        message = json.loads(record['Sns']['Message'])
        findings = message['scanning_result'].get('Findings')

        #ARN info to get AWS Account ID
        arn = json.dumps(record['EventSubscriptionArn'])
        account_id = arn.split(":")[4].strip()

        if findings:
        
            malwares = []
            types = []
            for finding in message['scanning_result']['Findings']:
                malwares.append(finding.get('malware'))
                types.append(finding.get('type'))

            account=str(account_id)
            
            malwares=', '.join(malwares)
            
            types=', '.join(types)
            
            file_url=str(message['file_url'])
            
            
            payload = {
                       "summary":"New Salesforce Lead",   
                       "sections":[
                          {
                             "activityTitle":"A <b>Malicous object</b> has been detected!"
                          },
                          {
                             "facts":[
                                {
                                   "name":"Account ID:",
                                   "value":account
                                },
                                {
                                   "name":"File Name:",
                                   "value":malwares
                                },
                                {
                                   "name":"Malware Type:",
                                   "value":types
                                },
                                {
                                   "name":"Location:",
                                   "value":file_url
                                }
                             ]
                          }
                       ],
                       "potentialAction":[
                          {
                             "@context":"http://schema.org",
                             "@type":"ViewAction",
                             "name":"View Object",
                             "target":[
                                file_url
                             ]
                          }
                       ]
                    }
            
            encoded_msg = json.dumps(payload).encode('utf-8')
            resp = http.request('POST',url, body=encoded_msg)
