# Copyright 2022 Fuzz Introspector Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Module for creating JSON reports"""
import os
import json
import logging

from typing import (
    Any,
    List,
    Dict
)

from fuzz_introspector import analysis, constants
from fuzz_introspector.datatypes import project_profile, fuzzer_profile


logger = logging.getLogger(name=__name__)


def _retrieve_json_section(
    analyser_name: str,
    analysis_instance: analysis.AnalysisInterface
) -> str:
    """
    Generate json string for saving the result of a
    specific analyser
    """
    if analyser_name in [item.get_name() for item in analysis.get_all_analyses()]:
        return analysis_instance.get_json_string_result()
    return json.dumps([])


def create_json_report(
    profiles: List[fuzzer_profile.FuzzerProfile],
    proj_profile: project_profile.MergedProjectProfile,
    analyser_instance_dict: Dict[str, analysis.AnalysisInterface],
    coverage_url: str
) -> None:
    """
    Generate json report for the fuzz-introspector execution session.
    This method is also extendable in the future to act in more
    results from other sessions to be included in the json format
    of the output.
    """

    logger.info(" - Creating JSON report for fuzz-introspetcor")
    if not proj_profile.has_coverage_data():
        logger.error(
            "No files with coverage data was found. This is either "
            "because an error occurred when compiling and running "
            "coverage runs, or because the introspector run was "
            "intentionally done without coverage collection. In order "
            "to get optimal results coverage data is needed."
        )

    result_dict: Dict[str, Dict[str, Any]] = {'report': {}}
    for analyses_name in analyser_instance_dict.keys():
        logger.info(f" - Handling {analyses_name}")
        result_str = _retrieve_json_section(
            analyses_name,
            analyser_instance_dict[analyses_name]
        )
        result_dict['report'][analyses_name] = json.loads(result_str)

    result_str = json.dumps(result_dict)
    logger.info("Finish handling sections that need json output")

    # Write the json string to file
    report_file = constants.JSON_REPORT_FILE
    if os.path.isfile(report_file):
        os.remove(report_file)
    with open(report_file, "a+") as file:
        file.write(result_str)
