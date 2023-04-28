#! /usr/bin/env python
#
# SPDX-License-Identifier: BSD-2-Clause
#
# Copyright Red Hat
#

import tempfile
import unittest

from DataFile import (DataException,
                      DataFile,
                      DataFileContentMissingException,
                      DataFileDoesNotExistException,
                      DataFileFormatException)

#############################################################################
#############################################################################
class Test_DataFile(unittest.TestCase):

  ####################################################################
  # Correctly formatted data.
  def test_correctFormat(self):
    file = tempfile.NamedTemporaryFile("w+")
    file.write("""---
      data:
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

    try:
      dataFile = DataFile(file.name)
    except Exception as ex:
      self.assertFalse(isinstance(ex, DataException))
      raise Exception("unexpected non-Data exception: {0}".format(ex))

    self.assertEqual(dataFile.content(["global1"]), "some-global-value")

    subgroup1 = dataFile.content(["group1", "subgroup1"])
    self.assertIsNotNone(subgroup1)
    self.assertTrue(isinstance(subgroup1, dict))

    self.assertEqual(dataFile.content(["value1"], subgroup1), "value111")

    with self.assertRaises(DataFileContentMissingException):
      dataFile.content(["non-existent-value"], subgroup1)

    self.assertEqual(dataFile.content(["group2", "subgroup1", "value1"]),
                     "value211")

    with self.assertRaises(DataFileContentMissingException):
      dataFile.content(["group2", "subgroup1", "non-existent-value"])

  ####################################################################
  # DataFile with a list.
  def test_List(self):
    file = tempfile.NamedTemporaryFile("w+")
    file.write("""---
      data:
        list:
          - a
      """
    )
    file.flush()

    try:
      dataFile = DataFile(file.name)
    except Exception as ex:
      self.assertFalse(isinstance(ex, DataException))
      raise Exception("unexpected non-Data exception: {0}".format(ex))

    self.assertTrue(isinstance(dataFile.content(["list"]), list))

  ####################################################################
  # File missing highest-level 'data'.
  def test_missingDataKey(self):
    file = tempfile.NamedTemporaryFile("w+")
    file.write("""---
      some-data:
        global1: some-global-value
        global2: another-global-value

        # Group1 data:
        group1:
          default: group1-data
          subgroup1:
            default: subgroup1-data
            value1: value11
            value2: value12
          subgroup2:
            default: subgroup2-data
            value1: value21
            value2: value22

        # Group2 data:
        group2:
          default: group2-data
          subgroup1:
            default: subgroup1-data
            value1: value11
            value2: value12
          subgroup2:
            default: subgroup2-data
            value1: value21
            value2: value22
      """
    )
    file.flush()

    with self.assertRaises(DataFileFormatException):
      DataFile(file.name)

  ####################################################################
  # Non-existent file.
  def test_nonExistentFile(self):
    with self.assertRaises(DataFileDoesNotExistException):
      DataFile("./non-existent-file.yml")

  ####################################################################
  # Test that no path gives high-level content.
  def test_noPath(self):
    file = tempfile.NamedTemporaryFile("w+")
    file.write("""---
      data:
        list:
          - a
      """
    )
    file.flush()

    try:
      dataFile = DataFile(file.name)
    except Exception as ex:
      self.assertFalse(isinstance(ex, DataException))
      raise Exception("unexpected non-Data exception: {0}".format(ex))

    try:
      dataFile.content()["list"]
    except Exception as ex:
      self.assertFalse(isinstance(ex, KeyError),
                       "no path did not return expected content")
      raise Exception("unexpected exception: {0}".format(ex))

  ####################################################################
  # File that results in a non-dictionary in-memory representation.
  def test_notDictionary(self):
    file = tempfile.NamedTemporaryFile("w+")
    file.write("""---
      - data:
        global1: some-global-value
        global2: another-global-value

        # Group1 data:
        group1:
          default: group1-data
          subgroup1:
            default: subgroup1-data
            value1: value11
            value2: value12
          subgroup2:
            default: subgroup2-data
            value1: value21
            value2: value22

        # Group2 data:
        group2:
          default: group2-data
          subgroup1:
            default: subgroup1-data
            value1: value11
            value2: value12
          subgroup2:
            default: subgroup2-data
            value1: value21
            value2: value22
      """
    )
    file.flush()

    with self.assertRaises(DataFileFormatException):
      DataFile(file.name)

#############################################################################
#############################################################################
if __name__ == "__main__":
  unittest.main()
