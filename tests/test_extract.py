import unittest
from unittest.mock import patch, MagicMock

from bs4 import BeautifulSoup

from utils.extract import scrape_product, fetching_content, extract_product_data


class TestFetchingContent(unittest.TestCase):
    @patch('utils.extract.requests.Session')
    def test_fetching_content_success(self, mock_session_cls):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.content = b"<html>ok</html>"
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response
        mock_session_cls.return_value = mock_session

        result = fetching_content("https://example.com")

        self.assertEqual(result, b"<html>ok</html>")

        mock_session.get.assert_called_once()

    @patch('utils.extract.requests.Session')
    def test_fetching_content_request_exception(self, mock_session_cls):
        import requests
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.RequestException("error")
        mock_session.get.return_value = mock_response
        mock_session_cls.return_value = mock_session

        with patch('builtins.print') as mock_print:
            result = fetching_content("https://example.com")

        self.assertIsNone(result)

        mock_print.assert_called_once()


class TestExtractProductData(unittest.TestCase):
    def test_extract_product_data_complete(self):
        html = """
            <div class="collection-card">
                <h3 class="product-title">T-shirt 2</h3>
                <div class="price-container"><span class="price">$102.15</span></div>
                <p style="font-size: 14px; color: #777;">Rating: ⭐ 3.9 / 5</p>
                <p style="font-size: 14px; color: #777;">3 Colors</p>
                <p style="font-size: 14px; color: #777;">Size: M</p>
                <p style="font-size: 14px; color: #777;">Gender: Women</p>
            </div>
        """
        card = BeautifulSoup(html, "html.parser").find('div', class_='collection-card')
        result = extract_product_data(card)

        self.assertEqual(result['title'], 'T-shirt 2')
        self.assertEqual(result['price'], '$102.15')
        self.assertEqual(result['rating'], 'Rating: ⭐ 3.9 / 5')
        self.assertEqual(result['colors'], '3 Colors')
        self.assertEqual(result['size'], 'Size: M')
        self.assertEqual(result['gender'], 'Gender: Women')

    def test_extract_product_data_missing_fields(self):
        html = '<div class="collection-card"></div>'
        card = BeautifulSoup(html, "html.parser").find('div', class_='collection-card')
        result = extract_product_data(card)

        self.assertEqual(result['title'], 'Unknown Title')
        self.assertEqual(result['price'], 'Price Not Available')
        self.assertEqual(result['rating'], 'No Rating')
        self.assertEqual(result['colors'], 'No Color Info')
        self.assertEqual(result['size'], 'No Size Info')
        self.assertEqual(result['gender'], 'No Gender Info')


class TestScrapeProduct(unittest.TestCase):
    @patch('utils.extract.time.sleep')
    @patch('utils.extract.fetching_content')
    def test_scrape_product_single_page_no_next(self, mock_fetch, mock_sleep):
        html = """
            <div class="collection-card">
                <h3 class="product-title">T-shirt 2</h3>
                <div class="price-container"><span class="price">$102.15</span></div>
                <p style="font-size: 14px; color: #777;">Rating: ⭐ 3.9 / 5</p>
                <p style="font-size: 14px; color: #777;">3 Colors</p>
                <p style="font-size: 14px; color: #777;">Size: M</p>
                <p style="font-size: 14px; color: #777;">Gender: Women</p>
            </div>
        """
        mock_fetch.return_value = html

        result = scrape_product("https://fashion-studio.dicoding.dev")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['title'], 'T-shirt 2')

        mock_fetch.assert_called_once()
        mock_sleep.assert_not_called()

    @patch('utils.extract.time.sleep')
    @patch('utils.extract.fetching_content')
    def test_scrape_product_multiple_pages_with_next(self, mock_fetch, mock_sleep):
        page1 = """
            <div class="collection-card">
                <h3 class="product-title">T-shirt 2</h3>
                <div class="price-container"><span class="price">$102.15</span></div>
                <p style="font-size: 14px; color: #777;">Rating: ⭐ 3.9 / 5</p>
                <p style="font-size: 14px; color: #777;">3 Colors</p>
                <p style="font-size: 14px; color: #777;">Size: M</p>
                <p style="font-size: 14px; color: #777;">Gender: Women</p>
            </div>
            <li class="next"><a href="#">Next</a></li>
        """
        page2 = """
            <div class="collection-card">
                <h3 class="product-title">Hoodie 3</h3>
                <div class="price-container"><span class="price">$496.88</span></div>
                <p style="font-size: 14px; color: #777;">Rating: ⭐ 4.8 / 5</p>
                <p style="font-size: 14px; color: #777;">3 Colors</p>
                <p style="font-size: 14px; color: #777;">Size: L</p>
                <p style="font-size: 14px; color: #777;">Gender: Unisex</p>
            </div>
        """
        mock_fetch.side_effect = [page1, page2]

        result = scrape_product("https://fashion-studio.dicoding.dev")

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['title'], 'T-shirt 2')
        self.assertEqual(result[0]['price'], '$102.15')
        self.assertEqual(result[0]['rating'], 'Rating: ⭐ 3.9 / 5')
        self.assertEqual(result[0]['colors'], '3 Colors')
        self.assertEqual(result[0]['size'], 'Size: M')
        self.assertEqual(result[0]['gender'], 'Gender: Women')
        self.assertEqual(result[1]['title'], 'Hoodie 3')
        self.assertEqual(result[1]['price'], '$496.88')
        self.assertEqual(result[1]['rating'], 'Rating: ⭐ 4.8 / 5')
        self.assertEqual(result[1]['colors'], '3 Colors')
        self.assertEqual(result[1]['size'], 'Size: L')
        self.assertEqual(result[1]['gender'], 'Gender: Unisex')
        self.assertEqual(mock_fetch.call_count, 2)

        mock_sleep.assert_called_once_with(2)

    @patch('utils.extract.fetching_content')
    def test_scrape_product_fetch_fails_returns_empty(self, mock_fetch):
        mock_fetch.return_value = None

        result = scrape_product("https://fashion-studio.dicoding.dev")

        self.assertEqual(result, [])

        mock_fetch.assert_called_once()


if __name__ == "__main__":
    unittest.main()
