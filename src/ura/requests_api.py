"""This file contains the common api to access resources
"""
import requests
from requests.exceptions import ConnectionError, InvalidSchema
from urllib2 import URLError


def ls(url):
    """List all available resources at the given location

    Warnings: work only on directory like resources.

    Args:
        url: (urlparse.SplitResult) Resource locator

    Returns:
        (list of (Bool, url)): list of urls and flag set to True
                               if url is a directory like resource.
    """
    del url
    raise NotImplementedError


def exists(url):
    """Check the existence of a resource.

    Args:
        url: (urlparse.SplitResult) Resource locator

    Returns:
        (Bool): True if resource is accessible
    """
    try:
        resp = requests.get(url.geturl())
    except InvalidSchema as e:
        raise URLError(e)

    return resp.status_code < 400


def touch(url):
    """Create a resource.

    Used mostly to create file in a single unit of computation
    for locking systems.

    Args:
        url: (urlparse.SplitResult) Resource locator

    Returns:
        (Bool): operation has been successful
    """
    del url
    raise NotImplementedError


def remove(url):
    """Remove a resource.

    Warnings: recursive operation on directory like resources.

    Args:
        url: (urlparse.SplitResult) Resource locator

    Returns:
        (Bool): operation has been successful
    """
    del url
    raise NotImplementedError


def read(url, binary=False):
    """Read the content of a resource.

    Raises: IOError if resource is not accessible

    Args:
        url: (urlparse.SplitResult) Resource locator
        binary: (Bool) whether to open the resource as a binary file

    Returns:
        (string|ByteArray): content of the resource
    """
    try:
        resp = requests.get(url.geturl())
    except InvalidSchema as e:
        raise URLError(e)

    if resp.status_code >= 400:
        raise URLError("url does not exists")

    if binary:
        return resp.content
    else:
        return resp.text


def write(url, content, binary=False):
    """Write the content in a resource.

    Warnings: content must be some json data

    Raises: IOError if resource is not accessible

    Args:
        url: (urlparse.SplitResult) Resource locator
        content: (string|ByteArray) conte of the resource
        binary: (Bool) whether to write the resource as a binary file

    Returns:
        (None)
    """
    del binary
    try:
        ret = requests.post(url.geturl(), content,
                            headers={'content-type': 'application/json'})
        if ret.status_code > 400:
            raise URLError("unable to send data: %s" % ret.status_code)
    except (ConnectionError, InvalidSchema) as e:
        raise URLError(e)
