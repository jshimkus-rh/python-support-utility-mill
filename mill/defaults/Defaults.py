#
# SPDX-License-Identifier: BSD-2-Clause
#
# Copyright Red Hat
#
import copy
import inspect
import importlib.resources
import logging
import os

from mill import data

log = logging.getLogger(__name__)

######################################################################
######################################################################
class DefaultsException(Exception):

  ####################################################################
  # Overridden methods
  ####################################################################
  def __init__(self, msg, *args, **kwargs):
    super(DefaultsException, self).__init__(*args, **kwargs)
    self._msg = str(msg)

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
class Defaults(data.DataFile):
  ####################################################################
  # Public methods
  ####################################################################

  ####################################################################
  # Overridden public methods
  ####################################################################
  def content(self, path = None, sourceDictionary = None):
    try:
      return super(Defaults, self).content(path, sourceDictionary)
    except Exception as ex:
      raise self._translateException(ex)

  ####################################################################
  # Overridden protected methods
  ####################################################################
  @property
  def _toplevelLabel(self):
    return "defaults"

  ####################################################################
  def _loadData(self):
    try:
      return super(Defaults, self)._loadData()
    except Exception as ex:
      raise self._translateException(ex)

  ####################################################################
  # Protected methods
  ####################################################################
  def _translateException(self, exception):
    if isinstance(exception, data.DataException):
      translate = {
        data.DataException.__name__ :
          DefaultsException,
        data.DataFileContentMissingException.__name__ :
          DefaultsFileContentMissingException,
        data.DataFileDoesNotExistException.__name__ :
          DefaultsFileDoesNotExistException,
        data.DataFileException.__name__ :
          DefaultsFileException,
        data.DataFileFormatException.__name__ :
          DefaultsFileFormatException
      }

      try:
        exception = translate[type(exception).__name__](exception)
      except KeyError:
        raise DefaultsException(
                "could not translate exception: {0}".format(exception)
              )

    return exception

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

    # Establish a path string which may be needed more than once for logging
    # and exceptions.
    pathString = "<no path>" if path is None else "/".join(path)

    # Iterate over the defaults checking the user, if any, and the system
    # defaults (in that order) for each entry (in order) until we find the
    # value requested or exhaust the defaults.
    for defaults in cls._defaults():
      try:
        if defaults["user"] is None:
          raise DefaultsFileDoesNotExistException

        try:
          log.debug("querying defaults {0} for path: '{1}'"
                    .format(defaults["user"].path, pathString))
          userContent = defaults["user"].content(path)
          # User defaults may include only those entries that override system
          # defaults.  If the content is a dictionary (implying the user is
          # caching it) get the system defaults of the same path and return a
          # copy of that updated from the user defaults so the entirety of the
          # defaults are available in the cached copy.
          if isinstance(userContent, dict):
            try:
              systemContent = defaults["system"].content(path)
            except DefaultsException:
              log.exception(
                "exception accessing system defaults {0} for path: '{1}'"
                  .format(defaults["system"].path, pathString))
              raise RuntimeError(
                      "exception accessing user matching system defaults")
            userContent = cls._overridenCopy(systemContent, userContent)
          return userContent
        except  DefaultsFileContentMissingException:
          # No user override.  No need to log anything, but re-raise it to
          # look up the value in the system defaults.
          raise
        except DefaultsException as ex:
          # Log any other defaults exception as it is unexpected.
          log.debug("exception accessing path '{0}' in defaults {1}: {2}"
                      .format(pathString, defaults["user"].path, ex))
          raise
      except DefaultsException:
        log.debug("querying defaults {0} for path: '{1}'"
                  .format(defaults["system"].path, pathString))
        try:
          return defaults["system"].content(path)
        except  DefaultsFileContentMissingException:
          # No value.  Hopefully the next set of defaults will have it.
          pass
        except DefaultsException as ex:
          log.debug("exception accessing path '{0}' in defaults {1}: {2}"
                      .format(pathString, defaults["system"].path, ex))
    # We've exhausted all the defaults and didn't find the requested value.
    raise DefaultsFileContentMissingException(pathString)

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

  ####################################################################
  @classmethod
  def _overridenCopy(cls, base, update):
    """Returns a deep copy of the base dictionary recursively updated from the
    update dictionary.  Updates occur only on terminal values; i.e., no
    wholesale replacement of intermediate dictionaries.  Also, only
    pre-existing content in the base dictionary is updated; any "new" content
    in the update dictionary raises an exception.
    """
    def _do_override(base, update):
      for key in update:
        if key not in base:
          raise RuntimeError(
                  "adding content not supported; key: {0}".format(key))

        if ((base[key] is None) and (not isinstance(update[key], dict))):
          base[key] = update[key]
          continue

        if not isinstance(base[key], type(update[key])):
          raise TypeError("content type mismatch; key: {0}".format(key))

        if not isinstance(base[key], dict):
          base[key] = update[key]
          continue

        _do_override(base[key], update[key])
      return base

    return _do_override(copy.deepcopy(base), update)

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
