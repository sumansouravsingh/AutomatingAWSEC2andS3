try:
	import boto3 as boto
	import sys
	import botocore.exceptions

except Exception as err:
	print "One of the packages were not Found"
	print err
	sys.exit(0)
#This file creates an instance profile to which a role will be added, which in turn will be assigned with EC2 instance
iam = boto.client('iam')
resIam = boto.resource('iam')
try:
	response = iam.list_instance_profiles(
	    PathPrefix='/',
	    MaxItems=123
	)
	#print response
	#If instance found, exit, else throw error to create new instance and role
	for r in response['InstanceProfiles']:
		if r['InstanceProfileName']=='sumaninstance1':
			print "Instance Found"
			sys.exit(0)
	raise Exception ("Creating Instance Profile")	
except Exception as e:	
	print e
	try:
		str1='{"Version": "2012-10-17","Statement": {"Sid": "","Effect": "Allow","Principal": {"Service": "ec2.amazonaws.com"},"Action": "sts:AssumeRole"}}'
		instance_profile = iam.create_instance_profile(InstanceProfileName='sumaninstance1',Path='/')
		roleName = raw_input('Enter Role Name')
		role = iam.create_role(
			    Path='/',
			    RoleName=roleName,
			    AssumeRolePolicyDocument= str1,
			    Description="Allow EC2 instances to call AWS services"
			)
		response = iam.attach_role_policy(
	    	RoleName=roleName, PolicyArn='arn:aws:iam::aws:policy/AdministratorAccess')
		
		response = iam.attach_role_policy(
		    RoleName=roleName,
		    PolicyArn='arn:aws:iam::aws:policy/AmazonS3FullAccess'
		)
		response = iam.attach_role_policy(
		    RoleName=roleName,
		    PolicyArn='arn:aws:iam::aws:policy/AmazonEC2FullAccess'
		)
		iam.add_role_to_instance_profile(InstanceProfileName='sumaninstance1', RoleName=roleName)
	except botocore.exceptions.ClientError as err:	
		print "Instance_profile is:\n"
		print err
