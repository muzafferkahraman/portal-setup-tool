'''
Python script to create and delete Nuage SDWAN Portal Resellers,Subscribers and Branches via Portal API
Author: Muzaffer Kahraman (Muzo) 
v 1.0 2023

Example Usage:

python labdeploy.py create reseller --name aaareseller -f reseller.json
python labdeploy.py create subscriber --name aasubscriber1 --parentName aaareseller -f subscriber.json        
python labdeploy.py create subscriber --name aasubscriber2 --parentName csp  -f subscriber.json       
python labdeploy.py create branch --name nsg1 --orgName aasubscriber1 --parentName aaareseller  -f branch.json    
python labdeploy.py create branch --name nsg2 --orgName aasubscriber2 --parentName csp  -f branch.json
python labdeploy.py create rg --name muzo1 --orgName abcsubscriber2 --parentName csp -f .\rg.json -fn .\branch.json
  
python labdeploy.py delete branch --name nsg2 --orgName aasubscriber2 --parentName csp
python labdeploy.py delete branch --name nsg1 --orgName aasubscriber1 --parentName aaareseller 
python labdeploy.py delete subscriber --name aasubscriber1 --parentName aaareseller
python labdeploy.py delete subscriber --name aasubscriber2 --parentName csp        
python labdeploy.py delete reseller --name aaareseller
python labdeploy.py delete rg --name muzo1 --orgName abcsubscriber2 --parentName csp

where parent name always indicate the reseller name/csp
and the orgNAme is the susbscriber name that the nsg belongs to
'''

#!/usr/bin/env python

import argparse
import requests
import logging
import json
import platform

