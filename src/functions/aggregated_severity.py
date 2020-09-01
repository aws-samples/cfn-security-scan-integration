"""

 Calculates the aggregated severity

 Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
 SPDX-License-Identifier: MIT-0
"""
import os

MULTIPLICATOR_CRITICAL_FINDING = int(os.environ['WeightFailing'])
MULTIPLICATOR_WARNING_FINDING = int(os.environ['WeightWarning'])
MAX_NORMALIZED=100

def calculate_severity_cfn_nag(cfn_nag_report: dict):
    # calculate the severity score
    fail = 0
    warn = 0

    for file in cfn_nag_report:
        if "file_results" in file and "violations" in file["file_results"]:
            for violation in file["file_results"]["violations"]:
                if violation["id"] != "FATAL":
                    if violation["type"] == "FAIL":
                        fail = fail+len(violation['logical_resource_ids'])
                    elif violation["type"] == "WARN":
                        warn = warn+len(violation['logical_resource_ids'])

    severity = fail*MULTIPLICATOR_CRITICAL_FINDING+warn*MULTIPLICATOR_WARNING_FINDING
    normalized_severity = MAX_NORMALIZED if severity > MAX_NORMALIZED else severity

    return (normalized_severity, severity)


def calculate_severity_cfn_guard(cfn_guard_report):
    # calculate the severity score
    severity = len(cfn_guard_report)*MULTIPLICATOR_CRITICAL_FINDING
    normalized_severity = MAX_NORMALIZED if severity > MAX_NORMALIZED else severity

    return (normalized_severity, severity)
