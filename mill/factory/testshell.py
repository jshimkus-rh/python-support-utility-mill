#! /usr/bin/env python
#
# SPDX-License-Identifier: BSD-2-Clause
#
# Copyright Red Hat
#

from __future__ import print_function

from mill import factory

#############################################################################
#############################################################################
if __name__ == "__main__":
  shell = factory.FactoryShell(factory.Factory)
  shell.printChoices()
  shell.run()
