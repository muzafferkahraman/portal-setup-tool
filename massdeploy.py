#!/usr/bin/env python

import labdeploy
import logging
import argparse
import datetime
import platform
import json
from queue import *
from concurrent.futures import ThreadPoolExecutor

Id_lookup={}
Resellers=[]

def createRes(token,instance,resname):
    id=instance.createReseller(token,resname,"reseller.json")
    Resellers.append(resname)
    queue.put(resname+":"+str(id))
    
def createSubs(token,instance,orgname,resname):
    if resname == "csp":
        resID=0
    else:
        resID=str(Id_lookup.get(resname))

    id=instance.createSubscriber(token,orgname,resname,resID,"subscriber.json")
    queue.put(orgname+":"+str(id))

def createNSG(token,instance,nsgname,orgname,resname):
    orgID=str(Id_lookup.get(orgname))
    id=instance.createBranch(token,nsgname,orgname,orgID,resname,"branch.json")
    queue.put(nsgname+":"+id)

def createRG(token,instance,nsg1name,nsg2name,rgname,orgname,resname):
    orgID=str(Id_lookup.get(orgname))
    nsg1id=instance.createBranch(token,nsg1name,orgname,orgID,resname,"branch.json")
    nsg2id=instance.createBranch(token,nsg2name,orgname,orgID,resname,"branch.json")
    rgid=instance.createRG(token,rgname,orgname,orgID,resname,nsg1id,nsg2id,"rg.json")
    queue.put(nsg1name+":"+nsg1id)
    queue.put(nsg2name+":"+nsg2id)
    queue.put(rgname+":"+rgid)

def deleteRG(token,instance,nsg1name,nsg2name,rgname,orgname,resname):
    orgID=str(Id_lookup.get(orgname))
    nsg1ID=str(Id_lookup.get(nsg1name))
    nsg2ID=str(Id_lookup.get(nsg2name))
    rgID=str(Id_lookup.get(rgname))
    instance.deleteRG(token,rgname,rgID,orgname,orgID,resname)
    instance.deleteBranch(token,nsg1name,nsg1ID,orgname,orgID,resname)
    instance.deleteBranch(token,nsg2name,nsg2ID,orgname,orgID,resname)

def deleteNSG(token,instance,nsgname,orgname,resname):
    orgID=str(Id_lookup.get(orgname))
    nsgID=str(Id_lookup.get(nsgname))
    instance.deleteBranch(token,nsgname,nsgID,orgname,orgID,resname)

def deleteSubs(token,instance,orgname,resname):
    orgID=str(Id_lookup.get(orgname))
    instance.deleteSubscriber(token,orgname,orgID,resname)

def deleteRes(token,instance,resname):
    resID=str(Id_lookup.get(resname))
    instance.deleteReseller(token,resname,resID)
  
# Construct the object name,id dictionary from the elements inside the queue and clean the queue afterwards
# This function is called after mass creation of every object type

def updateIdlookup_table():
    for item in list(queue.queue):
        Id_lookup.update({item.split(":")[0]:item.split(":")[1]})
    queue.queue.clear()

