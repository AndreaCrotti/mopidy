from __future__ import unicode_literals

import mock

from mopidy.utils.encoding import locale_decode

from tests import unittest


@mock.patch('mopidy.utils.encoding.locale.getpreferredencoding')
class LocaleDecodeTest(unittest.TestCase):
    def test_can_decode_utf8_strings_with_french_content(self, mock):
        mock.return_value = 'UTF-8'

        result = locale_decode(
            b'[Errno 98] Adresse d\xc3\xa9j\xc3\xa0 utilis\xc3\xa9e')

        self.assertEquals('[Errno 98] Adresse d\xe9j\xe0 utilis\xe9e', result)

    def test_can_decode_an_ioerror_with_french_content(self, mock):
        mock.return_value = 'UTF-8'

        error = IOError(98, b'Adresse d\xc3\xa9j\xc3\xa0 utilis\xc3\xa9e')
        result = locale_decode(error)

        self.assertEquals('[Errno 98] Adresse d\xe9j\xe0 utilis\xe9e', result)

    def test_does_not_use_locale_to_decode_unicode_strings(self, mock):
        mock.return_value = 'UTF-8'

        locale_decode('abc')

        self.assertFalse(mock.called)

    def test_does_not_use_locale_to_decode_ascii_bytestrings(self, mock):
        mock.return_value = 'UTF-8'

        locale_decode('abc')

        self.assertFalse(mock.called)
