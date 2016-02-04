"""This file contains the common api to access resources
"""
import os
import shutil
from subprocess import check_output, CalledProcessError
from urllib2 import URLError
from urlparse import SplitResult

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
    res = check_output(["dirac-dms-find-lfns Path=%s" % root], shell=True)

    pths = {}

    for line in res.splitlines()[1:]:
        line = line.strip()
        if len(line) > 0:
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
    if url.path[-1] == "/":  # bad way of checking if it is a directory
        root, dname = os.path.split(url.path[:-1])
        root_url = SplitResult(url.scheme, url.netloc, root, url.query, url.fragment)
        return any(name == dname for name, isdir in ls(root_url))
    else:
        # res = open("d.json").read()#check_output(["dirac-dms-lfn-metadata %s" % url.path], shell=True)
        # i = res.index("Successful")
        # # failed = res[1:(i - 4)]
        # success = res[(i - 1):-2]
        # # print "failed", failed
        # # print "success", success
        # return len(success) > 16
        res = check_output(["dirac-dms-data-size %s" % url.path], shell=True)
        return not res.startswith("Failed")


def touch(url):
    """Create a resource.

    Used mostly to create file in a single unit of computation
    for locking systems.

    Warnings: will create temporarily a file with same name in
    current working directory.

    Args:
        url: (urlparse.SplitResult) Resource locator

    Returns:
        (Bool): operation has been successful
    """
    loc_file = os.path.basename(url.path)
    try:
        with open(loc_file, 'w') as f:
            # os.utime(url.path, None) # won't work on dirac, need to put some stuff in the file to upload it
            f.write("lorem ipsum")

        try:
            res = check_output(["dirac-dms-add-file %s %s DIRAC-USER" % (url.path, loc_file)], shell=True)
            lines = res.splitlines()
            return lines[-1].startswith("Successfully")
        except CalledProcessError:
            return False
        finally:
            os.remove(loc_file)
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
    if url.path[-1] == "/":  # bad way of checking if it is a directory
        raise NotImplementedError
    else:
        res = check_output(["dirac-dms-remove-files %s" % url.path], shell=True)
        return res.startswith("Successfully")


def read(url, binary=False):
    """Read the content of a resource.

    Raises: URLError if resource is not accessible

    Warnings: will create temporarily a file with same name in
    current working directory.

    Args:
        url: (urlparse.SplitResult) Resource locator
        binary: (Bool) whether to open the resource as a binary file

    Returns:
        (string|ByteArray): content of the resource
    """
    loc_pth = os.path.basename(url.path)
    try:
        res = check_output(["dirac-dms-get-file %s" % url.path], shell=True)
    except CalledProcessError as e:
        raise URLError(e)

    if res.startswith("ERROR Failed"):
        raise URLError("unable to fetch given resource")

    if binary:
        mode = 'rb'
    else:
        mode = 'r'

    try:
        with open(loc_pth, mode) as f:
            cnt = f.read()
            os.remove(loc_pth)
            return cnt
    except IOError as e:
        os.remove(loc_pth)
        raise URLError(e)


def write(url, content, binary=False):
    """Write the content in a resource.

    Raises: URLError if resource is not accessible

    Warnings: will create temporarily a file with same name in
    current working directory.

    Args:
        url: (urlparse.SplitResult) Resource locator
        content: (string|ByteArray) content of the resource
        binary: (Bool) whether to write the resource as a binary file

    Returns:
        (None)
    """
    loc_pth = os.path.basename(url.path)

    if binary:
        mode = 'wb'
    else:
        mode = 'w'

    try:
        with open(loc_pth, mode) as f:
            f.write(content)
    except IOError as e:
        raise URLError(e)

    try:
        if exists(url):
            remove(url)

        res = check_output(["dirac-dms-add-file %s %s DIRAC-USER" % (url.path, loc_pth)], shell=True)
        lines = res.splitlines()
        return lines[-1].startswith("Successfully")
    except CalledProcessError:
        return False
    finally:
        os.remove(loc_pth)
