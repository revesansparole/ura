"""This file contains the common api to access resources
"""
import os
import shutil
from subprocess import check_output
from urllib2 import URLError

"""
dirac-dms-add-file <LFN> <FILE> <SE>
dirac-dms-get-file <LFN>
dirac-dms-remove-files <LFN>
dirac-dms-clean-directory <LFN> <SE>

dirac-dms-catalog-metadata <LFN>
dirac-dms-lfn-metadata <LFN>
dirac-dms-find-lfns Path=/vo.france-grilles.fr/user/j/jchopard
"""


def ls(url):
    """List all available resources at the given location

    Warnings: work only on directory like resources.

    Args:
        url: (urlparse.SplitResult) Resource locator

    Returns:
        (list of (url, Bool)): list of urls and flag set to True
                               if url is a directory like resource.
    """
    root = url.path
    res = check_output(["dirac-dms-find-lfns", "Path=%s" % root], shell=True)

    pths = {}

    for line in res.splitlines()[1:]:
        line = line.strip()
        if len(line) > 0:
            print line
            if line.startswith(root):
                pth = line[len(root):][1:]
                dname = os.path.dirname(pth)
                if len(dname) > 0:
                    pths[dname] = True
                else:
                    pths[pth] = False
            else:
                raise URLError("bad path")

    return pths.items()


def exists(url):
    """Check the existence of a resource.

    Args:
        url: (urlparse.SplitResult) Resource locator

    Returns:
        (Bool): True if resource is accessible
    """
    return os.path.exists(url.path)


def touch(url):
    """Create a resource.

    Used mostly to create file in a single unit of computation
    for locking systems.

    Args:
        url: (urlparse.SplitResult) Resource locator

    Returns:
        (Bool): operation has been successful
    """
    try:
        with open(url.path, 'w'):
            os.utime(url.path, None)
    except IOError as e:
        raise URLError(e)


def remove(url):
    """Remove a resource.

    Warnings: recursive operation on directory like resources.

    Args:
        url: (urlparse.SplitResult) Resource locator

    Returns:
        (Bool): operation has been successful
    """
    try:
        if os.path.isdir(url.path):
            shutil.rmtree(url.path, ignore_errors=True)
        else:
            os.remove(url.path)
    except IOError as e:
        raise URLError(e)


def read(url, binary=False):
    """Read the content of a resource.

    Raises: URLError if resource is not accessible

    Args:
        url: (urlparse.SplitResult) Resource locator
        binary: (Bool) whether to open the resource as a binary file

    Returns:
        (string|ByteArray): content of the resource
    """
    if binary:
        mode = 'rb'
    else:
        mode = 'r'

    try:
        with open(url.path, mode) as f:
            return f.read()
    except IOError as e:
        raise URLError(e)


def write(url, content, binary=False):
    """Write the content in a resource.

    Raises: URLError if resource is not accessible

    Args:
        url: (urlparse.SplitResult) Resource locator
        content: (string|ByteArray) conte of the resource
        binary: (Bool) whether to write the resource as a binary file

    Returns:
        (None)
    """
    if binary:
        mode = 'wb'
    else:
        mode = 'w'

    try:
        with open(url.path, mode) as f:
            f.write(content)
    except IOError as e:
        raise URLError(e)
