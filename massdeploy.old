'''
Python script to create and delete mass number of Nuage SDWAN Portal Resellers,Subscribers and Branches via Portal API
Author: Muzaffer Kahraman (Muzo) 
v 1.0 2023

This script utilizes labdeploy.py's class methods

Example Usage:

python massdeploy.py create -r 2 -s 2 -b 2
python massdeploy.py delete -r 2 -s 2 -b 2

where 

-r is the number of resellers
-s is the number of subscribers per reseller
-b is the number of branches per subscriber

please set -r as 0 to to specify csp

'''

#!/usr/bin/env python

import labdeploy
import logging
import argparse

if __name__ == "__main__":

    # Select the logfile path (linux/windows) and set the log file format
    # logfile = "/var/log/labdeploy.log"
    logfile = "c:/tmp/labdeploy.log"
    logging.basicConfig(filename=logfile,level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s')
    logging.info("mass creation instance started")

    parser = argparse.ArgumentParser()

    parser.add_argument("op", choices=["create","delete"],help="creates the to be selected object")
    
    parser.add_argument('-r','--reseller', type=int, required=True,help="number of the resellers to be created")
    parser.add_argument('-s','--subscriber', type=int, required=True,help="number of the subscribers per reseller to be created")
    parser.add_argument('-b','--branch', type=int, required=True,help="number of the branches per subscriber to be created")

    args=parser.parse_args()    

    # logging.info("labdeploy {} {} {} command is sent".format(args.op,args.ob,args.reselller))    

    r=args.reseller
    s=args.subscriber
    b=args.branch
   
    d=labdeploy.LabDeploy()

    token=d.getToken()

    if args.op == "create":
        if r != 0:
            for i in range(1,r+1):
                resname="massreseller"+str(i)
                d.createReseller(token,resname,"reseller.json")
            sundex=0  
             
            for i in range(1,r+1):
                resname="massreseller"+str(i)
                for j in range (1,s+1):
                    subsname="masssubscriber"+str(sundex+j)
                    d.createSubscriber(token,subsname,resname,"subscriber.json")
                sundex += s
            sundex=0
            for i in range(1,r+1):
                resname="massreseller"+str(i)
                for j in range (1,s+1):
                    subsname="masssubscriber"+str(sundex+j)
                    for q in range (1,b+1):
                        branchname="nsg"+str(q)     
                        d.createBranch(token,branchname,subsname,resname,"branch.json")
                sundex += s
        else:

            for j in range (1,s+1):
                    subsname="masssubscriber"+str(j)
                    d.createSubscriber(token,subsname,"csp","subscriber.json")    
            for j in range (1,s+1):
                    subsname="masssubscriber"+str(j)
                    for q in range (1,b+1):
                        branchname="nsg"+str(q)     
                        d.createBranch(token,branchname,subsname,"csp","branch.json")      

    if args.op == "delete":
        
        if r != 0:
           
            sundex=0
            brindex=0 
            for i in range(1,r+1):
                resname="massreseller"+str(i)
                for j in range (1,s+1):
                    subsname="masssubscriber"+str(sundex+j)
                    for q in range (1,b+1):
                        branchname="nsg"+str(brindex+q)     
                        d.deleteBranch(token,branchname,subsname,resname)
                sundex += b

            sundex=0        
            for i in range(1,r+1):
                resname="massreseller"+str(i)
                for j in range (1,s+1):
                    subsname="masssubscriber"+str(sundex+j)
                    d.deleteSubscriber(token,subsname,resname)
                sundex += s
        
            for i in range(1,r+1):
                resname="massreseller"+str(i)
                d.deleteReseller(token,resname)
        else:
            for j in range (1,s+1):
                subsname="masssubscriber"+str(j)
                for q in range (1,b+1):
                        branchname="nsg"+str(q)     
                        d.deleteBranch(token,branchname,subsname,"csp")
            for j in range (1,s+1):
                    subsname="masssubscriber"+str(j)
                    d.deleteSubscriber(token,subsname,"csp")

        
    