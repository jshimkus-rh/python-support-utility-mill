#! /usr/bin/env python
#
# SPDX-License-Identifier: BSD-2-Clause
#
# Copyright Red Hat
#

from __future__ import print_function

from mill import command

#############################################################################
#############################################################################
if __name__ == "__main__":
  command.CommandShell(command.Command).run()