class LabDeploy:

    # Reads the creds.json file and assign the variables accordingly
    def __init__(self):

        f=open('creds.json','r')
        creds=json.load(f)
        self.username=creds["username"]
        self.password=creds["password"]
        self.org=creds["org"]
        self.portal_url=creds["portal_url"]
        self.auth_url=creds["auth_url"]
        self.client_id=creds["client_id"]
        f.close()

    # Requests the token from the Integration Mediator and returns it
    def getToken(self):

        requests.packages.urllib3.disable_warnings()
            
        headers={"accept": "application/json",
        "Content-Type": "application/json" }

        data={
            "username": "{}".format(self.username),
            "password": "{}".format(self.password),
            "organization": "{}".format(self.org)
            }
    
        res=requests.post(self.auth_url, headers=headers,json=data,verify=False).json()
    
        token=res['accessToken']
   
        return token
    
    # Requests the ID of the object matching the name and returns it
    def getID(self,token,type,name,*args):

        if args:
            parentID=args[0]
    
        if type == "reseller":
            url= self.portal_url + "/organizations/1/resellers"
            res=self.sendAPI(url,token,"get") 
                
        if type == "subscriber":
            url= self.portal_url + "/organizations/"+parentID+"/subscribers"
            res=self.sendAPI(url,token,"get")   
      
        if type == "branch":
            url= self.portal_url + "/organizations/"+parentID+"/branches"
            res=self.sendAPI(url,token,"get")   
            
        if type == "rg":
            url= self.portal_url + "/organizations/"+parentID+"/redundancygroups"
            res=self.sendAPI(url,token,"get") 
       
        if str(res) == "<Response [200]>":
            A=res.json()
            for item in A:
                if item.get("name")==name:
                    if type == "branch":
                        id=str(item.get("vsdId"))
                        return(id)
                    if type == "rg" :
                        id=str(item.get("ID"))
                        return(id)
                    else:
                        id=str(item.get("id"))
                        return(id)
                    
    # Sends the specified API Request to the specified endpoint (Portal) with the specified headers and body and returns the result
    def sendAPI(self,url,token,method,*args):
        
        requests.packages.urllib3.disable_warnings()

        headers={"Content-Type": "application/json",
        "Authorization":"Bearer "+token,
        "client_id": self.client_id,
        "x-vns-pagesize":"2000"
        }
    
        if args:
            data=args[0]

        if method == "get":
            res=requests.get(url, headers=headers,verify=False)
    
        if method == "del":
            res=requests.delete(url, headers=headers,verify=False)
    
        if method == "post":
            res=requests.post(url, headers=headers,json=data,verify=False)
    
        return res
    
    # Reads the given json file and assigns it to jsonData variable and returns it
    def jsonGrab(self,file):

        f=open(file,'r')
        jsonData=json.load(f)
        f.close()

        return jsonData
    
    def createReseller(self,token,name,file):

        jsonData=self.jsonGrab(file)

        jsonData["name"]=name
    
        url= self.portal_url + "/organizations/1"

        res=self.sendAPI(url,token,"post",jsonData)
  
        if str(res) == "<Response [200]>":
            message="200 - Reseller {} created sucessfully".format(name)
        else:
            message=str(res) + " Failure in creating the reseller {}".format(name)
    
        logging.info(message)
        print(message)


    def createSubscriber(self,token,name,parentName,file):

        jsonData=self.jsonGrab(file)

        jsonData["name"]=name
   
        if parentName == "csp":
            parentID=1
        else:
            parentID=self.getID(token,"reseller",parentName)
    
        url= self.portal_url + "/organizations/"+str(parentID)

        res=self.sendAPI(url,token,"post",jsonData)
  
        if str(res) == "<Response [200]>":
            message="200 - Subscriber {} created sucessfully under {}".format(name,parentName)
        else:
            message=str(res) + " Failure in creating the subscriber {} under {}".format(name,parentName)
    
        logging.info(message)
        print(message)

    def createBranch(self,token,name,orgName,parentName,file):

        jsonData=self.jsonGrab(file)

        jsonData["name"]=name

        if parentName == "csp":
            parentID=1
        else:
            parentID=self.getID(token,"reseller",parentName)
    
        orgID=self.getID(token,"subscriber",orgName,str(parentID))

        url= self.portal_url + "/organizations/"+orgID+"/branches"

        res=self.sendAPI(url,token,"post",jsonData)
        vsdId=res.json()
        vsdId=res.json()['vsdId']
          
        if str(res) == "<Response [200]>":
            message="200 - Branch {} created sucessfully under {} of the parent {}".format(name,orgName,parentName)
        else:
            message=str(res) + " Failure in creating the branch {} under {} of the parent {}".format(name,orgName,parentName)
    
        logging.info(message)
        print(message)

        return(vsdId)
    
    def createRG(self,token,name,orgName,parentName,nsg1id,nsg2id,file):

        jsonData=self.jsonGrab(file)

        jsonData["name"]=name
        jsonData["gatewayPeer1ID"]=nsg1id
        jsonData["gatewayPeer2ID"]=nsg2id

        if parentName == "csp":
            parentID=1
        else:
            parentID=self.getID(token,"reseller",parentName)
    
        orgID=self.getID(token,"subscriber",orgName,str(parentID))

        url= self.portal_url + "/organizations/"+orgID+"/redundancygroups"

        res=self.sendAPI(url,token,"post",jsonData)

        if str(res) == "<Response [200]>":
            message="200 - RG {} created sucessfully under {} of the parent {}".format(name,orgName,parentName)
        else:
            message=str(res) + " Failure in creating the RG {} under {} of the parent {}".format(name,orgName,parentName)
    
        logging.info(message)
        print(message)

    def deleteReseller(self,token,name):

        id=self.getID(token,"reseller",name)
               
        url= self.portal_url + "/organizations/"+id
        
        res=self.sendAPI(url,token,"del")
  
        if str(res) == "<Response [200]>":
            message="200 - Reseller {} deleted sucessfully".format(name)
        else:
            message=str(res) + " Failure in deleting the reseller {}".format(name)
    
        logging.info(message)
        print(message)

    def deleteSubscriber(self,token,name,parentName):

        if parentName == "csp":
            parentID=1
        else:
            parentID=self.getID(token,"reseller",parentName)
    
        orgID=self.getID(token,"subscriber",name,str(parentID))
        url= self.portal_url + "/organizations/"+orgID
        res=self.sendAPI(url,token,"del")
  
        if str(res) == "<Response [200]>":
            message="200 - Subscriber {} deleted sucessfully under {}".format(name,parentName)
        else:
            message=str(res) + " Failure in deleting the subscirber {} under {}".format(name,parentName)
    
        logging.info(message)
        print(message)

    def deleteBranch(self,token,name,orgName,parentName):
    
        if parentName == "csp":
            parentID=1
        else:
            parentID=self.getID(token,"reseller",parentName)
    
        orgID=self.getID(token,"subscriber",orgName,str(parentID))
        branchID=self.getID(token,"branch",name,orgID)
            
        url=self.portal_url + "/organizations/"+orgID+"/branches/"+str(branchID)
        res=self.sendAPI(url,token,"del")
  
        if str(res) == "<Response [200]>":
            message="200 - Branch {} deleted sucessfully under {} of the parent {}".format(name,orgName,parentName)
        else:
            message=str(res) + " Failure in deleting the branch {} under {} of the parent {}".format(name,orgName,parentName)
    
        logging.info(message)
        print(message)

    def deleteRG(self,token,name,orgName,parentName):

        if parentName == "csp":
            parentID=1
        else:
            parentID=self.getID(token,"reseller",parentName)
    
        orgID=self.getID(token,"subscriber",orgName,str(parentID))
        rgID=self.getID(token,"rg",name,orgID)
    
        url=self.portal_url + "/organizations/"+orgID+"/redundancygroups/"+str(rgID)
        res=self.sendAPI(url,token,"del")
  
        if str(res) == "<Response [200]>":
            message="200 - RG {} deleted sucessfully under {} of the parent {}".format(name,orgName,parentName)
        else:
            message=str(res) + " Failure in deleting the RG {} under {} of the parent {}".format(name,orgName,parentName)
    
        logging.info(message)
        print(message)

    def __del__(self):

        logging.info("labdeploy instance terminated")


