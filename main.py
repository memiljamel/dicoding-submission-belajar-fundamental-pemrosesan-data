from utils.extract import scrape_product
from utils.load import store_to_postgresql, store_to_csv
from utils.transform import transform_to_DataFrame, transform_data


def main():
    """Fungsi utama untuk keseluruhan proses scraping hingga menyimpannya."""
    BASE_URL = 'https://fashion-studio.dicoding.dev'

    # Menjalankan scraping untuk mengambil data products
    all_products_data = scrape_product(BASE_URL)

    # Jika data berhasil diambil, lakukan transformasi dan simpan ke PostgreSQL
    if all_products_data:
        try:
            # Mengubah data menjadi DataFrame
            DataFrame = transform_to_DataFrame(all_products_data)

            # Mentransformasikan data (misalnya konversi mata uang, rating, dll)
            DataFrame = transform_data(DataFrame, 16000)  # Anggap 16000 adalah nilai tukar yang diperlukan
            print(DataFrame)

            # Menyimpan data ke CSV
            store_to_csv(DataFrame, 'products.csv')

            # Menyimpan data ke PostgreSQL
            db_url = 'postgresql+psycopg2://postgres:@localhost:5432/test'
            store_to_postgresql(DataFrame, db_url)  # Memanggil fungsi untuk menyimpan ke database
        except Exception as e:
            print(f"Terjadi kesalahan dalam proses: {e}")
    else:
        print("Tidak ada data yang ditemukan.")


if __name__ == '__main__':
    main()
