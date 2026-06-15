from datetime import datetime

import numpy as np
import pandas as pd


def transform_to_DataFrame(data):
    """Mengubah data menjadi DataFrame."""
    df = pd.DataFrame(data)
    return df


def transform_data(data, exchange_rate):
    """Menggabungkan semua transformasi data menjadi satu fungsi."""

    # Transformasi title
    data = data[~data['title'].str.lower().str.contains('unknown', na=False)].copy()
    data['title'] = data['title'].astype('string')

    # Transformasi price
    data['price'] = data['price'].replace(r'[^\d.]', '', regex=True).replace('', np.nan)
    data.dropna(subset=['price'], inplace=True)
    data['price'] = data['price'].astype(float) * exchange_rate

    # Transformasi rating
    data['rating'] = data['rating'].astype(str).str.extract(r'(\d+\.\d+|\d+)').replace('', np.nan)
    data.dropna(subset=['rating'], inplace=True)
    data['rating'] = data['rating'].astype(float)

    # Transformasi colors
    data['colors'] = data['colors'].replace(r'\D', '', regex=True).replace('', np.nan)
    data.dropna(subset=['colors'], inplace=True)
    data['colors'] = data['colors'].astype(int)

    # Transformasi size
    data['size'] = data['size'].replace(r'Size:\s*', '', regex=True)
    data['size'] = data['size'].astype('string')

    # Transformasi gender
    data['gender'] = data['gender'].replace(r'Gender:\s*', '', regex=True)
    data['gender'] = data['gender'].astype('string')

    # Menghapus kolom redundan
    data.drop_duplicates(inplace=True)
    data.dropna(inplace=True)

    # Tambahkan kolom timestamp
    data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    return data
