"""
 AWS Security Hub Integration

 Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
 SPDX-License-Identifier: MIT-0
"""
import sys
import logging
sys.path.insert(0, "external")
import boto3

logger = logging.getLogger(__name__)

securityhub = boto3.client('securityhub')

# This function import agregated report findings to securityhub


def import_finding_to_sh(account_id: str, region: str, created_at: str, source_repository: str, 
    source_branch: str, source_commitid: str, build_id: str, report_url: str, finding_id: str, generator_id: str,
                         normalized_severity: str, severity: str, finding_type: str, finding_title: str, finding_description: str, best_practices_cfn: str):
    """ Import finding to AWS Security Hub """
    new_findings = []

    new_findings.append({
        "SchemaVersion": "2018-10-08",
        "Id": finding_id,
        "ProductArn": "arn:aws:securityhub:{0}:{1}:product/{1}/default".format(region, account_id),
        "GeneratorId": generator_id,
        "AwsAccountId": account_id,
        "Types": [
            "Software and Configuration Checks/AWS Security Best Practices/{0}".format(
                finding_type)
        ],
        "CreatedAt": created_at,
        "UpdatedAt": created_at,
        "Severity": {
            "Product": severity,
            "Normalized": normalized_severity
        },
        "Title":  f"{finding_title} repo:{source_repository}/{source_branch}",
        "Description": f"{finding_description} repo:{source_repository}/{source_branch}#source_commitid",
        'Remediation': {
            'Recommendation': {
                'Text': 'For directions on how to fix this issue, see the AWS Cloud Formation documentation and AWS Best practices',
                'Url': best_practices_cfn
            }
        },
        'SourceUrl': report_url,
        'Resources': [
            {
                'Id': build_id,
                'Type': "CodeBuild",
                'Partition': "aws",
                'Region': region
            }
        ],
    })

    response = securityhub.batch_import_findings(Findings=new_findings)
    if response['FailedCount'] > 0:
        logger.error("Error importing finding: " + response)
        raise Exception("Failed to import finding: {}".format(response['FailedCount']))

def supress_old_reports(generator_id: str, created_at: str, region: str, account_id: str):
    """ Suppress old branch Security Hub findings """
    response = securityhub.get_findings(
        Filters={'GeneratorId': [{'Value': generator_id, 'Comparison': 'EQUALS'}]})

    for finding in response['Findings']:
        try:
            response = securityhub.batch_update_findings(
                FindingIdentifiers=[
                    {'Id':  finding['Id'],
                        'ProductArn': "arn:aws:securityhub:{0}:{1}:product/{1}/default".format(region, account_id)}],
                Workflow={'Status': 'SUPPRESSED'})
        except Exception as error:
            logger.error("Error supressing finding: {}".format(error))
            logger.debug("Finding: {}".format(finding))
