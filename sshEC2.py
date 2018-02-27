try:
	import boto3
	import botocore
	import paramiko
	import time
	import csv
	import sys
	import os
except Exception as err:
	print "One of the packages were not Found"
	print err
	sys.exit(0)

#This file is used to SSH to the VM instance created.
#Uploads, deletes, creates files on the VM and S3 bucket and logs it into a csv file - log.csv
class connectToEC2():

	bucketName=""
	keyFileName=""
	ipAddr=""
	client=""
	s3=""
	def __init__(self, bucketName, keyFileName, ipAddr):
		self.bucketName= bucketName
		self.keyFileName=keyFileName
		self.ipAddr = ipAddr
		self.client=""

	#Check if the bucket given exists	
	def checkIfBucketExists(self):
		bucket = self.s3.Bucket(self.bucketName)
		exists = True
		try:
			self.s3.meta.client.head_bucket(Bucket=self.bucketName)
		except botocore.exceptions.ClientError as e:
			error_code = int(e.response['Error']['Code'])
			if error_code == 404:
			    exists = False
		return exists       

	#Check if a file upload is successful
	def checkIfUploaded(self,fileName):
		bucket = self.s3.Bucket(self.bucketName)
		#print "FILE NAME:"+fileName
		for files in bucket.objects.all():
		#   print files.key
		    if files.key == fileName:
		    	return True
		return False

	#Check if a file has been created successfully
	def checkIfFileCreated(self, fileName, result):
		exists=True
		if fileName not in result:
			exists=False
		return exists

	#Create a file on the instance	
	def createFile(self, fileName, size):
		fileName = fileName+'.txt'
		createResult=-1
		print "\n\nCreating File: "+fileName+" of "+size+"Mib"
		command = 'fallocate -l '+size+'M '+fileName
		createStart = time.time()
		#Create a dummy file of given size
		stdin, stdout, stderr = self.client.exec_command(command)
		createEnd = time.time()
		stdin, stdout, stderr = self.client.exec_command('ls')
		output = stdout.read()
		#Check if file was created succesfully
		if self.checkIfFileCreated(fileName,output):
			print "File Created: "+fileName
			createResult = createEnd - createStart
		else:
			print "Error in creating File "+fileName
		return createResult

	#Upload file to S3 using VM instance	
	def uploadFile(self, fileName):
		uploadResult=-1
		fileName = fileName+'.txt' 
		print "\nUploading File : "+fileName
		command = 'aws s3 cp '+fileName+' s3://'+self.bucketName
		uploadStart = time.time()
		#Upload the file
		stdin, stdout, stderr = self.client.exec_command(command)
		print stdout.read()
		uploadEnd = time.time()
		#Check if the uploading of file was uploaded successfully
		if self.checkIfUploaded(fileName):
			print "File Uploaded: "+fileName
			uploadResult = uploadEnd - uploadStart
		else:
			print "Error in uploading File: "+fileName
		return uploadResult

	#Read a file from S3 using instance	
	def readFile(self, fileName):
		readResult=-1 
		fileName = fileName+'.txt'
		print "\nReading File : "+fileName
		command =  'aws s3api get-object --bucket '+self.bucketName+' --key '+fileName+' file.log'
		readStart = time.time()
		#Read the file
		stdin, stdout, stderr = self.client.exec_command(command)
		readEnd = time.time()
		stdin, stdout, stderr = self.client.exec_command('ls')
		output= stdout.read()
		readResult = readEnd-readStart
		return readResult

	#Delete a file from S3 and instance	
	def deleteFile(self, fileName):
		fileName= fileName+'.txt'
		deleteResult=-1 
		print "\nDeleting File : "+fileName
		command =  'aws s3api delete-object --bucket '+self.bucketName+' --key '+fileName
		deleteStart = time.time()
		stdin, stdout, stderr = self.client.exec_command(command)
		print stdout.read()
		deleteEnd = time.time()
		#Delete the file
		stdin, stdout, stderr = self.client.exec_command('rm '+fileName)
		output= stdout.read()
		#Check if the file was deleted successfully
		if not self.checkIfUploaded(fileName):
			print "File deleted: "+fileName
			deleteResult = deleteEnd - deleteStart
		else:
			print "Error in deleting File: "+fileName
		return deleteResult


	def callMethods(self, fileName, size, filewriter):
		errorCount=0
		createResult=self.createFile(fileName,size)
		if createResult==-1:
			errorCount+=1
		uploadResult=self.uploadFile(fileName)
		if uploadResult==-1:
			errorCount+=1
		readResult=self.readFile(fileName)
		if readResult==-1:
			errorCount+=1
		deleteResult=self.deleteFile(fileName)
		if deleteResult==-1:
			errorCount+=1

		filewriter.writerow([fileName+'.txt', size+'Mib',createResult,uploadResult,readResult,deleteResult,errorCount])
				

	def connectToEC2Instance(self):
		# Connect/ssh to an instance
		try:
			#print self.bucketName, self.keyFileName, self.ipAddr
			self.s3= boto3.resource('s3')
			with open('log.csv', 'a') as csvfile:
			    filewriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
			    if not os.path.isfile("log.csv"):
			    	filewriter.writerow(['FileName', 'FileSize','Creation Time','Upload Time','Read Time','Delete Time','Total Errors'])
			    if not self.checkIfBucketExists():
			    	print "Bucket does not exists"
			    	sys.exit(0)	
			    key = paramiko.RSAKey.from_private_key_file(self.keyFileName)
			    self.client = paramiko.SSHClient()
			    self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			    print "Connecting to EC2 instance"
			    self.client.connect(hostname=self.ipAddr,username='ec2-user', pkey=key)
			    print "Connected! Running on VM"
			    self.callMethods('o100','100',filewriter)
			    self.callMethods('o300','300',filewriter)
			    self.callMethods('o500','500',filewriter)
			    self.callMethods('o800','800',filewriter)
			    
			    # close the client connection once the job is done
			    self.client.close()
		    

		except Exception, e:
		    print e

file = open('getEC2Details.txt', "r") 
x = file.read().split()
print x
conn = connectToEC2(x[2],x[1],x[0])
conn.connectToEC2Instance()