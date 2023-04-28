#
# SPDX-License-Identifier: BSD-2-Clause
#
# Copyright Red Hat
#
import errno
import logging
import yaml

log = logging.getLogger(__name__)

######################################################################
######################################################################
class DataException(Exception):

  ####################################################################
  # Overridden methods
  ####################################################################
  def __init__(self, msg, *args, **kwargs):
    super(DataException, self).__init__(*args, **kwargs)
    self._msg = str(msg)

  ######################################################################
  def __str__(self):
    return self._msg

######################################################################
######################################################################
class DataFileException(DataException):

  ####################################################################
  # Overridden methods
  ####################################################################
  def __init__(self, msg = "error with file", *args, **kwargs):
    super(DataFileException, self).__init__(msg, *args, **kwargs)

######################################################################
######################################################################
class DataFileContentMissingException(DataFileException):

  ####################################################################
  # Overridden methods
  ####################################################################
  def __init__(self, missingContent, *args, **kwargs):
    super(DataFileContentMissingException, self).__init__(
      "'{0}' missing".format(missingContent), *args, **kwargs)

######################################################################
######################################################################
class DataFileDoesNotExistException(DataFileException):

  ####################################################################
  # Overridden methods
  ####################################################################
  def __init__(self, msg = "file does not exist", *args, **kwargs):
    super(DataFileDoesNotExistException, self).__init__(msg,
                                                            *args,
                                                            **kwargs)

######################################################################
######################################################################
class DataFileFormatException(DataFileException):

  ####################################################################
  # Overridden methods
  ####################################################################
  def __init__(self, msg = "file format invalid", *args, **kwargs):
    super(DataFileFormatException, self).__init__(msg, *args, **kwargs)

######################################################################
######################################################################
class DataFile(object):
  ####################################################################
  # Public methods
  ####################################################################
  @property
  def path(self):
    return self.__filePath

  ####################################################################
  def content(self, path = None, sourceDictionary = None):
    """Returns the specified content from the data file or the specified
    dictionary.

    The path argument is a list specifying the key path to the value of
    interest.  In the case of the data file (i.e., no specified dictionary)
    this excludes the highest level key of 'data'.

    The source dictionary argument is provided for specifying a dictionary
    extracted from the data (one of local processing interest) while
    operating on said dictionary with the same overall data content checks.
    Note that the path is local to the specified dictionary thus any exception
    generated which includes the path will also be local to the specified
    dictionary.

    Both the data file and any specified source dictionary are treated as a
    dictionary of dictionaries of arbitrary depth.
    """
    if path is None:
      path = []
    return self._content(sourceDictionary if sourceDictionary is not None
                                          else self._data,
                         path)

  ####################################################################
  # Overridden methods
  ####################################################################
  def __init__(self, filePath):
    super(DataFile, self).__init__()
    self.__filePath = filePath
    self.__data = self._loadData()

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
        raise DataFileContentMissingException(missing)
    return result

  ####################################################################
  @property
  def _data(self):
    return self.__data

  ####################################################################
  @property
  def _toplevelLabel(self):
    return "data"

  ####################################################################
  def _loadData(self):
    data = None
    try:
      with open(self.path) as f:
        data = yaml.safe_load(f)
        if not isinstance(data, dict):
          raise DataFileFormatException()
        try:
          data = self._content(data, [self._toplevelLabel])
        except DataFileContentMissingException:
          raise DataFileFormatException()
    except IOError as ex:
      if ex.errno != errno.ENOENT:
        raise
      raise DataFileDoesNotExistException()

    # Conceivably there could have been nothing but the top-level label
    # in the data file.  If that was the case we would have a value
    # for the data of None.  If so, set it to an empty dictionary.
    if data is None:
      data = {}

    return data

  ####################################################################
  # Private methods
  ####################################################################
