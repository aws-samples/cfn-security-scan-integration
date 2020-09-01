# Integrating AWS CloudFormation security tests with AWS Security Hub and AWS CodeBuild reports

The concept of infrastructure as code, by using pipelines for continuous integration and delivery, is fundamental for the development of cloud infrastructure. Including code quality and vulnerability scans in the pipeline is essential for the security of this infrastructure as code.

In this sample code, we introduce a method for integrating open source tools that find potentially insecure patterns in your AWS CloudFormation templates with both AWS Security Hub and AWS CodeBuild reports. We’ll be using Stelligent’s open source tool CFN-Nag. We also show you how you can extend the solution to use AWS CloudFormation Guard (currently in preview).

For more information on the solution, see [AWS Blog](https://aws.amazon.com/blogs/security/integrating-aws-cloudformation-security-tests-with-aws-security-hub-and-aws-codebuild-reports/)

## Getting Started

### Prerequisites

* [AWS CLI](https://aws.amazon.com/cli/) - AWS Command Line Interface
* AWS Security Hub is enabled for that particular account and region  

### Usage

### Step 1. Clone this repository

From your terminal application, execute the following command:

`git clone git@github.com:aws-samples/cfn-security-scan-integration.git`

### Step 2. Create S3 bucket for artifacts in sougitrce account

Create a S3 bucket where the artifacts will be uploaded. Your AWS CLI selected profile must have read/write permission to the bucket. It can be in the different region from the region you choose to deploy the solution. 

### Step 3. Copy HTTPS URL for target repository

Create or select an existing CodeCommit repository that you want to scan and copy its HTTPS URL. The repository must be in the same AWS account and region where you deploy.

### Step 4. Configure parameters

Update `./conf/params.sh` with the specific Cloudformation parameters such as repository and branch to scan copied above, tool to use (CFN-Guard or CFN-Nag) and whether to fail or not the pipeline.

### Step 5. Deploy the solution

Run the deploy script, like `./deploy.sh bucket aws-cli-profile region`

Example:
`./deploy.sh sources-cfn-scan my-cli-profile eu-west-1`

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.
