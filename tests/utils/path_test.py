# encoding: utf-8

from __future__ import unicode_literals

import glib
import os
import shutil
import sys
import tempfile

from mopidy.utils import path

from tests import unittest, path_to_data_dir


class GetOrCreateFolderTest(unittest.TestCase):
    def setUp(self):
        self.parent = tempfile.mkdtemp()

    def tearDown(self):
        if os.path.isdir(self.parent):
            shutil.rmtree(self.parent)

    def test_creating_folder(self):
        folder = os.path.join(self.parent, 'test')
        self.assert_(not os.path.exists(folder))
        self.assert_(not os.path.isdir(folder))
        created = path.get_or_create_folder(folder)
        self.assert_(os.path.exists(folder))
        self.assert_(os.path.isdir(folder))
        self.assertEqual(created, folder)

    def test_creating_nested_folders(self):
        level2_folder = os.path.join(self.parent, 'test')
        level3_folder = os.path.join(self.parent, 'test', 'test')
        self.assert_(not os.path.exists(level2_folder))
        self.assert_(not os.path.isdir(level2_folder))
        self.assert_(not os.path.exists(level3_folder))
        self.assert_(not os.path.isdir(level3_folder))
        created = path.get_or_create_folder(level3_folder)
        self.assert_(os.path.exists(level2_folder))
        self.assert_(os.path.isdir(level2_folder))
        self.assert_(os.path.exists(level3_folder))
        self.assert_(os.path.isdir(level3_folder))
        self.assertEqual(created, level3_folder)

    def test_creating_existing_folder(self):
        created = path.get_or_create_folder(self.parent)
        self.assert_(os.path.exists(self.parent))
        self.assert_(os.path.isdir(self.parent))
        self.assertEqual(created, self.parent)

    def test_create_folder_with_name_of_existing_file_throws_oserror(self):
        conflicting_file = os.path.join(self.parent, 'test')
        open(conflicting_file, 'w').close()
        folder = os.path.join(self.parent, 'test')
        self.assertRaises(OSError, path.get_or_create_folder, folder)


class PathToFileURITest(unittest.TestCase):
    def test_simple_path(self):
        if sys.platform == 'win32':
            result = path.path_to_uri('C:/WINDOWS/clock.avi')
            self.assertEqual(result, 'file:///C://WINDOWS/clock.avi')
        else:
            result = path.path_to_uri('/etc/fstab')
            self.assertEqual(result, 'file:///etc/fstab')

    def test_folder_and_path(self):
        if sys.platform == 'win32':
            result = path.path_to_uri('C:/WINDOWS/', 'clock.avi')
            self.assertEqual(result, 'file:///C://WINDOWS/clock.avi')
        else:
            result = path.path_to_uri('/etc', 'fstab')
            self.assertEqual(result, 'file:///etc/fstab')

    def test_space_in_path(self):
        if sys.platform == 'win32':
            result = path.path_to_uri('C:/test this')
            self.assertEqual(result, 'file:///C://test%20this')
        else:
            result = path.path_to_uri('/tmp/test this')
            self.assertEqual(result, 'file:///tmp/test%20this')

    def test_unicode_in_path(self):
        if sys.platform == 'win32':
            result = path.path_to_uri('C:/æøå')
            self.assertEqual(result, 'file:///C://%C3%A6%C3%B8%C3%A5')
        else:
            result = path.path_to_uri('/tmp/æøå')
            self.assertEqual(result, 'file:///tmp/%C3%A6%C3%B8%C3%A5')


class UriToPathTest(unittest.TestCase):
    def test_simple_uri(self):
        if sys.platform == 'win32':
            result = path.uri_to_path('file:///C://WINDOWS/clock.avi')
            self.assertEqual(result, 'C:/WINDOWS/clock.avi')
        else:
            result = path.uri_to_path('file:///etc/fstab')
            self.assertEqual(result, '/etc/fstab')

    def test_space_in_uri(self):
        if sys.platform == 'win32':
            result = path.uri_to_path('file:///C://test%20this')
            self.assertEqual(result, 'C:/test this')
        else:
            result = path.uri_to_path('file:///tmp/test%20this')
            self.assertEqual(result, '/tmp/test this')

    def test_unicode_in_uri(self):
        if sys.platform == 'win32':
            result = path.uri_to_path('file:///C://%C3%A6%C3%B8%C3%A5')
            self.assertEqual(result, 'C:/æøå')
        else:
            result = path.uri_to_path('file:///tmp/%C3%A6%C3%B8%C3%A5')
            self.assertEqual(result, '/tmp/æøå')


class SplitPathTest(unittest.TestCase):
    def test_empty_path(self):
        self.assertEqual([], path.split_path(''))

    def test_single_folder(self):
        self.assertEqual(['foo'], path.split_path('foo'))

    def test_folders(self):
        self.assertEqual(['foo', 'bar', 'baz'], path.split_path('foo/bar/baz'))

    def test_initial_slash_is_ignored(self):
        self.assertEqual(
            ['foo', 'bar', 'baz'], path.split_path('/foo/bar/baz'))

    def test_only_slash(self):
        self.assertEqual([], path.split_path('/'))


class ExpandPathTest(unittest.TestCase):
    # TODO: test via mocks?

    def test_empty_path(self):
        self.assertEqual(os.path.abspath('.'), path.expand_path(''))

    def test_absolute_path(self):
        self.assertEqual('/tmp/foo', path.expand_path('/tmp/foo'))

    def test_home_dir_expansion(self):
        self.assertEqual(
            os.path.expanduser('~/foo'), path.expand_path('~/foo'))

    def test_abspath(self):
        self.assertEqual(os.path.abspath('./foo'), path.expand_path('./foo'))

    def test_xdg_subsititution(self):
        self.assertEqual(
            glib.get_user_data_dir() + '/foo',
            path.expand_path('$XDG_DATA_DIR/foo'))

    def test_xdg_subsititution_unknown(self):
        self.assertEqual(
            '/tmp/$XDG_INVALID_DIR/foo',
            path.expand_path('/tmp/$XDG_INVALID_DIR/foo'))


class FindFilesTest(unittest.TestCase):
    def find(self, value):
        return list(path.find_files(path_to_data_dir(value)))

    def test_basic_folder(self):
        self.assert_(self.find(''))

    def test_nonexistant_folder(self):
        self.assertEqual(self.find('does-not-exist'), [])

    def test_file(self):
        files = self.find('blank.mp3')
        self.assertEqual(len(files), 1)
        self.assert_(files[0], path_to_data_dir('blank.mp3'))

    def test_names_are_unicode(self):
        is_unicode = lambda f: isinstance(f, unicode)
        for name in self.find(''):
            self.assert_(
                is_unicode(name), '%s is not unicode object' % repr(name))

    def test_ignores_hidden_folders(self):
        self.assertEqual(self.find('.hidden'), [])

    def test_ignores_hidden_files(self):
        self.assertEqual(self.find('.blank.mp3'), [])


class MtimeTest(unittest.TestCase):
    def tearDown(self):
        path.mtime.undo_fake()

    def test_mtime_of_current_dir(self):
        mtime_dir = int(os.stat('.').st_mtime)
        self.assertEqual(mtime_dir, path.mtime('.'))

    def test_fake_time_is_returned(self):
        path.mtime.set_fake_time(123456)
        self.assertEqual(path.mtime('.'), 123456)
