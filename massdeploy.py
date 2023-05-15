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
-p is the number of the simultaneous processes, 5 is reccomended for creation, and 2 for deletion

please set -r as 0 to to specify csp

'''

#!/usr/bin/env python

import labdeploy
import logging
import argparse
import datetime
from multiprocessing import Process
import platform


def createRes(token,nesne,i):
    resname="massreseller"+str(i)
    nesne.createReseller(token,resname,"reseller.json")

def createSubs(token,nesne,resname,j,sundex):
    subsname="masssubscriber"+str(sundex+j)
    nesne.createSubscriber(token,subsname,resname,"subscriber.json")

def createNSG(token,nesne,q,subsname,resname):
    branchname="nsg"+str(q)     
    nesne.createBranch(token,branchname,subsname,resname,"branch.json")

def deleteSubs(token,nesne,j,sundex,resname):
    subsname="masssubscriber"+str(sundex+j)
    nesne.deleteSubscriber(token,subsname,resname)


def deleteRes(token,nesne,i):
    resname="massreseller"+str(i)
    nesne.deleteReseller(token,resname)


if __name__ == "__main__":

    # Select the logfile path (linux/windows) and set the log file format
    if platform.system() == "Windows":
        logfile = "c:/tmp/labdeploy.log"
    if platform.system() == "Linux":
        logfile = "/var/log/labdeploy.log"
    logging.basicConfig(filename=logfile,level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s')
    logging.info("mass creation instance started")

    parser = argparse.ArgumentParser()

    parser.add_argument("op", choices=["create","delete"],help="creates the to be selected object")
    
    parser.add_argument('-r','--reseller', type=int, required=True,help="number of the resellers to be created")
    parser.add_argument('-s','--subscriber', type=int, required=True,help="number of the subscribers per reseller to be created")
    parser.add_argument('-b','--branch', type=int, required=True,help="number of the branches per subscriber to be created")
    parser.add_argument('-p','--simprocess', type=int, required=False,default=5,help="number of the simultaneous processes")

    args=parser.parse_args()    

    # logging.info("labdeploy {} {} {} command is sent".format(args.op,args.ob,args.reselller))    

    r=args.reseller
    s=args.subscriber
    b=args.branch
   
    d=labdeploy.LabDeploy()

    a=datetime.datetime.now()

    token=d.getToken()

    max_simultaneous_process=args.simprocess

    if args.op == "create":
        if r != 0:
            for i in range(1,r+1):
                process = Process(target=createRes,args=(token,d,i,))
                process.start()
                if i % max_simultaneous_process == 0:
                    process.join()   
                process.join()
            process.join()

            sundex=0          
            for i in range(1,r+1):
                resname="massreseller"+str(i)
                for j in range (1,s+1):
                    process = Process(target=createSubs,args=(token,d,resname,j,sundex,))
                    process.start()
                    if j % max_simultaneous_process == 0:
                        process.join()   
                sundex += s
                process.join()
            
            sundex=0
            for i in range(1,r+1):
                resname="massreseller"+str(i)
                for j in range (1,s+1):
                    subsname="masssubscriber"+str(sundex+j)
                    for q in range (1,b+1):
                        process = Process(target=createNSG,args=(token,d,q,subsname,resname,))
                        process.start()
                        if q % max_simultaneous_process == 0:
                            process.join() 
                sundex += s
            process.join()
            

        else:

            for j in range (1,s+1):
                    process = Process(target=createSubs,args=(token,d,"csp",j,0,))
                    process.start()
                    if j % max_simultaneous_process == 0:
                        process.join() 
            process.join()

            for j in range (1,s+1):
                    subsname="masssubscriber"+str(j)
                    for q in range (1,b+1):
                        process = Process(target=createNSG,args=(token,d,q,subsname,"csp",))
                        process.start()
                        if j % max_simultaneous_process == 0:
                            process.join() 
            process.join()

    if args.op == "delete":
        
        if r != 0:
           
            sundex=0   
                
            for i in range(1,r+1):
                resname="massreseller"+str(i)
                
                for j in range (1,s+1):
                    process = Process(target=deleteSubs,args=(token,d,j,sundex,resname,))
                    process.start()
                    if j % max_simultaneous_process == 0:
                        process.join()     
                sundex += s
                process.join()

            for i in range(1,r+1):
                process = Process(target=deleteRes,args=(token,d,i,))
                process.start() 
                if i % max_simultaneous_process == 0:
                    process.join()   
            process.join() 
            
        else:

            for j in range (1,s+1):
                process = Process(target=deleteSubs,args=(token,d,j,0,"csp",))
                process.start()
                if j % max_simultaneous_process == 0:
                    process.join()    
            process.join()
    
    b=datetime.datetime.now()
    print("Execution time:",b-a)

        
    
