#!/bin/bash

clear

pip -V
if [ $? -eq 0 ];then
	echo "PIP PRESENT"
elif sudo apt-get install python-pip; then
	echo "Installed pip"
else
	echo "Error in installing PIP"
	exit
fi

aws --version
if [ $? -eq 0 ];then
	echo "AWS PRESENT"
	aws configure

elif sudo pip install awscli --upgrade --user;then
	echo "INSTALLED AWS"
else
	echo "ERror in installing aws"
	exit
fi

sudo pip install boto3
if [ $? -eq 0 ];then
	echo "BOTO 3 Installed"
else
	echo "Error in installing Boto3"
	exit
fi

python createInstance.py
python main.py

file="getEC2Details.txt"
file_name=""
user=""
bucket_name=""
instanceid=""
read user file_name bucket_name instanceid<$file
if [ $? -eq 0 ];then
	echo "Read values"
else
	echo "Error in reading file"
	exit
fi


sudo apt-get install automake autotools-dev fuse g++ git libcurl4-gnutls-dev libfuse-dev libssl-dev libxml2-dev make pkg-config
if [ $? -eq 0 ];then
	echo "INSTALLED"
else
	echo "Error in installing Packages for s3fs"
	exit
fi


if [ ! -d s3fs-fuse ]; then
git clone https://github.com/s3fs-fuse/s3fs-fuse.git
if [ $? -eq 0 ];then
	echo "Cloned S3FS"
else
	echo "Error. Make sure git and other dependencies are installed"
	exit
fi

cd s3fs-fuse
if [ $? -eq 0 ];then
	echo "Cloned S3FS"
else
	echo "Error. Not found"
	exit
fi

./autogen.sh
if [ $? -eq 0 ];then
	echo "Autogen sh file found"
else
	echo "Error. Not found"
	exit
fi

./configure
if [ $? -eq 0 ];then
	echo "Configured"
else
	echo "Error. Not found"
	exit
fi

make
if [ $? -eq 0 ];then
	echo "make"
else
	echo "Error. Not found"
	exit
fi

sudo make install
if [ $? -eq 0 ];then
	echo "success"
else
	echo "Error. Not found"
	exit
fi
fi

if [ ! -d mountS3 ]; then
	mkdir mountS3
	if [ $? -eq 0 ];then
		echo "Folder created"
	else
		echo "Cannot create directory to mount"
		exit
	fi
fi

sudo chmod 600 password.txt
if [ $? -eq 0 ];then
	echo "Mode changed"
else
	echo "Error in changing mode"
	exit
fi

sudo s3fs $bucket_name mountS3 -o passwd_file=password.txt
if [ $? -eq 0 ];then
	echo "Mount Successfull"
else
	echo "Mount Unsuccessful"
	exit
fi


sudo pip install paramiko
if [ $? -eq 0 ];then
	echo "Paramiko Installed"
else
	echo "Error. cant install paramiko"
	exit
fi

python sshEC2.py

