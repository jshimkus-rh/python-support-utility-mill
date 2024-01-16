#! /usr/bin/env python
#
# SPDX-License-Identifier: BSD-2-Clause
#
# Copyright Red Hat
#

import os
import tempfile
import unittest

from Defaults import Defaults

#############################################################################
#############################################################################
class Test_Defaults(unittest.TestCase):

  ####################################################################
  # Correctly generated environment variables.
  def test_environment_variables(self):
    file = tempfile.NamedTemporaryFile("w+")
    file.write("""---
      defaults:
        global1: some-global-value
        global2: another-global-value

        # Group1 data:
        group1:
          default: group1-data
          subgroup1:
            default: default11
            value1: value111
            value2: value112
          subgroup2:
            default: default12
            value1: value121
            value2: value122

        # Group2 defaults:
        group2:
          default: group2-data
          subgroup1:
            default: default21
            value1: value211
            value2: value212
          subgroup2:
            default: default22
            value1: value221
            value2: value222
      """
    )
    file.flush()

    valid = {
      "GLOBAL1",
      "GLOBAL2",
      "GROUP1_DEFAULT",
      "GROUP1_SUBGROUP1_DEFAULT",
      "GROUP1_SUBGROUP1_VALUE1",
      "GROUP1_SUBGROUP1_VALUE2",
      "GROUP1_SUBGROUP2_DEFAULT",
      "GROUP1_SUBGROUP2_VALUE1",
      "GROUP1_SUBGROUP2_VALUE2",
      "GROUP2_DEFAULT",
      "GROUP2_SUBGROUP1_DEFAULT",
      "GROUP2_SUBGROUP1_VALUE1",
      "GROUP2_SUBGROUP1_VALUE2",
      "GROUP2_SUBGROUP2_DEFAULT",
      "GROUP2_SUBGROUP2_VALUE1",
      "GROUP2_SUBGROUP2_VALUE2"
    }

    defaults = Defaults(file.name)

    self.assertEqual(defaults.environmentVariables(),
                     valid,
                     "environment variables match leaf paths")


  ####################################################################
  # Environmental override.
  def test_environmental_override(self):
    file = tempfile.NamedTemporaryFile("w+")
    file.write("""---
      defaults:
        global1: some-global-value
      """
    )
    file.flush()

    defaults = Defaults(file.name)

    path = ["global1"]
    environmentVariable = defaults._pathAsEnvironmentVariable(path)
    try:
      del os.environ[environmentVariable]
    except KeyError:
      pass

    self.assertEqual(defaults.content(path),
                     "some-global-value",
                     "value from defaults")

    os.environ[environmentVariable] = "some-overridden-value"
    self.assertEqual(defaults.content(path),
                     "some-overridden-value",
                     "value from environmental override")


#############################################################################
#############################################################################
if __name__ == "__main__":
  unittest.main()
