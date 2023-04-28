#! /usr/bin/env python
#
# SPDX-License-Identifier: BSD-2-Clause
#
# Copyright Red Hat
#

import yaml

from mill.data import (DataFile,
                       DataException,
                       DataFileContentMissingException,
                       DataFileDoesNotExistException,
                       DataFileFormatException)

#############################################################################
#############################################################################
if __name__ == "__main__":
  # Non-existent file.
  try:
    data = DataFile("./non-existent-file.yml")
  except DataFileDoesNotExistException:
    pass

  # File missing highest-level 'data'.
  try:
    data = DataFile("./bad-data-no-data-key.yml")
  except DataFileFormatException:
    pass

  # File that results in a non-dictionary in-memory representation.
  try:
    data = DataFile("./bad-data-non-dictionary.yml")
  except DataFileFormatException:
    pass

  # Correctly formatted data.
  data = DataFile("./example-data.yml")

  assert data.content(["global1"]) == "some-global-value"

  subgroup1 = data.content(["group1", "subgroup1"])
  assert subgroup1 is not None
  assert data.content(["value1"], subgroup1) == "value111"
  try:
    data.content(["non-existent-value"], subgroup1)
  except DataFileContentMissingException:
    pass

  assert data.content(["group2", "subgroup1", "value1"]) == "value211"
  try:
    data.content(["group2", "subgroup1", "non-existent-value"])
  except DataFileContentMissingException:
    pass

  # Data file with a list.
  data = DataFile("./data-containing-list.yml")
  assert isinstance(data.content(["list"]), list)

  # Test that no path gives high-level content.
  try:
    data.content()["list"]
  except KeyError:
    raise DataException("no path did not return expected content")

  # Successfully passed.
  print("success")
