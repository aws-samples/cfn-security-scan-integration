"""
 Generates JUnit report

 Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
 SPDX-License-Identifier: MIT-0
"""
import sys
import re
sys.path.insert(0, "external")
from junit_xml import TestSuite, TestCase

def generate_junit_report_from_cfn_nag(report):
    """Generate Test Case from cfn_nag report"""

    test_cases = []
    for file_findings in report:
        for violation in file_findings["file_results"]['violations']:
            for i,resource_id in enumerate(violation['logical_resource_ids']):
                test_case = TestCase(
                    "%s - %s" % (violation['id'], violation['message']),
                    classname=resource_id)
                test_case.add_failure_info(output="%s#L%s" % (
                    file_findings['filename'], violation['line_numbers'][i]))
                test_cases.append(test_case)

    test_suite = TestSuite("cfn-nag test suite", test_cases)
    return TestSuite.to_xml_string([test_suite], prettyprint=False)

def generate_junit_report_from_cfn_guard(report):
    """Generate Test Case from cloudformation guard report"""

    test_cases = []
    count_id = 0
    for file_findings in report:
        finding = file_findings["message"]
        # extract resource id from finsind line
        resource_regex = re.search("^\[([^]]*)]", finding)
        if resource_regex:
            resource_id = resource_regex.group(1)
            test_case = TestCase(
                "%i - %s" % (count_id, finding),
                classname=resource_id)
            test_case.add_failure_info(output="%s#R:%s" % (file_findings["file"], resource_id))
            test_cases.append(test_case)
            count_id += 1

    test_suite = TestSuite("aws cfn-guard test suite", test_cases)
    return TestSuite.to_xml_string([test_suite], prettyprint=False)
