import unittest

import pandas as pd

from utils.transform import transform_to_DataFrame, transform_data


class TestTransformToDataFrame(unittest.TestCase):
    def test_transform_to_dataframe_returns_dataframe(self):
        data = [
            {'title': 'Item A', 'price': '$10.00', 'rating': 'Rating: 4.5',
             'colors': 'Colors: 3', 'size': 'Size: M', 'gender': 'Gender: Male'}
        ]
        result = transform_to_DataFrame(data)

        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 1)
        self.assertIn('title', result.columns)
        self.assertIn('price', result.columns)
        self.assertIn('rating', result.columns)
        self.assertIn('colors', result.columns)
        self.assertIn('size', result.columns)
        self.assertIn('gender', result.columns)

    def test_transform_to_dataframe_empty_list(self):
        result = transform_to_DataFrame([])

        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 0)


class TestTransformData(unittest.TestCase):
    def setUp(self):
        self.raw_data = [
            {'title': 'Item A', 'price': '$10.00', 'rating': 'Rating: 4.5',
             'colors': 'Colors: 3', 'size': 'Size: M', 'gender': 'Gender: Male'},
            {'title': 'Unknown Title', 'price': '$5.00', 'rating': 'Rating: 3.0',
             'colors': 'Colors: 1', 'size': 'Size: S', 'gender': 'Gender: Female'},
        ]

    def test_transform_data_filters_unknown_title(self):
        df = transform_to_DataFrame(self.raw_data)
        result = transform_data(df, 16000)

        self.assertNotIn('Unknown Title', result['title'].values)
        self.assertEqual(len(result), 1)

    def test_transform_data_price_conversion(self):
        df = transform_to_DataFrame(self.raw_data)
        result = transform_data(df, 16000)

        self.assertEqual(result.iloc[0]['price'], 10.00 * 16000)
        self.assertTrue(pd.api.types.is_float_dtype(result['price']))

    def test_transform_data_rating_extraction(self):
        df = transform_to_DataFrame(self.raw_data)
        result = transform_data(df, 16000)

        self.assertEqual(result.iloc[0]['rating'], 4.5)
        self.assertTrue(pd.api.types.is_float_dtype(result['rating']))

    def test_transform_data_colors_extraction(self):
        df = transform_to_DataFrame(self.raw_data)
        result = transform_data(df, 16000)

        self.assertEqual(result.iloc[0]['colors'], 3)
        self.assertTrue(pd.api.types.is_integer_dtype(result['colors']))

    def test_transform_data_size_and_gender_label_removed(self):
        df = transform_to_DataFrame(self.raw_data)
        result = transform_data(df, 16000)

        self.assertEqual(result.iloc[0]['size'], 'M')
        self.assertEqual(result.iloc[0]['gender'], 'Male')

    def test_transform_data_adds_timestamp_column(self):
        df = transform_to_DataFrame(self.raw_data)
        result = transform_data(df, 16000)

        self.assertIn('timestamp', result.columns)

    def test_transform_data_drops_duplicates(self):
        duplicated_data = [
            {'title': 'Item A', 'price': '$10.00', 'rating': 'Rating: 4.5',
             'colors': 'Colors: 3', 'size': 'Size: M', 'gender': 'Gender: Male'},
            {'title': 'Item A', 'price': '$10.00', 'rating': 'Rating: 4.5',
             'colors': 'Colors: 3', 'size': 'Size: M', 'gender': 'Gender: Male'},
        ]
        df = transform_to_DataFrame(duplicated_data)
        result = transform_data(df, 16000)

        self.assertEqual(len(result), 1)

    def test_transform_data_drops_invalid_price(self):
        invalid_data = [
            {'title': 'Item A', 'price': 'Price Not Available', 'rating': 'Rating: 4.5',
             'colors': 'Colors: 3', 'size': 'Size: M', 'gender': 'Gender: Male'},
            {'title': 'Item B', 'price': '$8.00', 'rating': 'Rating: 4.0',
             'colors': 'Colors: 2', 'size': 'Size: L', 'gender': 'Gender: Female'},
        ]
        df = transform_to_DataFrame(invalid_data)
        result = transform_data(df, 16000)

        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]['title'], 'Item B')

    def test_transform_data_drops_invalid_rating(self):
        invalid_data = [
            {'title': 'Item A', 'price': '$10.00', 'rating': 'No Rating',
             'colors': 'Colors: 3', 'size': 'Size: M', 'gender': 'Gender: Male'},
            {'title': 'Item B', 'price': '$8.00', 'rating': 'Rating: 4.0',
             'colors': 'Colors: 2', 'size': 'Size: L', 'gender': 'Gender: Female'},
        ]
        df = transform_to_DataFrame(invalid_data)
        result = transform_data(df, 16000)

        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]['title'], 'Item B')


if __name__ == "__main__":
    unittest.main()