if __name__=="__main__":

    # Selects the logfile path suitable for the OS (linux/windows) and sets the log file format
    if platform.system() == "Windows":
        logfile = "c:/tmp/labdeploy.log"
    if platform.system() == "Linux":
        logfile = "/var/log/labdeploy.log"
    logging.basicConfig(filename=logfile,level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s')
    logging.info("labdeploy instance started")

    # Specifies the commandline arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("op", choices=["create","delete"],help="creates the to be selected object")
    subparser = parser.add_subparsers(dest='ob')
    reseller = subparser.add_parser('reseller')
    subscriber = subparser.add_parser('subscriber')
    branch = subparser.add_parser('branch')
    rg = subparser.add_parser('rg')
    
    reseller.add_argument('--name', type=str, required=True,help="name of the reseller to be created")
    reseller.add_argument('-f','--templateFile', type=str, required=False,help="template file to inherit the variables")

    subscriber.add_argument('--name', type=str, required=True,help="name of the subscriber to be created")
    subscriber.add_argument('--parentName', type=str, required=True,help="name of the parent org, enter either reseller name or csp")
    subscriber.add_argument('-f','--templateFile', type=str, required=False,help="template file to inherit the variables")

    branch.add_argument('--name', type=str, required=True,help="name of the branch to be created")
    branch.add_argument('--orgName', type=str, required=True,help="name of the subscriber org of the branch")
    branch.add_argument('--parentName', type=str, required=True,help="parent of the subscriber org (reseller/csp)")
    branch.add_argument('-f','--templateFile', type=str, required=False,help="template file to inherit the variables")

    rg.add_argument('--name', type=str, required=True,help="name of the branch to be created")
    rg.add_argument('--orgName', type=str, required=True,help="name of the subscriber org of the branch")
    rg.add_argument('--parentName', type=str, required=True,help="parent of the subscriber org (reseller/csp)")
    rg.add_argument('-f','--templateFile', type=str, required=False,help="template file to inherit the variables")
    rg.add_argument('-fn','--NSGtemplateFile', type=str, required=False,help="template file to inherit the variables (for NSGs)")
 
    args=parser.parse_args()    

    logging.info("labdeploy {} {} {} command is sent".format(args.op,args.ob,args.name))    

    portal=LabDeploy()
    token=portal.getToken()

    if token:
        logging.info("Token is retrieved sucessfully")

    # Parses the user's commandline arguments and calls the appropriate functions
    if args.op == "create":
        f=open(args.templateFile,'r')
        jsonData=json.load(f)
        jsonData["name"]=args.name
        f.close()

        if args.ob == "reseller":
            portal.createReseller(token,args.name,args.templateFile)
        if args.ob == "subscriber":
            portal.createSubscriber(token,args.name,args.parentName,args.templateFile)
        if args.ob == "branch":
            portal.createBranch(token,args.name,args.orgName,args.parentName,args.templateFile)
        if args.ob == "rg":
            nsgid1=portal.createBranch(token,args.name+"nsg1",args.orgName,args.parentName,args.NSGtemplateFile)
            nsgid2=portal.createBranch(token,args.name+"nsg2",args.orgName,args.parentName,args.NSGtemplateFile)
            portal.createRG(token,args.name,args.orgName,args.parentName,nsgid1,nsgid2,args.templateFile)
                
    if args.op == "delete":
        if args.ob == "reseller":
            portal.deleteReseller(token,args.name)
        if args.ob == "subscriber":
            portal.deleteSubscriber(token,args.name,args.parentName)
        if args.ob == "branch":
            portal.deleteBranch(token,args.name,args.orgName,args.parentName)
        if args.ob == "rg":
            portal.deleteRG(token,args.name,args.orgName,args.parentName)
            portal.deleteBranch(token,args.name+"nsg1",args.orgName,args.parentName)
            portal.deleteBranch(token,args.name+"nsg2",args.orgName,args.parentName)
    


   
