from sqlalchemy import create_engine


def store_to_csv(data, filename):
    data.to_csv(filename, index=False)
    print(f"Data berhasil disimpan ke {filename}")


def store_to_postgresql(data, db_url):
    """Fungsi untuk menyimpan data ke dalam PostgreSQL."""
    try:
        # Membuat engine database
        engine = create_engine(db_url)

        # Menyimpan data ke tabel 'productstoscrape' jika tabel sudah ada, data akan ditambahkan (append)
        with engine.connect() as con:
            data.to_sql('productstoscrape', con=con, if_exists='append', index=False)
            print("Data berhasil disimpan ke database")

    except Exception as e:
        print(f"Terjadi kesalahan saat menyimpan data: {e}")
