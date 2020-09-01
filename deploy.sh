#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
#
# This script deploys the CloudFormation security scan sample in an account
set -e 


function print_usage (){
	echo "------------------------------------------------------------------------------"
	echo "	This script deploys the CloudFormation security scan sample in an account	"	
	echo "------------------------------------------------------------------------------"
	echo "Usage: ./deploy.sh s3bucket aws-cli-profile aws-region"
	echo "For example: ./deploy.sh  mybucket myprofile eu-west-1"
	echo 
}


if [ -z $1 ]; then 
	echo "Error: provide as first(1) param target bucket without prefix"
	print_usage
	exit 1
else 
	bucket="$1"
fi

if [ -z $2 ]; then 
	echo "Error: provide as second(2) param the AWS CLI profle"
	print_usage
	exit 2
else
	profile="$2"
fi

if [ -z $3 ]; then 
	echo "Error: provide as third(3) param the AWS region"
	print_usage
	exit 3
else
	region=$3
fi

if  [ "${bucket: -1}" = "/" ]; then 
	bucket="${bucket%%/}"
	echo "removed slash at the end of $bucket" 
fi

rm -rf src/functions/external || echo "dir 'src/functions/external' does not exists"
[ -d "dist" ] && rm -rf dist/* || mkdir dist

random=$(dd if=/dev/random bs=6 count=1 2>/dev/null | od -An -tx1 | tr -d ' \t\n')
prefix="${random}/"
# Add source bucket and prefix 
b=${bucket#*//}
sed "s/{S3BucketSources}/${b}/" ./conf/params.sh | sed "s|{S3SourcesPrefix}|${prefix}|" > "./dist/.tmp.param.sh"

DEPENDENCIES=$(cd 'src/functions' && pip install -r requirements.txt -t external)

export AWS_CFN="aws cloudformation --region $region --profile $profile"

(cd src/functions && zip -r  "./../../dist/cfn-scan-functions.zip" "./" )
aws s3 cp --exclude ".*" --recursive "./src/cfn/"   "s3://$bucket/${prefix}" 
aws s3 cp "./dist/cfn-scan-functions.zip"  "s3://$bucket/${prefix}"
echo "resource uploaded successfully to ${bucket}"

. ./dist/.tmp.param.sh

$AWS_CFN deploy --stack-name "security-test-integration-sample" --template-file "./src/cfn/main.yaml" --no-fail-on-empty-changeset --parameter-overrides "${PARAMETERS[@]}"  --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND CAPABILITY_IAM
