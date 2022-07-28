#
# SPDX-License-Identifier: BSD-2-Clause
#
# Copyright Red Hat
#
########################################################################
class FactoryShell(object):
  """Base class for instantiation.
  """
  ####################################################################
  # Public methods
  ####################################################################
  def printChoices(self):
   print("Choices: {0}".format(", ".join(self.__factoryClass.choices())))

  ####################################################################
  def run(self):
    return self.__factoryClass.makeItem()

  ####################################################################
  # Overridden methods
  ####################################################################
  def __init__(self, factoryClass):
    super(FactoryShell, self).__init__()
    self.__factoryClass = factoryClass

  ####################################################################
  # Protected methods
  ####################################################################

  ####################################################################
  # Private methods
  ####################################################################
