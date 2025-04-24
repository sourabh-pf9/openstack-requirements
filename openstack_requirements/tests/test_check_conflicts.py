# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import openstack_requirements
import pkg_resources
import sys
import testtools

from openstack_requirements.cmds import check_conflicts
from unittest import mock


class CheckConflictsTest(testtools.TestCase):

    def setUp(self):
        super(CheckConflictsTest, self).setUp()

    @mock.patch.object(pkg_resources, "require")
    def test_all_uc_required(self, mock_require):
        test_args = [
            "check_conflicts",
            "upper-constraints.txt",
            "upper-constraints-xfails.txt",
        ]
        with mock.patch.object(sys, "argv", test_args):
            ret = check_conflicts.main()

        pkgs = set(
            [
                uc.key
                for uc in pkg_resources.parse_requirements(
                    open("upper-constraints.txt", "rt").read()
                )
            ]
        )

        rpkgs = set([call.args[0] for call in mock_require.mock_calls])

        self.assertEqual(pkgs, rpkgs)
        self.assertEqual(ret, 0)

    @mock.patch("importlib.metadata.version", return_value="1.0.0")
    @mock.patch.object(pkg_resources, "require",
                       side_effect=pkg_resources.DistributionNotFound)
    def test_all_uc_alternative_method(self, mock_require, mock_metadata):
        test_args = [
            "check_conflicts",
            "upper-constraints.txt",
            "upper-constraints-xfails.txt",
        ]
        original_fn = (
            openstack_requirements.cmds.check_conflicts.read_requirements_file
        )

        def patched_uc_read(filename):
            output = {}
            uc = original_fn(filename)

            for name, _ in uc.items():
                fake_spec_list = (
                    openstack_requirements.requirement.Requirement(
                        name, "", "===1.0.0", "", ""
                    )
                )
                output[name] = [(fake_spec_list, f"{name}===1.0.0\n")]
            return output

        with (
            mock.patch.object(sys, "argv", test_args),
            mock.patch(
                "openstack_requirements.cmds.check_conflicts."
                "read_requirements_file",
                side_effect=patched_uc_read,
            ),
        ):
            ret = check_conflicts.main()

        pkgs = set(
            [
                uc.key
                for uc in pkg_resources.parse_requirements(
                    open("upper-constraints.txt", "rt").read()
                )
            ]
        )
        rpkgs = set([call.args[0] for call in mock_metadata.mock_calls])

        self.assertEqual(pkgs, rpkgs)
        self.assertEqual(ret, 0)

    @mock.patch("importlib.metadata.version", return_value="2.0.0")
    @mock.patch.object(
        pkg_resources,
        "require",
        side_effect=pkg_resources.DistributionNotFound,
    )
    def test_all_uc_alternative_method_failure(
        self, mock_require, mock_metadata
    ):
        test_args = [
            "check_conflicts",
            "upper-constraints.txt",
            "upper-constraints-xfails.txt",
        ]
        original_fn = (
            openstack_requirements.cmds.check_conflicts.read_requirements_file
        )

        def patched_uc_read(filename):
            output = {}
            uc = original_fn(filename)

            for name, _ in uc.items():
                fake_spec_list = (
                    openstack_requirements.requirement.Requirement(
                        name, "", "===1.0.0", "", ""
                    )
                )
                output[name] = [(fake_spec_list, f"{name}===1.0.0\n")]
            return output

        with (
            mock.patch.object(sys, "argv", test_args),
            mock.patch(
                "openstack_requirements.cmds.check_conflicts."
                "read_requirements_file",
                side_effect=patched_uc_read,
            ),
        ):
            exc = self.assertRaises(ValueError, check_conflicts.main)

            self.assertIn(
                "version mismatch version 1.0.0 is required and current "
                "package version is 2.0.0.",
                str(exc),
            )
