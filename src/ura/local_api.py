"""This file contains the common api to access resources
"""
import os
import shutil
from urllib2 import URLError


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

    try:
        ret = []
        for name in os.listdir(root):
            pth = os.path.join(root, name)
            ret.append((pth.replace("\\", "/"), os.path.isdir(pth)))

        return ret
    except OSError as e:
        raise URLError(e)


def exists(url):
    """Check the existence of a resource.

    Args:
        url: (urlparse.SplitResult) Resource locator

    Returns:
        (Bool): True if resource is accessible
    """
    return os.path.exists(url.path)


def _ensure_dir(pth):
    """Recursively ensure that all dir in pth have been created

    Args:
        pth: (str)

    Returns:
        None
    """
    dpth = os.path.dirname(pth)
    if len(dpth) == 0:
        return

    if not os.path.exists(dpth):
        _ensure_dir(dpth)
        os.mkdir(dpth)


def touch(url):
    """Create a resource.

    Used mostly to create file in a single unit of computation
    for locking systems.

    Args:
        url: (urlparse.SplitResult) Resource locator

    Returns:
        (Bool): operation has been successful
    """
    _ensure_dir(url.path)
    with open(url.path, 'w'):
        os.utime(url.path, None)
    return True


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
    except OSError as e:
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
