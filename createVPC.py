import boto3
import sys

#This file creates a VPC and security group
class VPC():
	subnetId=""
	vpcId=""
	secGroupId=""

	def __init__(self):
		self.subnetId=""
		self.vpcId=""
		self.secGroupId=""
		
	def createAndConfigVPC(self):
		ec2 = boto3.resource('ec2')
		client = boto3.client('ec2')
		try:
			x=""
			response = client.describe_security_groups()
			for res in response['SecurityGroups']:
				if(res['GroupName']=='securityGroupSuman'):
					x= res['VpcId']
					filters = [{'Name':'vpc-id', 'Values':[x]}]
					subnets = list(ec2.subnets.filter(Filters=filters))
					self.subnetId=subnets[0].id
					self.vpcId = x
					self.secGroupId = res['GroupId']
					return
			
			#sys.exit(0)
			print "NOT FOUND HERE"	
		except Exception as err:
			print "NOT FOUND"
			sys.exit(0)         

		# create VPC       
		vpc = ec2.create_vpc(CidrBlock='192.168.0.0/16')
		# we can assign a name to vpc, or any resource, by using tag
		vpc.create_tags(Tags=[{"Key": "Name", "Value": "suman_vpc_1"}])
		vpc.wait_until_available()
		self.vpcId= vpc.id
		ig = ec2.create_internet_gateway()
		vpc.attach_internet_gateway(InternetGatewayId=ig.id)
		#print(ig.id)

		# create a route table and a public route
		route_table = vpc.create_route_table()
		route = route_table.create_route(
		    DestinationCidrBlock='0.0.0.0/0',
		    GatewayId=ig.id
		)
		#print(route_table.id)

		# create subnet
		subnet = ec2.create_subnet(CidrBlock='192.168.1.0/24', VpcId=vpc.id)
		self.subnetId= subnet.id

		# associate the route table with the subnet
		route_table.associate_with_subnet(SubnetId=subnet.id)

		ip_ranges = [{
		        'CidrIp': '0.0.0.0/0'
		}]
		# Create sec group
		sec_group = ec2.create_security_group(
		    GroupName='securityGroupSuman', Description='Automated security group', VpcId=vpc.id)
		permissions = [{
			'IpRanges': ip_ranges,
			'IpProtocol': 'TCP',
		    'FromPort': 443,
		    'ToPort': 443
		},
		{
			'IpRanges': ip_ranges,
			'IpProtocol': 'TCP',
			'FromPort': 80,
			'ToPort': 80
		},
		{
			'IpRanges': ip_ranges,
			'IpProtocol': 'TCP',
			'FromPort': 22,
			'ToPort': 22
		}
		]
		sec_group.authorize_ingress(
		    IpPermissions=permissions)

		self.secGroupId = sec_group.group_id
		return 
		

