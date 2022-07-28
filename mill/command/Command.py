#
# SPDX-License-Identifier: BSD-2-Clause
#
# Copyright Red Hat
#
from __future__ import print_function

import argparse
import sys

from mill import factory
from .CommandArgumentParser import (CommandArgumentParser,
                                    CommandNullArgumentParser)

########################################################################
class Command(factory.Factory):
  ####################################################################
  # Public factory-behavior methods
  ####################################################################

  ####################################################################
  # Public instance-behavior methods
  ####################################################################
  @property
  def isVerbose(self):
    # Is verbose enabled?
    return self.verbosity > 0

  ####################################################################
  @property
  def verbosity(self):
    # Is verbose enabled?
    return self.args.commandVerbosity

  ####################################################################
  def run(self):
    # Execute the command.
    raise NotImplementedError("COMMAND NOT IMPLEMENTED")

  ####################################################################
  # Overridden factory-behavior methods
  ####################################################################
  @classmethod
  def help(cls):
    return "execute command {0}".format(cls.name())

  ####################################################################
  @classmethod
  def _argumentParserClass(cls):
    return CommandArgumentParser

  ####################################################################
  # Overridden instance-behavior methods
  ####################################################################
  @classmethod
  def parserParents(cls):
    parser = argparse.ArgumentParser(add_help = False)

    parser.add_argument("--verbose", "-v",
                        help = "turn on/increase verbose mode",
                        dest = "commandVerbosity",
                        action = "count",
                        default = 0)

    parents = super(Command, cls).parserParents()
    parents.append(parser)
    return parents

  ####################################################################
  # Protected factory-behavior methods
  ####################################################################
  @classmethod
  def _nullArgumentParserClass(cls):
    return CommandNullArgumentParser

  ####################################################################
  # Protected instance-behavior methods
  ####################################################################

  ####################################################################
  # Private factory-behavior methods
  ####################################################################

  ####################################################################
  # Private instance-behavior methods
  ####################################################################
