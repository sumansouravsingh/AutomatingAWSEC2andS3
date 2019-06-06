try:
	import boto3 as boto
	import botocore.exceptions
	import sys
	import subprocess
	import os
except Exception as err:
	print "One of the packages were not Found"
	print err
	sys.exit(0)
try:
	from createS3Bucket import BucketFunction
	from ec2functions import EC2Functions
	from InvalidOptionError import InvalidOptionError
	from createVPC import VPC
except Exception as err:
	print "One of the files couldn't be found"
	print err
	sys.exit(0)
## This file is the main entry point. It first captures the user's details. 
#It then configures VPC and creates a security group fpr it
#It then calls the createInstance Method to create instance of EC2.
#Then it creates a S3 bucket which will be mounted on to a folder and on which the files will be uploaded
regionName = ""
client=""
tries = 0

#Get details from User
def selectUser():
	try:
		global regionName
		global client 
		client = boto.client('iam')
		response = client.list_policies(
		    Scope='AWS',
		    OnlyAttached=True,
		    MaxItems=10
		)
		for PolicyName in response["Policies"]:
			print PolicyName["PolicyName"]
		session = boto.session.Session()
		credentials = session.get_credentials()
		credentials = credentials.get_frozen_credentials()
		regionName = session.region_name
		#Create a password.txt file for s3fs fuse
		path_names = os.listdir(".")
		for name in path_names:
			if name=='password.txt':
				os.chmod('password.txt',0777)
				os.chmod('password.txt',0o777)
		password = open('password.txt','w')
		password.write(credentials.access_key+':'+credentials.secret_key)
		#Check if the password file was created successfully
		path_names = os.listdir(".")
		for name in path_names:
			if name=='password.txt':
				return			
	except ValueError as err:
		print err
		sys.exit(0)

	except InvalidOptionError as err:
		print err
		sys.exit(0)

	except botocore.exceptions.ClientError as err:
		print err.response["Error"]["Code"]
		print err.response["Error"]["Message"]
		if err.response["Error"]["Code"]=="InvalidClientTokenId":
			print "Please configure aws with a proper user details"
		elif err.response["Error"]["Code"]=="AccessDenied":
			print "You are not authorised to perform this action"
		sys.exit(0)	
	
	except Exception as err:
		print err
		sys.exit(0)

#create an instance of EC2
def createEC2Instance(ec2Instance, subnetId, groupId):
	global tries
	try:
		if not (ec2Instance.createInstance(subnetId, groupId)):	
			print "EC2 Instance Start Failed! Please note the errors and try to rectify them\n"
			# Allow the user to retry to create an instance (Max tries = 5)
			tryAgain = int(raw_input("Try again? 1 for yes, 0 for no"))
			if tryAgain==1:
				if tries ==5:
					raise InvalidOptionError("You have exceeded Maximum number of tries")
				tries+=1
				createEC2Instance(ec2Instance,subnetId,groupId)
			elif tryAgain==0:
				sys.exit(0)
			else:
				raise InvalidOptionError("Please select 1 or 0")
		else:
			print "Created Instance Successfully"
	except InvalidOptionError as err:
		print err
		sys.exit(0)
	except Exception as err:
		print err
		sys.exit(0)						 			

#Generate a file containing the public ip address of instance, name of key file, id of the instance generated and the bucket name created
def generateDetailsFile(dnsName, fileName,instanceId, bucketName):
	try:
		val = dnsName+' '+fileName+' '+bucketName+' '+instanceId
		#print "Values: ",val
		outputKeyFile = open('getEC2Details.txt','w')
		outputKeyFile.write(val)
		items = os.listdir(".")
		for names in items:
			if names=='getEC2Details.txt':
				return
		raise Exception("Something went wrong")	
	except IOError as err:
		print err
		deleteBucket(bucketName)
		terminateInstance(instanceId)
		sys.exit(0)

	except Exception as err:
		print err
		deleteBucket(bucketName)
		terminateInstance(instanceId)
		sys.exit(0)

def terminateInstance(instanceId):
	try:
		ec2 = boto.resource('ec2')
		ec2.instances.filter(InstanceIds=[instanceId]).stop()
		ec2.instances.filter(InstanceIds=[instanceId]).terminate()
	except Exception as err:
		print "Cannot Terminate instance."
		print err
		sys.exit(0)


def deleteBucket(bucketName):
	try:
		s3 = boto.resource('s3')
		bucket = s3.Bucket(bucketName)
		for key in bucket.objects.all():
			key.delete()

		bucket.delete()
	except Exception as err:
		print "Cannot Terminate instance."
		print err
		#sys.exit(0)


selectUser()
vpc = VPC()
vpc.createAndConfigVPC()
ec2Instance = EC2Functions()
createEC2Instance(ec2Instance,vpc.subnetId,vpc.secGroupId)
bucket = BucketFunction(regionName)
#If problem in creating a bucket, terminate the instance that was created
if not bucket.createBucket():
	terminateInstance(ec2Instance.instanceId)
	sys.exit(0)		

generateDetailsFile(ec2Instance.dnsName, ec2Instance.keyFile, ec2Instance.instanceId, bucket.bucketName)
