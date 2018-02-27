import boto3 as boto
import sys
import botocore.exceptions
import os
from ec2exception import EC2Exception
import time
import subprocess


#File creates an instance of EC2
#It creates a key and assigns it to the instance profile
class EC2Functions():
	instanceId=""
	accessKey =""
	secretKey=""
	instanceCnt=0
	ec2=""
	client=""
	dnsName=""
	keyFile=""
	roleName=""
	instanceProfile=""
	def __init__(self):
		self.instanceId=""
		self.accessKey=""
		self.secretKey=""
		self.instanceCnt=0
		self.ec2=""
		self.client=""
		self.dnsName="empty"
		self.keyFile=""
		self.roleName=""
		self.instanceProfile="tempo"
	def checkIfFileExists(self,fileName):
		items = os.listdir(".")
		for names in items:
			if names==fileName:
				return True
		return False			

	#Check if keyname already exists
	def checkIfKeyExists(self, keyName):
		response = self.client.describe_key_pairs()
		for keyNames in response["KeyPairs"]:
			if keyName==keyNames["KeyName"]:
				return False
		return True						

	def waitForInstanceToBeRunning(self):
		#If instance does not change to running state after 2 minutes, exit program
		if(self.instanceCnt>12):
			print "Cannot start the instance"
			sys.exit(0)
		instances = self.ec2.instances.filter(
			    Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
		for instance in instances:
		    if self.instanceId==instance.id:
		    	return
		time.sleep(10)
		print("Waiting for instance to start running")
		self.instanceCnt+=1
		self.waitForInstanceToBeRunning()		    		
	
	def createInstance(self, subnetId, groupId):
		instanceType = 't2.micro' #create instance of type t2.micro
		try:
			imageId = "ami-f63b1193"
			imageId = raw_input("Enter image id. (Press Enter to select default image id: ami-f63b1193):")
			if not imageId:
				imageId='ami-f63b1193'
			if imageId.find("ami")!=0:
				raise EC2Exception("ImageId should start with ami")
			self.ec2 = boto.resource('ec2')
			self.client = boto.client('ec2')
			response = self.client.describe_key_pairs()
			keyName = raw_input("Enter key name to be created or enter the name of an existing key:")
			keyInstance=""
			val=self.checkIfKeyExists(keyName)
			#create a new key, store it in a file and check if the file was created successfully
			if val:
				keyInstance = self.ec2.create_key_pair(KeyName=keyName)
				if self.checkIfKeyExists(keyName):
					raise EC2Exception("Error in creating key")
			val=self.checkIfFileExists(keyName+'.pem')	
			
			##create key file, if new key  and check if created successfully
			if not val:
				#if the key already existed and the key file is not present, throw error
				if not keyInstance:
					raise Exception ("Private key file not found. Please create a new key")
				keyPair = str(keyInstance.key_material)
				outputKeyFile = open(keyName+'.pem','w')
				outputKeyFile.write(keyPair)
				val = self.checkIfFileExists(keyName+'.pem')
				if not val:
					raise IOError ("Error in creating key file")
			
			os.chmod(keyName+'.pem',400)
			os.chmod(keyName+'.pem',0400)
			os.chmod(keyName+'.pem',0o400)
			val = False		
			self.keyFile = keyName+'.pem'
	
			#Create a new Instance	
			print ("Creating EC2 Instance")
			instance = self.ec2.create_instances(
			    ImageId=imageId,
			    MinCount=1,
			    MaxCount=1,
			    KeyName=keyName,
			    InstanceType=instanceType,
			    IamInstanceProfile={
                    'Name': 'sumaninstance1'
                },
                NetworkInterfaces=[{'SubnetId': subnetId,'DeviceIndex': 0, 'AssociatePublicIpAddress': True, 'Groups': [groupId]}])
			self.instanceId = instance[0].id
			#check if Instance Creation Successfull
			print("Waiting for instance to start running")
			self.waitForInstanceToBeRunning()
			response = self.client.describe_instances(InstanceIds=[self.instanceId])
			response =  response['Reservations'][0]['Instances'][0]['PublicIpAddress']
			self.dnsName = response
			return True
		except botocore.exceptions.ClientError as err:
			print "Error Code: ",err.response["Error"]["Code"]
			print "Reason: ",err.response["Error"]["Message"]
			if (err.response["Error"]["Code"]=="AuthFailure"):		
				print "AWS is not Configured. Kindly configure by running aws configure in cmd"
				sys.exit(0)
			return False 	
		except EC2Exception as err:
			print "Error in creating instance:\n"
			print err.msg
			return False

		except IOError as err:
			print err
			return False	

		except Exception as err:
			print "Error: ",err
			return False 	