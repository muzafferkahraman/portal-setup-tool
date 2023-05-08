# labdeploy 
labdeploy is a python script to create and delete Nuage SDWAN Portal Resellers,Subscribers and Branches via API <br /> 
Author: Muzaffer Kahraman (Muzo) <br /> 
v 1.0 2023

**Example Usage:**

for creating

> python labdeploy.py create reseller --name aaareseller -f reseller.json
python labdeploy.py create subscriber --name aasubscriber1 --parentName aaareseller -f subscriber.json        
python labdeploy.py create subscriber --name aasubscriber2 --parentName csp  -f subscriber.json       
python labdeploy.py create branch --name nsg1 --orgName aasubscriber1 --parentName aaareseller  -f branch.json    
python labdeploy.py create branch --name nsg2 --orgName aasubscriber2 --parentName csp  -f branch.json
  

for deleting
	
> python labdeploy.py delete  branch --name nsg2 --orgName aasubscriber2 --parentName csp
python labdeploy.py delete  branch --name nsg1 --orgName aasubscriber1 --parentName aaareseller 
python labdeploy.py delete  subscriber --name aasubscriber1 --parentName aaareseller
python labdeploy.py delete  subscriber --name aasubscriber2 --parentName csp        
python labdeploy.py delete  reseller --name aaareseller

where parent name always indicate the reseller name/csp
and the orgNAme is the susbscriber name that the nsg belongs to

# massdeploy 

massdeploy is a python script to create and delete mass number of Nuage SDWAN Portal Resellers,Subscribers and Branches via API <br /> 
Author: Muzaffer Kahraman (Muzo) <br /> 
v 1.0 2023

This script utilizes labdeploy.py's class methods

**Example Usage:**

for creating 
> python massdeploy.py create -r 2 -s 2 -b 2<br /> 

for deleting
> python massdeploy.py delete -r 2 -s 2 -b 2

where 

-r is the number of resellers

-s is the number of subscribers per reseller

-b is the number of branches per subscriber

please set -r as 0 to to specify csp

