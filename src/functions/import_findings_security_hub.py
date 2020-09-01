"""
 Imports finding in Security Hub and generate JUnit report

 Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
 SPDX-License-Identifier: MIT-0
"""

import os
import json
import logging

import boto3
import junit_report
import aggregated_severity
import upload
import securityhub

logger = logging.getLogger()
logger.setLevel(logging.INFO)

FINDING_TITLE = "CFN scan"
FINDING_DESCRIPTION_TEMPLATE = "Summarized report of code scan with {0}"
FINDING_TYPE_TEMPLATE = "{0} code scan"
BEST_PRACTICES_CFN = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/best-practices.html"


def process_message(event):
    """ Process Lambda Event """
    if event['messageType'] == 'CodeScanReport':

        account_id = boto3.client('sts').get_caller_identity().get('Account')
        region = os.environ['AWS_REGION']
        created_at = event['createdAt']
        source_repository = event['source_repository']
        source_branch = event['source_branch']
        source_commitid = event['source_commitid']
        build_id = event['build_id']
        report = event['report']
        report_type = event['reportType']

        finding_type = FINDING_TYPE_TEMPLATE.format(report_type)
        finding_description = FINDING_DESCRIPTION_TEMPLATE.format(report_type)
        finding_id = f"{report_type.lower()}-{source_repository}-{source_branch}-{build_id}"
        generator_id = f"{report_type.lower()}-{source_repository}-{source_branch}"

        # Update old findings in Security Hub for the repo:branch to resolved
        securityhub.supress_old_reports(
            generator_id, created_at, region, account_id)

        if event['reportType'] == 'CFN-NAG':
            (normalized_severity,
             severity) = aggregated_severity.calculate_severity_cfn_nag(report)

            report_url = upload.upload_report("cfn_nag", report, created_at, source_repository, source_branch)

            # import to Security Hub
            securityhub.import_finding_to_sh(account_id, region, created_at, source_repository,
                                             source_branch, source_commitid, build_id, report_url,
                                             finding_id, generator_id, normalized_severity, severity,
                                             finding_type, FINDING_TITLE, finding_description, BEST_PRACTICES_CFN)

            return junit_report.generate_junit_report_from_cfn_nag(report).encode("unicode_escape")

        elif event['reportType'] == 'CFN-GUARD':
            (normalized_severity,
             severity) = aggregated_severity.calculate_severity_cfn_guard(report)
            # import to Security Hub
            report_url = upload.upload_report("cfn-guard", report, created_at, source_repository, source_branch)

            securityhub.import_finding_to_sh(account_id, region, created_at, source_repository,
                                             source_branch, source_commitid, build_id, report_url,
                                             finding_id, generator_id, normalized_severity, severity,
                                             finding_type, FINDING_TITLE, finding_description, BEST_PRACTICES_CFN)

            # generate JUnit report
            return junit_report.generate_junit_report_from_cfn_guard(report).encode("unicode_escape")
    else:
        logger.error("Report type not supported: {}".format(event['reportType']))


def lambda_handler(event, context):
    """ Lambda entrypoint """
    try:
        logger.info("Starting function")
        return process_message(event)
    except Exception as error:
        logger.error("Error {}".format(error))
        raise
