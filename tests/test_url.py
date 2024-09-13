import unittest
from furl import furl

def clean_url(url):
    # Clean the URL by removing unnecessary query params, fragment, and other noise
    f = furl(url)
    f.args.clear()  # Remove query parameters
    f.fragment = ''  # Remove fragment
    return f.url

class TestUrlCleaning(unittest.TestCase):

    def test_basic_url(self):
        url = "https://example.com/path/to/page"
        expected_cleaned_url = "https://example.com/path/to/page"
        self.assertEqual(clean_url(url), expected_cleaned_url)

    def test_url_with_query_params(self):
        url = "https://example.com/path/to/page?foo=bar&baz=qux"
        expected_cleaned_url = "https://example.com/path/to/page"
        self.assertEqual(clean_url(url), expected_cleaned_url)

    def test_url_with_fragment(self):
        url = "https://example.com/path/to/page#section"
        expected_cleaned_url = "https://example.com/path/to/page"
        self.assertEqual(clean_url(url), expected_cleaned_url)

    def test_url_with_query_and_fragment(self):
        url = "https://example.com/path/to/page?foo=bar#section"
        expected_cleaned_url = "https://example.com/path/to/page"
        self.assertEqual(clean_url(url), expected_cleaned_url)

    def test_url_with_encoded_characters(self):
        url = "https://example.com/path/to/%E4%BE%8B%E5%AD%90"
        expected_cleaned_url = "https://example.com/path/to/%E4%BE%8B%E5%AD%90"
        self.assertEqual(clean_url(url), expected_cleaned_url)

if __name__ == '__main__':
    unittest.main()