if __name__ == "__main__":

    # Selects the logfile path suitable for the OS (linux/windows) and sets the log file format
    if platform.system() == "Windows":
        logfile = "c:/tmp/labdeploy.log"
    if platform.system() == "Linux":
        logfile = "/var/log/labdeploy.log"

    # logging.basicConfig(filename=logfile,level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s')
    # logging.info("mass creation instance started")

    # Specifies the commandline arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("op", choices=["create","delete"],help="creates the to be selected object")
    
    parser.add_argument('-x','--prefix', type=str, required=True,help="name prefix for objects")
    parser.add_argument('-r','--reseller', type=int, required=True,help="number of the resellers to be created")
    parser.add_argument('-s','--subscriber', type=int, required=True,help="number of the subscribers per reseller to be created")
    parser.add_argument('-b','--branch', type=int, required=False,help="number of the branches per subscriber to be created")
    parser.add_argument('-g','--redundantgroup', type=int, required=False,help="number of the redundant groups per subscriber to be created")
    parser.add_argument('-i','--id', type=str, required=False,default=5,help="filename for database of object name and identity pairs")

    args=parser.parse_args()    

    # logging.info("massdeploy {} command is sent".format(args.op))    

    r=args.reseller
    s=args.subscriber
    b=args.branch
    g=args.redundantgroup
    x=args.prefix
   
    massdep_instance=labdeploy.LabDeploy()

    a=datetime.datetime.now()

    token=massdep_instance.getToken()

    # Procedure for creating the objects
    if args.op == "create":
    
        # This queue is for a shared  storage between threads, for object_name,object_id pairs
        queue = Queue()
        
        if r != 0:  # if at least 1 reseller is specified

            # Reseller Creation
            executor=ThreadPoolExecutor(10) 
            for i in range(1,r+1):
                resname=x+"reseller"+str(i)
                executor.submit(createRes,token,massdep_instance,resname)
            executor.shutdown(wait=True)
            updateIdlookup_table()
            
            
            # Subscriber Creation
            executor1=ThreadPoolExecutor(10) 
            for i in range(1,r+1):
                resname=x+"reseller"+str(i)
                for j in range (1,s+1):
                    orgname=resname+"-subscriber"+str(j)
                    executor1.submit(createSubs,token,massdep_instance,orgname,resname)
            executor1.shutdown(wait=True)
            updateIdlookup_table()
           
            # SA NSG Creation
            if b:
                executor2=ThreadPoolExecutor(10) 
                for i in range(1,r+1):
                    resname=x+"reseller"+str(i)
                    for j in range (1,s+1):
                        orgname=resname+"-subscriber"+str(j)
                        for q in range (1,b+1):
                            nsgname=orgname+"-nsg"+str(q)
                            executor2.submit(createNSG,token,massdep_instance,nsgname,orgname,resname)
                executor2.shutdown(wait=True)
            updateIdlookup_table()
        
            # Redundant Group NSG Pair Creation
            if g:
                executor4=ThreadPoolExecutor(5) 
                for i in range(1,r+1):
                    resname=x+"reseller"+str(i)
                    for j in range (1,s+1):
                        orgname=resname+"-subscriber"+str(j)
                        for q in range (1,g+1):
                            nsg1name=orgname+"-rgnsg"+str(q)+"-1"
                            nsg2name=orgname+"-rgnsg"+str(q)+"-2" 
                            rgname=orgname+"-rg"+str(q)
                            executor4.submit(createRG,token,massdep_instance,nsg1name,nsg2name,rgname,orgname,resname)
                executor4.shutdown(wait=True)
                updateIdlookup_table()
            

        else: # if the Subscribers are going to be the members of the csp

            # Subscriber Creation
            executor=ThreadPoolExecutor(10) 
            for j in range (1,s+1):
                orgname=x+"-subscriber"+str(j)
                executor.submit(createSubs,token,massdep_instance,orgname,"csp")
            executor.shutdown(wait=True)
            updateIdlookup_table()
            
             # SA NSG Creation
            if b:
                executor=ThreadPoolExecutor(5) 
                for j in range (1,s+1):
                    orgname=x+"-subscriber"+str(j)
                    for q in range (1,b+1):
                        nsgname=orgname+"-nsg"+str(q)
                        executor.submit(createNSG,token,massdep_instance,nsgname,orgname,"csp")
                executor.shutdown(wait=True)
                updateIdlookup_table()
            
            # Redundant Group NSG Pair Creation
            if g:
                executor4=ThreadPoolExecutor(5) 
                for j in range (1,s+1):
                    orgname=x+"-subscriber"+str(j)
                    for q in range (1,g+1):
                        nsg1name=orgname+"-rgnsg"+str(q)+"-1"
                        nsg2name=orgname+"-rgnsg"+str(q)+"-2" 
                        rgname=orgname+"-rg"+str(q)
                        executor4.submit(createRG,token,massdep_instance,nsg1name,nsg2name,rgname,orgname,"csp")
                executor4.shutdown(wait=True)
                updateIdlookup_table()

        # Save the dictionary of object_name,object_id pairs to the specified json file for the use of deletion procedure
        f=open(args.id,"w")
        json.dump(Id_lookup,f)
        f.close()
        
    # Procedure for deleting the objects
    if args.op == "delete":

        # Open the specified json file and load it to the dictionary
        f=open(args.id,"r")
        Id_lookup=json.load(f)
        f.close()

        if r != 0: # if at least 1 reseller is specified
            
            # NSG Deletion
            if b:
                executor=ThreadPoolExecutor(5) 
                for i in range(1,r+1):
                    resname=x+"reseller"+str(i)    
                    for j in range (1,s+1):
                            orgname=resname+"-subscriber"+str(j)
                            for q in range (1,b+1):
                                nsgname=orgname+"-nsg"+str(q)
                                executor.submit(deleteNSG,token,massdep_instance,nsgname,orgname,resname)
                executor.shutdown(wait=True)

            # Redundant Group NSG Pair Deletion
            if g:
                print("deleting")
                executor4=ThreadPoolExecutor(5) 
                for i in range(1,r+1):
                    resname=x+"reseller"+str(i)
                    for j in range (1,s+1):
                        orgname=resname+"-subscriber"+str(j)
                        for q in range (1,g+1):
                            nsg1name=orgname+"-rgnsg"+str(q)+"-1"
                            nsg2name=orgname+"-rgnsg"+str(q)+"-2" 
                            rgname=orgname+"-rg"+str(q)
                            executor4.submit(deleteRG,token,massdep_instance,nsg1name,nsg2name,rgname,orgname,resname)
                    executor4.shutdown(wait=True)
                
            # Subscriber Deletion
            executor1=ThreadPoolExecutor(20) 
            for i in range(1,r+1):
                resname=x+"reseller"+str(i)    
                for j in range (1,s+1):
                    orgname=resname+"-subscriber"+str(j)
                    executor1.submit(deleteSubs,token,massdep_instance,orgname,resname)
            executor1.shutdown(wait=True)

            # Reseller Deletion
            executor2=ThreadPoolExecutor(10) 
            for i in range(1,r+1):
                resname=x+"reseller"+str(i)
                executor2.submit(deleteRes,token,massdep_instance,resname)
            executor2.shutdown(wait=True) 
             
        else: # if the Subscribers are going to be the members of the csp

            # NSG Deletion
            if b:
                executor3=ThreadPoolExecutor(5) 
                for j in range (1,s+1):
                        orgname=x+"-subscriber"+str(j)
                        for q in range (1,b+1):
                            nsgname=orgname+"-nsg"+str(q)
                            executor3.submit(deleteNSG,token,massdep_instance,nsgname,orgname,"csp")
                executor3.shutdown(wait=True)

            # Redundant Group NSG Pair Deletion
            if g:
                executor4=ThreadPoolExecutor(5) 
                for j in range (1,s+1):
                    orgname=x+"-subscriber"+str(j)
                    for q in range (1,g+1):
                        nsg1name=orgname+"-rgnsg"+str(q)+"-1"
                        nsg2name=orgname+"-rgnsg"+str(q)+"-2" 
                        rgname=orgname+"-rg"+str(q)
                        executor4.submit(deleteRG,token,massdep_instance,nsg1name,nsg2name,rgname,orgname,"csp")
                executor4.shutdown(wait=True)
                
            # Subscriber Deletion
            executor2=ThreadPoolExecutor(10)    
            for j in range (1,s+1):
                orgname=x+"-subscriber"+str(j)
                executor2.submit(deleteSubs,token,massdep_instance,orgname,"csp")
            executor2.shutdown(wait=True)

    b=datetime.datetime.now()
    print("Execution time:",b-a)




