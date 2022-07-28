#
# SPDX-License-Identifier: BSD-2-Clause
#
# Copyright Red Hat
#
import errno
import inspect
import importlib.resources
import logging
import os
import yaml

log = logging.getLogger(__name__)

######################################################################
######################################################################
class DefaultsException(Exception):

  ####################################################################
  # Overridden methods
  ####################################################################
  def __init__(self, msg, *args, **kwargs):
    super(DefaultsException, self).__init__(*args, **kwargs)
    self._msg = msg

  ######################################################################
  def __str__(self):
    return self._msg

######################################################################
######################################################################
class DefaultsFileException(DefaultsException):

  ####################################################################
  # Overridden methods
  ####################################################################
  def __init__(self, msg = "error with defaults file", *args, **kwargs):
    super(DefaultsFileException, self).__init__(msg, *args, **kwargs)

######################################################################
######################################################################
class DefaultsFileContentMissingException(DefaultsFileException):

  ####################################################################
  # Overridden methods
  ####################################################################
  def __init__(self, missingContent, *args, **kwargs):
    super(DefaultsFileContentMissingException, self).__init__(
      "'{0}' missing".format(missingContent), *args, **kwargs)

######################################################################
######################################################################
class DefaultsFileDoesNotExistException(DefaultsFileException):

  ####################################################################
  # Overridden methods
  ####################################################################
  def __init__(self, msg = "defaults file does not exist", *args, **kwargs):
    super(DefaultsFileDoesNotExistException, self).__init__(msg,
                                                            *args,
                                                            **kwargs)

######################################################################
######################################################################
class DefaultsFileFormatException(DefaultsFileException):

  ####################################################################
  # Overridden methods
  ####################################################################
  def __init__(self, msg = "defaults file format invalid", *args, **kwargs):
    super(DefaultsFileFormatException, self).__init__(msg, *args, **kwargs)

######################################################################
######################################################################
class Defaults(object):
  ####################################################################
  # Public methods
  ####################################################################
  @property
  def path(self):
    return self.__filePath

  ####################################################################
  def content(self, path = None, sourceDictionary = None):
    """Returns the specified content from the defaults file or the specified
    dictionary.

    The path argument is a list specifying the key path to the value of
    interest.  In the case of the defaults file (i.e., no specified dictionary)
    this excludes the highest level key of 'defaults'.

    The source dictionary argument is provided for specifying a dictionary
    extracted from the defaults (one of local processing interest) while
    operating on said dictionary with the same overall defaults content checks.
    Note that the path is local to the specified dictionary thus any exception
    generated which includes the path will also be local to the specified
    dictionary.

    Both the defaults file and any specified source dictionary are treated as a
    dictionary of dictionaries of arbitrary depth.
    """
    if path is None:
      path = []
    return self._content(sourceDictionary if sourceDictionary is not None
                                          else self._defaults,
                         path)

  ####################################################################
  # Overridden methods
  ####################################################################
  def __init__(self, filePath):
    super(Defaults, self).__init__()
    self.__filePath = filePath
    self.__defaults = self._loadDefaults()

  ####################################################################
  # Protected methods
  ####################################################################
  def _content(self, sourceDictionary, path):
    """Returns the specified content from the source dictionary.
    The source dictionary is a dictionary of dictionaries of arbitrary depth.
    The path argument is a list specifying the keyword path to the value
    of interest.
    """
    result = sourceDictionary
    missing = None
    for element in path:
      missing = element if missing is None else "/".join([missing, element])
      try:
        result = result[element]
      except KeyError:
        raise DefaultsFileContentMissingException(missing)
    return result

  ####################################################################
  @property
  def _defaults(self):
    return self.__defaults

  ####################################################################
  @property
  def _toplevelLabel(self):
    return "defaults"

  ####################################################################
  def _loadDefaults(self):
    defaults = None
    try:
      with open(self.path) as f:
        defaults = yaml.safe_load(f)
        if not isinstance(defaults, dict):
          raise DefaultsFileFormatException()
        try:
          defaults = self._content(defaults, [self._toplevelLabel])
        except DefaultsFileContentMissingException:
          raise DefaultsFileFormatException()
    except IOError as ex:
      if ex.errno != errno.ENOENT:
        raise
      raise DefaultsFileDoesNotExistException()

    # Conceivably there could have been nothing but the top-level label
    # in the defaults file.  If that was the case we would have a value
    # for the defaults of None.  If so, set it to an empty dictionary.
    if defaults is None:
      defaults = {}

    return defaults

  ####################################################################
  # Private methods
  ####################################################################

