from nose.tools import assert_raises
from shutil import rmtree
from urlparse import urlsplit

from ura.local_api import exists, ls, touch, read, remove, URLError, write


def test_ls_raise_error_if_pth_not_exists():
    url = urlsplit("takapouet")
    assert_raises(URLError, lambda: ls(url))


def test_ls_list_all_elms_in_dir():
    url = urlsplit("test/toto")
    elms = ls(url)
    assert len(elms) == 2
    assert ("test/toto/sub", True) in elms
    assert ("test/toto/doofus.txt", False) in elms

    url = urlsplit("test/toto/sub")
    elms = ls(url)
    assert len(elms) == 2
    assert ("test/toto/sub/doofus.txt", False) in elms
    assert ("test/toto/sub/subdoofus.txt", False) in elms


def test_ls_do_not_list_subdirs():
    url = urlsplit("test/toto")
    elms = ls(url)
    assert ("test/toto/sub/doofus.txt", False) not in elms
    assert ("test/toto/sub/subdoofus.txt", False) not in elms


def test_ls_accept_trailing_slashes():
    url = urlsplit("test/toto")
    elms1 = ls(url)
    url = urlsplit("test/toto/")
    elms2 = ls(url)

    assert set(elms1) == set(elms2)


def test_exists_do_not_raise_error_if_file_does_not_exists():
    url = urlsplit("takapouet")
    assert not exists(url)


def test_exists_return_true_for_existing_file():
    for pth in ("setup.py", "test/toto/doofus.txt", "test/toto/sub/doofus.txt"):
        url = urlsplit(pth)
        assert exists(url)


def test_exists_return_true_for_existing_directory():
    for pth in ("test", "test/toto", "test/toto/sub"):
        url = urlsplit(pth)
        assert exists(url)


def test_exists_do_not_care_about_trailing_slashes():
    for pth in ("test", "test/"):
        url = urlsplit(pth)
        assert exists(url)


# def test_touch_returns_false_if_pth_is_faulty():
#     url = urlsplit("/takapouet/touch.txt")
#     assert not touch(url)


def test_touch_do_not_raise_error_if_dir_part_of_pth_do_not_exist():
    url = urlsplit("takapouet/touch.txt")
    assert touch(url)
    assert exists(urlsplit("takapouet"))
    assert exists(urlsplit("takapouet/"))
    assert exists(url)
    rmtree("takapouet")


def test_touch_create_file():
    url = urlsplit("test/toto/touch.txt")
    assert not exists(url)
    touch(url)
    assert exists(url)
    remove(url)
    assert not exists(url)


def test_touch_overwrite_existing_file():
    url = urlsplit("test/toto/touch.txt")
    assert not exists(url)
    touch(url)
    assert exists(url)
    touch(url)
    assert exists(url)
    remove(url)
    assert not exists(url)


def test_remove_raise_error_if_pth_do_not_exist():
    url = urlsplit("takapouet")
    assert_raises(URLError, lambda: remove(url))
    url = urlsplit("takapouet/touch.txt")
    assert_raises(URLError, lambda: remove(url))


def test_remove_remove_file():
    url = urlsplit("test/tugudu/touch.txt")
    assert not exists(url)
    touch(url)
    assert exists(url)
    remove(url)
    assert not exists(url)


def test_remove_dir_remove_all_tree():
    url = urlsplit("test/tugudu/touch.txt")
    assert not exists(url)
    touch(url)
    assert exists(url)
    remove(urlsplit("test/tugudu"))
    assert not exists(urlsplit("test/tugudu"))
    assert not exists(url)


def test_read_raises_error_if_file_do_not_exists():
    url = urlsplit("test/tugudu/touch.txt")
    assert_raises(URLError, lambda: read(url))


def test_read_returns_file_content():
    url = urlsplit("test/toto/doofus.txt")
    txt = read(url)
    assert txt.strip() == "lorem ipsum"

    cnt = read(url, binary=True)
    assert cnt.strip() == "lorem ipsum"


def test_write_raises_error_if_dir_pth_do_not_exists():
    url = urlsplit("test/tugudu/touch.txt")
    assert_raises(URLError, lambda: write(url, "toto was here"))


def test_write_content_create_file_if_needed():
    url = urlsplit("test/toto/testwrite.txt")
    assert not exists(url)
    write(url, "toto was here")
    assert exists(url)
    assert read(url) == "toto was here"
    remove(url)


def test_write_binary_content():
    url = urlsplit("test/toto/testwrite.txt")
    assert not exists(url)
    write(url, "toto was here", binary=True)
    assert exists(url)
    assert read(url, binary=True) == "toto was here"
    remove(url)

