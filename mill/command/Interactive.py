#
# SPDX-License-Identifier: BSD-2-Clause
#
# Copyright Red Hat
#
import argparse
import cmd
import shlex

from .Command import Command
from .CommandArgumentParser import (CommandArgumentParser,
                                    CommandNullArgumentParser)

########################################################################
########################################################################
class InteractiveCommand(Command):
  """The basal class for commands used in a command loop.
  """
  ####################################################################
  # Public factory-behavior methods
  ####################################################################

  ####################################################################
  # Public instance-behavior methods
  ####################################################################

  ####################################################################
  # Overridden class-behavior methods
  ####################################################################
  @classmethod
  def help(cls):
    return "interactive command: {0}".format(cls.name())

  ####################################################################
  @classmethod
  def makeCommandItem(cls, commandLine = None):
    args = (None if commandLine is None
                 else cls._argumentParser().parse_args(shlex.split(commandLine)))
    return super(InteractiveCommand, cls).makeItem(args = args)

  ####################################################################
  @classmethod
  def _argumentParserClass(cls):
    return InteractiveCommandArgumentParser

  ####################################################################
  @classmethod
  def _nullArgumentParserClass(cls):
    return InteractiveCommandNullArgumentParser

  ####################################################################
  # Overridden instance-behavior methods
  ####################################################################
  def run(self, arg = None):
    super(InteractiveCommand, self).run()

  ####################################################################
  # Protected factory-behavior methods
  ####################################################################

  ####################################################################
  # Protected instance-behavior methods
  ####################################################################

  ####################################################################
  # Private factory-behavior methods
  ####################################################################

  ####################################################################
  # Private instance-behavior methods
  ####################################################################

########################################################################
########################################################################
class InteractiveInterface(cmd.Cmd):
  ####################################################################
  # Overridden instance-behavior methods
  ####################################################################
  def default(self, line):
    if line == "EOF":
      raise EOFError

    return self.__loop.makeCommandItemAndRun(line)

  ####################################################################
  def do_help(self, arg):
    return self.__loop.makeCommandItemAndRun("{0} --help".format(arg))

  ####################################################################
  def emptyline(self):
    pass

  ####################################################################
  def __init__(self, loop, prompt, **kwargs):
    super(InteractiveInterface, self).__init__(**kwargs)
    self.__loop = loop
    self.prompt = prompt

########################################################################
########################################################################
class InteractiveInterfaceQuit(InteractiveInterface):
  ####################################################################
  # Overridden instance-behavior methods
  ####################################################################
  def do_help(self, arg):
    if (arg != "") and (shlex.split(arg)[0] == "quit"):
      self.help_quit()
    else:
      super(InteractiveInterfaceQuit, self).do_help(arg)

  ####################################################################
  def do_quit(self, arg):
    raise StopIteration

  ####################################################################
  def help_quit(self):
    print("quit: exits back to the shell regardless of depth within command"
          " hierarchy")

########################################################################
########################################################################
class InteractiveLoop(InteractiveCommand):
  """A Command class which operates as a loop possing its own Command
  hierarchy.
  """
  ####################################################################
  # Public instance-behavior methods
  ####################################################################
  def makeCommandItemAndRun(self, commandLine = None):
    return self.makeCommandItem(commandLine).run()

  ####################################################################
  # Overridden class-behavior methods
  ####################################################################
  @classmethod
  def help(cls):
    return "interactive command loop"

  ####################################################################
  @classmethod
  def makeCommandItem(cls, commandLine = None):
    return cls._commandRootClass().makeCommandItem(commandLine)

  ####################################################################
  # Overridden instance-behavior methods
  ####################################################################
  def run(self, arg = None):
    self._preLoop(arg)

    # Establish the user interface.
    userInterface = self._interfaceClass(self,
                                         "{0} > "
                                          .format(self._loopName))

    # Execute the loop.
    try:
      while True:
        try:
          userInterface.cmdloop()
        except StopIteration:
          # User requested quit.
          raise
        except EOFError:
          # User requested end of this loop.
          print("\n")
          break
        except SystemExit:
          # Raised by argument parser.
          pass
        except Exception as ex:
          print(ex)
    finally:
      self._postLoop()

  ####################################################################
  # Protected class-behavior methods
  ####################################################################
  @classmethod
  def _commandRootClass(cls):
    raise NotImplementedError("SPECIFY ROOT OF INTERACTIVE COMMANDS")

  ####################################################################
  # Protected instance-behavior methods
  ####################################################################
  @property
  def _interfaceClass(self):
    return InteractiveInterfaceQuit

  ####################################################################
  @property
  def _loopName(self):
    return self.name()

  ####################################################################
  def _postLoop(self):
    return

  ####################################################################
  def _preLoop(self, arg):
    pass

########################################################################
########################################################################
class _NonExitingArgumentParser(argparse.ArgumentParser):
  ####################################################################
  # Overridden instance-behavior methods
  ####################################################################
  def exit(self, status = 0, message = None):
    # Intercept exit.
    # Print the message, if any.
    # Raise SystemExit to trap on.
    if message is not None:
      print(message)
    raise SystemExit

########################################################################
########################################################################
class InteractiveCommandArgumentParser(CommandArgumentParser,
                                       _NonExitingArgumentParser):
  """Argument parser for interactive commands.
  """
  pass

########################################################################
########################################################################
class InteractiveCommandNullArgumentParser(CommandNullArgumentParser,
                                           _NonExitingArgumentParser):
  """Null argument parser for interactive commands.
  """
  pass
