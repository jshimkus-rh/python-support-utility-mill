#
# SPDX-License-Identifier: BSD-2-Clause
#
# Copyright Red Hat
#
import argparse
import os
import platform

########################################################################
class FactoryArgumentParser(argparse.ArgumentParser):
  """Argument parser for factory items.
  """

  ####################################################################
  # Public methods
  ####################################################################
  @classmethod
  def parserDestination(cls):
    return "selection"

  ####################################################################
  @classmethod
  def parserHelp(cls):
    return "description"

  ####################################################################
  @classmethod
  def parserMetaVar(cls):
    return cls.parserDestination()

  ####################################################################
  @classmethod
  def parserTitle(cls):
    return "factory item specification"

  ####################################################################
  # Overridden methods
  ####################################################################
  def __init__(self, factoryItems, **kwargs):
    super(FactoryArgumentParser, self).__init__(**kwargs)

    (major, minor, patch) = map(lambda x: int(x),
                                platform.python_version_tuple())
    if (major < 3) or ((major == 3) and (minor < 7)):
      parserAdder = self.add_subparsers(
                                title = self.parserTitle(),
                                help = self.parserHelp(),
                                dest = self.parserDestination(),
                                metavar = self.parserMetaVar(),
                                parser_class = argparse.ArgumentParser)
    else:
      parserAdder = self.add_subparsers(
                                title = self.parserTitle(),
                                help = self.parserHelp(),
                                dest = self.parserDestination(),
                                metavar = self.parserMetaVar(),
                                parser_class = argparse.ArgumentParser,
                                required = True)

    # Add a subparser for each command.
    for item in factoryItems:
      parents = item.parserParents()
      epilog = os.linesep.join([parser.epilog for parser in parents
                                              if parser.epilog is not None])
      for name in item.names():
        parserAdder.add_parser(name,
                               formatter_class
                                = argparse.RawDescriptionHelpFormatter,
                               parents = parents,
                               help = item.help(),
                               epilog = epilog)

  ####################################################################
  # Protected methods
  ####################################################################

  ####################################################################
  # Private methods
  ####################################################################

########################################################################
class FactoryNullArgumentParser(argparse.ArgumentParser):
  """Argument parser for factories with no choices.
  """
  ####################################################################
  # Overridden methods
  ####################################################################
  def __init__(self, factoryItemClass, **kwargs):
    parents = factoryItemClass.parserParents()
    description = os.linesep.join([parser.description for parser in parents
                                            if parser.description is not None])
    epilog = os.linesep.join([parser.epilog for parser in parents
                                            if parser.epilog is not None])
    super(FactoryNullArgumentParser, self).__init__(
                      formatter_class = argparse.RawDescriptionHelpFormatter,
                      description = description,
                      epilog = epilog,
                      parents = parents,
                      **kwargs)
