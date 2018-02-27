import boto3 as boto
import re
import botocore
from InvalidOptionError import InvalidOptionError
import sys

class BucketFunction():		
	s3BucketObj=""
	region=""
	bucketName=""
	client=""
	def __init__(self, region):
		self.s3BucketObj = boto.resource('s3')
		self.client = boto.client('s3')
		self.region = region
		self.bucketName=""

	#Check if bucket name already exists
	def checkIfBucketExists(self,bucketName):
		bList = self.client.list_buckets()
		for bucket in bList['Buckets']:
			if bucketName== bucket['Name']:
				return True
		return False		
	
	#create a bucket	
	def createBucket(self):
		try:
			listOfDetails = self.getInputDetails()
			#Return if there was an error in input
			if not listOfDetails:
				return False
			#Create a bucket
			bucket = self.s3BucketObj.create_bucket(ACL=listOfDetails[0], Bucket=listOfDetails[1], CreateBucketConfiguration= {'LocationConstraint': listOfDetails[2]} )
			#Check whether the bucket was successfully uploaded or not
			val = self.checkIfBucketExists(listOfDetails[1])
			if not val:
				raise Exception("Error! Bucket was not created")
			return True	
		except Exception as e:
			print "Error Occurred!"
			print e
			return False

	#Get and verify the input from user for bucket creation 		
	def getInputDetails(self):
		try:
			ACLopt = int(raw_input("Select a ACL type:\nPress\n1 for 'private'| 2 for 'public-read'| 3 for 'public-read-write'|4 for 'authenticated-read "))
			ACLVals = ['private','public-read','public-read-write', 'authenticated-read']
			aclVal=''
			if 1<=ACLopt<=4:
				aclVal = ACLVals[ACLopt-1]
			else:
				raise InvalidOptionError("Please Select a valid ACL Option")
			self.bucketName = raw_input("Enter bucket name\n")
			#match if the entered name satisfies aws S3 bucket naming conditions
			bucketMatch = re.match('^([a-z]|(\d(?!\d{0,2}\.\d{1,3}\.\d{1,3}\.\d{1,3})))([a-z\d]|(\.(?!(\.|-)))|(-(?!\.))){1,61}[a-z\d]$',self.bucketName)
			if not self.bucketName:
				raise InvalidOptionError("Bucket Name Cannot be blank")
			if (64>len(self.bucketName)<3):
				raise InvalidOptionError("Bucket Name should be between 3-63 characters")
			if not bucketMatch: 
				raise InvalidOptionError("Invalid Name Format. Please check the naming conventions for s3 bucket")	
			if self.checkIfBucketExists(self.bucketName):
				raise Exception("Error! Bucket name already exists")
			return [aclVal,self.bucketName,self.region]	
						
		except ValueError as err:
			print err
			return False		

		except InvalidOptionError as err:
			print err.message
			return False

		except Exception as err:
			print err
			return False