######################################################################
######################################################################
class DefaultsFileBaseMixin(object):
  """Base mixin used internally to provide info concerning a defaults file.
  This information is accessed using a Config instance based on the package
  config file (a config file being a specialized defaults file) which isolates
  any future modifications to the config file alone allowing both package
  installation and runtime execution to utilize the settings.
  """

  ####################################################################
  # Overridden methods
  ####################################################################
  @classmethod
  def __init_subclass__(subclass, **kwargs):
    super().__init_subclass__(**kwargs)
    subclass.__config = None

  ####################################################################
  # Protected methods
  ####################################################################
  @classmethod
  def _config(cls):
    if cls.__config is None:
      cls.__config = Config(cls)
    return cls.__config

  ####################################################################
  @classmethod
  def _fileDirectory(cls):
    """Returns the directory in which the defaults file is to be installed.
    If there is no installation directory this indicates that the defaults
    is installed as package data.
    """
    return cls._config().content(["defaults", "install-dir"])

  ####################################################################
  @classmethod
  def _fileInPackage(cls):
    return cls._fileDirectory() is None

  ####################################################################
  @classmethod
  def _fileName(cls):
    """Returns the name of the defaults file.  If there is no name then
    a defaults file is not used.
    """
    return cls._config().content(["defaults", "name"])

  ####################################################################
  @classmethod
  def _filePackage(cls):
    return inspect.getmodule(cls).__package__

  ####################################################################
  @classmethod
  def _filePath(cls):
    # If the defaults file is in the package the assumption is that the
    # defaults file is located in the installed package location and we
    # query the package for the location.
    path = None

    if cls._fileName() is not None:
      if cls._fileInPackage():
        path = cls._findFile(cls._filePackage(), cls._fileName())
      else:
        path = os.path.join(cls._fileDirectory(), cls._fileName())

    return path

  ####################################################################
  @classmethod
  def _findFile(cls, package, fileName):
    # The class seeking to access the defaults could be arbitrarily deep
    # in the class hierarchy.  We work our way up from the package the class
    # is in until we find the defaults or exhaust the hierarchy.
    while True:
      try:
        # We use importlib.resources.path to get the file path.
        # However with python310 this gives us the path *as if* the file
        # exists; that is, it doesn't raise the FileNotFoundError of pre-310.
        # Thus, after getting the path, we include a check that the resource
        # actually exists and if not raise FileNotFoundError ourself.
        with importlib.resources.path(package, fileName) as f:
          path = str(f)
          if not importlib.resources.is_resource(package, fileName):
            raise FileNotFoundError(path)
          break
      except FileNotFoundError:
        split = package.rsplit(".", 1)
        if len(split) == 1:
          # That was our last chance.
          raise
        package = split[0]

    return path

######################################################################
######################################################################
class DefaultsFileInfo(DefaultsFileBaseMixin):
  """Mixin that classes which use Defaults can inherit to provide access to
  their defaults.
  """

  ####################################################################
  # Public methods
  ####################################################################
  @classmethod
  def defaults(cls, path = None, sourceDictionary = None):
    # We allow that there is no backing defaults in which case the response
    # is None.
    if len(cls._defaults()) == 0:
      return None

    # If using a specified dictionary we only need the processing mechanics
    # not a particular defaults.
    # Any extant entry always has a system defaults; simply use the first one.
    if sourceDictionary is not None:
      return cls._defaults()[0]["system"].content(path, sourceDictionary)

    # Iterate over the defaults checking the user, if any, and the system
    # defaults (in that order) for each entry (in order) until we find the
    # value requested or exhaust the defaults.
    for defaults in cls._defaults():
      try:
        if defaults["user"] is None:
          raise DefaultsFileDoesNotExistException

        try:
          return defaults["user"].content(path)
        except  DefaultsFileContentMissingException:
          # No user override.  No need to log anything, but re-raise it to
          # look up the value in the system defaults.
          raise
        except DefaultsException as ex:
          # Log any other defaults exception as it is unexpected.
          log.debug("exception accessing path '{0}' in defaults {1}: {2}"
                      .format("<no path>" if path is None else "/".join(path),
                              defaults["user"].path,
                              ex))
          raise
      except DefaultsException:
        log.debug("querying defaults {0} for path: '{1}'"
                  .format(defaults["system"].path,
                          "<no path>" if path is None else "/".join(path)))
        try:
          return defaults["system"].content(path)
        except  DefaultsFileContentMissingException:
          # No value.  Hopefully the next set of defaults will have it.
          pass
        except DefaultsException as ex:
          log.debug("exception accessing path '{0}' in defaults {1}: {2}"
                      .format("<no path>" if path is None else "/".join(path),
                              defaults["system"].path,
                              ex))
    # We've exhausted all the defaults and didn't find the requested value.
    raise DefaultsFileContentMissingException("<no path>" if path is None
                                                          else "/".join(path))

  ####################################################################
  # Overridden methods
  ####################################################################
  @classmethod
  def __init_subclass__(subclass, **kwargs):
    super().__init_subclass__(**kwargs)
    # Get the unique (by package), in-order classes from the subclass's MRO.
    classes = []
    packages = []
    for klass in subclass.mro():
      if klass is object:
        continue
      package = inspect.getmodule(klass).__package__
      if (package not in packages) and issubclass(klass, DefaultsFileInfo):
        packages.append(package)
        classes.append(klass)

    # Construct the in-order system and user defaults from each class.
    subclass.__defaults = []
    for klass in classes:
      path = klass._filePath()
      if path is not None:
        system = Defaults(path)
        user = None
        try:
          user = Defaults(os.path.join(os.environ["HOME"],
                                       ".{0}".format(klass._fileName())))
        except DefaultsFileDoesNotExistException:
          pass
        except DefaultsException as ex:
          log.warn("exception instantiating user defaults: {0}".format(ex))
          log.warn("using global defaults solely")

        subclass.__defaults.append({"system": system, "user": user})

  ####################################################################
  # Protected methods
  ####################################################################
  @classmethod
  def _defaults(cls):
    return cls.__defaults

######################################################################
######################################################################
class Config(Defaults, DefaultsFileBaseMixin):
  """Special case of Defaults used for runtime determination of defaults
  file location.
  The config file is always installed as part of the package.
  """
  ####################################################################
  # Overridden methods
  ####################################################################
  def __init__(self, targetClass):
    super(Config, self).__init__(self._filePath(targetClass))

  ####################################################################
  @property
  def _toplevelLabel(self):
    return "config"

  ####################################################################
  @classmethod
  def _fileDirectory(cls):
    return None

  ####################################################################
  @classmethod
  def _fileName(cls):
    return "config.yml"

  ####################################################################
  @classmethod
  def _filePath(cls, targetClass):
    return cls._findFile(targetClass._filePackage(), cls._fileName())
