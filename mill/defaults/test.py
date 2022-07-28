#! /usr/bin/env python
#
# SPDX-License-Identifier: BSD-2-Clause
#
# Copyright Red Hat
#

from __future__ import print_function

import yaml

from mill.defaults import (Defaults,
                           DefaultsException,
                           DefaultsFileContentMissingException,
                           DefaultsFileDoesNotExistException,
                           DefaultsFileFormatException)

#############################################################################
#############################################################################
if __name__ == "__main__":
  # Non-existent file.
  try:
    defaults = Defaults("./non-existent-file.yml")
  except DefaultsFileDoesNotExistException:
    pass

  # File missing highest-level 'defaults'.
  try:
    defaults = Defaults("./bad-defaults-no-defaults-key.yml")
  except DefaultsFileFormatException:
    pass

  # File that results in a non-dictionary in-memory representation.
  try:
    defaults = Defaults("./bad-defaults-non-dictionary.yml")
  except DefaultsFileFormatException:
    pass

  # Correctly formatted defaults.
  defaults = Defaults("./example-defaults.yml")

  assert defaults.content(["global1"]) == "some-global-value"

  subgroup1 = defaults.content(["group1", "subgroup1"])
  assert subgroup1 is not None
  assert defaults.content(["value1"], subgroup1) == "value111"
  try:
    defaults.content(["non-existent-value"], subgroup1)
  except DefaultsFileContentMissingException:
    pass

  assert defaults.content(["group2", "subgroup1", "value1"]) == "value211"
  try:
    defaults.content(["group2", "subgroup1", "non-existent-value"])
  except DefaultsFileContentMissingException:
    pass

  # Defaults file with a list.
  defaults = Defaults("./defaults-containing-list.yml")
  assert isinstance(defaults.content(["list"]), list)

  # Test that no path gives high-level content.
  try:
    defaults.content()["list"]
  except KeyError:
    raise DefaultsException("no path did not return expected content")

  # Successfully passed.
  print("success")
