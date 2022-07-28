#
# SPDX-License-Identifier: BSD-2-Clause
#
# Copyright Red Hat
#
import argparse
import os
from mill import factory

########################################################################
class CommandArgumentParser(factory.FactoryArgumentParser):
  """Argument parser for commands.
  """

  ####################################################################
  # Public methods
  ####################################################################

  ####################################################################
  # Overridden methods
  ####################################################################
  @classmethod
  def parserDestination(cls):
    return "command"

  ####################################################################
  @classmethod
  def parserTitle(cls):
    return "command specification"

  ####################################################################
  # Protected methods
  ####################################################################

  ####################################################################
  # Private methods
  ####################################################################

########################################################################
class CommandNullArgumentParser(factory.FactoryNullArgumentParser):
  """Argument parser for command line utilities which don't have subcommands.
  """
  pass
