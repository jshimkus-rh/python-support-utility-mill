#
# SPDX-License-Identifier: BSD-2-Clause
#
# Copyright Red Hat
#
from __future__ import print_function

from mill import factory

########################################################################
class CommandShell(factory.FactoryShell):
  """Base class for command.
  """
  ####################################################################
  # Public methods
  ####################################################################
  def run(self):
    command = super(CommandShell, self).run()
    result = None
    try:
      result = command.run()
    except Exception as ex:
      if command.isDebug:
        raise ex
      print(ex)
    return result

  ####################################################################
  # Overridden methods
  ####################################################################

  ####################################################################
  # Protected methods
  ####################################################################

  ####################################################################
  # Private methods
  ####################################################################
