#
# SPDX-License-Identifier: BSD-2-Clause
#
# Copyright Red Hat
#
import argparse
import logging
import os
import textwrap
import yaml

from mill import defaults
from .FactoryArgumentParser import (FactoryArgumentParser,
                                    FactoryNullArgumentParser)

# Default logging config.
logging.basicConfig(level = logging.INFO
                            if int(os.getenv("PYTHON_FACTORY_DEBUG", "0")) == 0
                            else logging.DEBUG)

log = logging.getLogger(__name__)

########################################################################
class _AttributeMixin(object):
  @classmethod
  def __init_subclass__(subclass, **kwargs):
    super().__init_subclass__(**kwargs)
    subclass.__mapping = None

  @classmethod
  def _getMapping(cls):
    return cls.__mapping

  @classmethod
  def _setMapping(cls, mapping):
    cls.__mapping = mapping

########################################################################
########################################################################
class Factory(_AttributeMixin, defaults.DefaultsFileInfo):
  """Factory for instantiating objects.
  """
  ####################################################################
  # Factory-behavior attributes.
  ####################################################################
  __mapping = None

  ####################################################################
  # Instance-behavior attributes.
  ####################################################################
  # If _available is not overridden as True the class will not be identified as
  # an available item.
  _available = False

  # By default the class's lowercased name will be used as the name of
  # the item.  This can be overridden by using _name.
  #
  # An overriding value of _name must be:
  #   - a string
  #   - an iterable that returns strings when used in a "for x in _name" loop
  #
  # Each potential name will be stripped of leading and trailing whitespace.
  # If a potential name contains embedded whitespace it will be skipped.
  # Duplicate names will be removed.
  #
  # If no potential name passes the above checks the default will be used.
  #
  # The resultant names must be unique (within the hierarchy of items you
  # are creating) and be composed of characters suitable for use as an argparse
  # choice value.
  _name = None

  ####################################################################
  # Public factory-behavior methods
  ####################################################################
  @classmethod
  def choices(cls, option = None):
    """'option' is a subclass-dependent parameter specifying what targets
    should be mapped.  This allows runtime usage of alternate mappings.

    A value of None indicates that the subclass's default mapping is to be
    used.
    """
    return sorted(cls._itemNames(option))

  ####################################################################
  @classmethod
  def defaultChoice(cls):
    choice = cls._defaultChoice()
    if (choice is not None) and (not cls._isItemAvailable(choice)):
      choice = None
    return choice

  ####################################################################
  @classmethod
  def makeItem(cls, itemName = None, args = None, option = None):
    """'option' is a subclass-dependent parameter specifying what targets
    should be mapped.  This allows runtime usage of alternate mappings.

    A value of None indicates that the subclass's default mapping is to be
    used.
    """
    haveChoices = len(cls.choices()) > 0
    if itemName is None:
      parser = cls._argumentParser()
      if args is None:
        args = parser.parse_args()
      if haveChoices:
        itemName = vars(args)[parser.parserDestination()]
      else:
        itemName = cls._rootClass().name()

    # Set debug level logging, if specified.
    if (args is not None) and args.factoryDebug:
      logging.basicConfig(level = logging.DEBUG, force = True)

    log.debug("instantiating item '{0}'{1}"
                .format(itemName,
                        "" if option is None
                           else " with mapping option '{0}'".format(option)))
    itemClass = (cls._item(itemName, option) if haveChoices
                                             else cls._rootClass())
    return itemClass(args)

  ####################################################################
  @classmethod
  def parserName(cls):
    return None

  ####################################################################
  @classmethod
  def parserEpilog(cls):
    epilog = []

    # Check for environmental overrides and, if they exist, generate
    # an epilog listing them and the resolved value of the default;
    # i.e., the value returned when querying for a default taking into
    # account all applicable overrides.
    varsAndValues = [
      f"    {k}: {v}" for (k, v) in cls.envVarsAndValues().items()
    ]
    if len(varsAndValues) > 0:
      epilog = ["Environment Variables and Resolved Defaults"]
      epilog.extend(sorted(varsAndValues))

    return os.linesep.join(epilog)

  ####################################################################
  # Public instance-behavior methods
  ####################################################################
  @classmethod
  def available(cls):
    return cls._available

  ####################################################################
  @classmethod
  def className(cls):
    return cls.__name__

  ####################################################################
  @classmethod
  def name(cls):
    return cls.names()[0]

  ####################################################################
  @classmethod
  def names(cls):
    names = cls._name
    if names is None:
      names = []
    if isinstance(names, str):
      names = [names]
    names = set([x.strip() for x in names if isinstance(x, str)])
    names = [x for x in names if not any(c.isspace() for c in x)]
    if len(names) == 0:
      names = [cls.className().lower()]
    return names

  ####################################################################
  @classmethod
  def help(cls):
    return "no special considerations"

  ####################################################################
  @classmethod
  def parserParents(cls):
    parser = argparse.ArgumentParser(add_help = False,
                                     epilog = cls.parserEpilog())
    parser.add_argument("--debug",
                        help = "turn on debugging mode",
                        dest = "factoryDebug",
                        action = "store_true")
    return [parser]

  ####################################################################
  @property
  def args(self):
    return self.__args

  ####################################################################
  @property
  def isDebug(self):
    # Is debugging enabled?
    isDebug = False if self.args is None else self.args.factoryDebug
    return isDebug

  ####################################################################
  # Overridden factory-behavior methods
  ####################################################################

  ####################################################################
  # Overridden instance-behavior methods
  ####################################################################
  def __init__(self, args):
    super(Factory, self).__init__()
    self.__args = args

  ####################################################################
  # Protected factory-behavior methods
  ####################################################################
  @classmethod
  def _argumentParser(cls):
    if len(cls.choices()) > 0:
      parser = cls._argumentParserClass()(set(cls._items()),
                                          prog = cls.parserName())
    else:
      parser = cls._nullArgumentParserClass()(cls._rootClass(),
                                              prog = cls.parserName())
    return parser

  ####################################################################
  @classmethod
  def _argumentParserClass(cls):
    return FactoryArgumentParser

  ####################################################################
  @classmethod
  def _defaultChoice(cls):
    return None

  ####################################################################
  @classmethod
  def _mapping(cls, option = None):
    """'option' is a subclass-dependent parameter specifying what targets
    should be mapped.  This allows runtime usage of alternate mappings.

    A value of None indicates that the subclass's default mapping is to be
    used.
    """
    if cls._getMapping() is None:
      # Available entities are identified by having a True availability.
      klasses = cls.__getClasses(cls._rootClass())

      mapping = []
      for klass in klasses:
        mapping.extend([(name, klass) for name in klass.names()])
      cls._setMapping(dict(mapping))

      log.debug("discovered instantiable items: {0}"
                  .format(', '.join(cls._getMapping().keys())))
    return cls._getMapping()

  ####################################################################
  @classmethod
  def _nullArgumentParserClass(cls):
    return FactoryNullArgumentParser

  ####################################################################
  @classmethod
  def _rootClass(cls):
    return cls

  ####################################################################
  # Protected factory-behavior methods
  ####################################################################
  @classmethod
  def _isItemAvailable(cls, name):
      available = False

      try:
        item = cls._item(name)
      except ValueError:
        pass
      else:
        available = item.available()

      return available

  ####################################################################
  @classmethod
  def _item(cls, name, option = None):
    """'option' is a subclass-dependent parameter specifying what targets
    should be mapped.  This allows runtime usage of alternate mappings.

    A value of None indicates that the subclass's default mapping is to be
    used.
    """
    try:
      item = cls._mapping(option)[name]
    except KeyError:
      raise ValueError("unknown {0} item specified: {1}".format(
                        cls.className(), name))
    return item

  ####################################################################
  @classmethod
  def _itemNames(cls, option = None):
    """'option' is a subclass-dependent parameter specifying what targets
    should be mapped.  This allows runtime usage of alternate mappings.

    A value of None indicates that the subclass's default mapping is to be
    used.
    """
    return cls._mapping(option).keys()

  ####################################################################
  @classmethod
  def _items(cls, option = None):
    """'option' is a subclass-dependent parameter specifying what targets
    should be mapped.  This allows runtime usage of alternate mappings.

    A value of None indicates that the subclass's default mapping is to be
    used.
    """
    return cls._mapping(option).values()

  ####################################################################
  # Private factory-behavior methods
  ####################################################################
  @classmethod
  def __getClasses(cls, klass):
    klasses = [] if not klass.available() else [klass]
    for subclass in klass.__subclasses__():
      klasses.extend(cls.__getClasses(subclass))
    return klasses

  ####################################################################
  # Private instance-behavior methods
  ####################################################################
