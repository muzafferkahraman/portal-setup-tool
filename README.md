# labdeploy 
labdeploy is a python script to create and delete Nuage SDWAN Portal Resellers,Subscribers and Branches via API <br /> 
Author: Muzaffer Kahraman (Muzo) <br /> 
v 1.0 2023

**Example Usage:**

for creating

> python labdeploy.py create reseller --name reseller1 -f reseller.json <br />
python labdeploy.py create subscriber --name subscriber1 --parentName reseller1 -f subscriber.json <br />    
python labdeploy.py create subscriber --name subscriber2 --parentName csp  -f subscriber.json <br />      
python labdeploy.py create branch --name nsg1 --orgName subscriber1 --parentName reseller1  -f branch.json <br /> 
python labdeploy.py create branch --name nsg2 --orgName subscriber2 --parentName csp  -f branch.json <br />
python labdeploy.py create rg --name rg1 --orgName subscriber1 --parentName reseller1  -f rg.json -fn branch.json <br />    
python labdeploy.py create rg --name rg1 --orgName subscriber2 --parentName csp  -f rg.json -fn branch.json <br />   
* Each of the last 2 commands create 2 NSGs (rg1nsg1 and rg2nsg2) and combines them under a RG named rg1 
  

for deleting
	
> python labdeploy.py delete  branch --name nsg2 --orgName subscriber2 --parentName csp <br />
python labdeploy.py delete  branch --name nsg1 --orgName subscriber1 --parentName reseller1 <br />
python labdeploy.py delete --name rg1 --orgName subscriber1 --parentName reseller1 <br />
python labdeploy.py delete --name rg1 --orgName subscriber2 --parentName csp <br />
python labdeploy.py delete  subscriber --name subscriber1 --parentName reseller <br />
python labdeploy.py delete  subscriber --name subscriber2 --parentName csp <br />   
python labdeploy.py delete  reseller --name aaareseller <br />

where parent name always indicate the reseller name/csp
and the orgNAme is the susbscriber name that the nsg belongs to

# massdeploy 

massdeploy is a python script to create and delete mass number of Nuage SDWAN Portal Resellers,Subscribers and Branches via API <br /> 
Author: Muzaffer Kahraman (Muzo) <br /> 
v 1.0 2023

This script utilizes labdeploy.py's class methods

**Example Usage:**

for creating 
> python massdeploy.py create -r 2 -s 2 -b 2 -g 2 -p 5<br /> 

for deleting
> python massdeploy.py delete -r 2 -s 2 -p 2

* You don't need to specify branches and RGs when deleting

where 

-r is the number of resellers

-s is the number of subscribers per reseller

-b is the number of branches per subscriber

-g is the number of redundant groups per subscriber 

-p is the number of the simultaneous processes, 5 is reccomended for creation, and 2 for deletion

please set -r as 0 to to specify csp

