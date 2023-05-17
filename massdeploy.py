'''
Python script to create and delete mass number of Nuage SDWAN Portal Resellers,Subscribers and Branches via Portal API
Author: Muzaffer Kahraman (Muzo) 
v 1.0 2023

This script utilizes labdeploy.py's class methods

Example Usage:

python massdeploy.py create -r 2 -s 2 -b 2 -g 2 -p 5
python massdeploy.py delete -r 2 -s 2 -p 2

where 

-r is the number of resellers
-s is the number of subscribers per reseller
-b is the number of branches per subscriber
-g is the number of redundant groups per subscriber
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

def createRG(token,nesne,q,subsname,resname):
    nsg1name="rgnsg"+str(q)+"-1"
    nsg2name="rgnsg"+str(q)+"-2" 
    rgname="rg"+str(q)
    nsg1id=nesne.createBranch(token,nsg1name,subsname,resname,"branch.json")
    nsg2id=nesne.createBranch(token,nsg2name,subsname,resname,"branch.json")
    nesne.createRG(token,rgname,subsname,resname,nsg1id,nsg2id,"rg.json")
    
def deleteSubs(token,nesne,j,sundex,resname):
    subsname="masssubscriber"+str(sundex+j)
    nesne.deleteSubscriber(token,subsname,resname)

def deleteRes(token,nesne,i):
    resname="massreseller"+str(i)
    nesne.deleteReseller(token,resname)


if __name__ == "__main__":

    # Selects the logfile path suitable for the OS (linux/windows) and sets the log file format
    if platform.system() == "Windows":
        logfile = "c:/tmp/labdeploy.log"
    if platform.system() == "Linux":
        logfile = "/var/log/labdeploy.log"
    logging.basicConfig(filename=logfile,level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s')
    logging.info("mass creation instance started")

    # Specifies the commandline arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("op", choices=["create","delete"],help="creates the to be selected object")
    
    parser.add_argument('-r','--reseller', type=int, required=True,help="number of the resellers to be created")
    parser.add_argument('-s','--subscriber', type=int, required=True,help="number of the subscribers per reseller to be created")
    parser.add_argument('-b','--branch', type=int, required=False,help="number of the branches per subscriber to be created")
    parser.add_argument('-g','--redundantgroup', type=int, required=False,help="number of the redundant groups per subscriber to be created")
    parser.add_argument('-p','--simprocess', type=int, required=False,default=5,help="number of the simultaneous processes")

    args=parser.parse_args()    

    logging.info("massdeploy {} command is sent".format(args.op))    

    r=args.reseller
    s=args.subscriber
    b=args.branch
    g=args.redundantgroup
   
    massdep_instance=labdeploy.LabDeploy()

    a=datetime.datetime.now()

    token=massdep_instance.getToken()

    max_simultaneous_process=args.simprocess

    if args.op == "create":

        if r != 0:  # if at least 1 reseller is in place

            for i in range(1,r+1):
                process = Process(target=createRes,args=(token,massdep_instance,i,))
                process.start()
                if i % max_simultaneous_process == 0:
                    process.join()   
                process.join()
            process.join()

            sundex=0          
            for i in range(1,r+1):
                resname="massreseller"+str(i)
                for j in range (1,s+1):
                    process = Process(target=createSubs,args=(token,massdep_instance,resname,j,sundex,))
                    process.start()
                    if j % max_simultaneous_process == 0:
                        process.join()   
                sundex += s
                process.join()
            
            if b:
                sundex=0
                for i in range(1,r+1):
                    resname="massreseller"+str(i)
                    for j in range (1,s+1):
                        subsname="masssubscriber"+str(sundex+j)
                        for q in range (1,b+1):
                            process = Process(target=createNSG,args=(token,massdep_instance,q,subsname,resname,))
                            process.start()
                            if q % max_simultaneous_process == 0:
                                process.join() 
                    sundex += s

                sundex=0

            if g:
                sundex=0
                for i in range(1,r+1):
                    resname="massreseller"+str(i)
                    for j in range (1,s+1):
                        subsname="masssubscriber"+str(sundex+j)
                        for q in range (1,g+1):
                            process = Process(target=createRG,args=(token,massdep_instance,q,subsname,resname,))
                            process.start()
                            if q % max_simultaneous_process == 0:
                                process.join() 
                    sundex += s

            process.join()
            

        else: # if the subscribers are going to be the members of the csp

            for j in range (1,s+1):
                process = Process(target=createSubs,args=(token,massdep_instance,"csp",j,0,))
                process.start()
                if j % max_simultaneous_process == 0:
                    process.join() 
            process.join()
            
            if b:
                for j in range (1,s+1):
                    subsname="masssubscriber"+str(j)
                    for q in range (1,b+1):
                        process = Process(target=createNSG,args=(token,massdep_instance,q,subsname,"csp",))
                        process.start()
                        if j % max_simultaneous_process == 0:
                            process.join() 
            if g:
                for j in range (1,s+1):
                        subsname="masssubscriber"+str(j)
                        for q in range (1,g+1):
                            process = Process(target=createRG,args=(token,massdep_instance,q,subsname,"csp",))
                            process.start()
                            if q % max_simultaneous_process == 0:
                                process.join() 

            process.join()

    if args.op == "delete":

        if r != 0: # if at least 1 reseller is in place
           
            sundex=0   
                
            for i in range(1,r+1):
                resname="massreseller"+str(i)
                
                for j in range (1,s+1):
                    process = Process(target=deleteSubs,args=(token,massdep_instance,j,sundex,resname,))
                    process.start()
                    if j % max_simultaneous_process == 0:
                        process.join()     
                sundex += s
                process.join()

            for i in range(1,r+1):
                process = Process(target=deleteRes,args=(token,massdep_instance,i,))
                process.start() 
                if i % max_simultaneous_process == 0:
                    process.join()   
            process.join() 
            
        else: # if the subscribers are going to be the members of the csp

            for j in range (1,s+1):
                process = Process(target=deleteSubs,args=(token,massdep_instance,j,0,"csp",))
                process.start()
                if j % max_simultaneous_process == 0:
                    process.join()    
            process.join()
    
    b=datetime.datetime.now()
    print("Execution time:",b-a)

        
    
