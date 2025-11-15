from extract.crypto_api import fetch_crypto
from transform.transform_crypto import transform_crypto

if __name__ == "__main__":
    print("=== Running Crypto ETL ===")
    fetch_crypto()
    transform_crypto()
    print("=== Done Crypto ETL ===")