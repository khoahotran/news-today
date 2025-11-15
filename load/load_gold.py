from extract.gold_scraper import fetch_gold
from transform.transform_gold import transform_gold

if __name__ == "__main__":
    print("=== Running Gold ETL ===")
    fetch_gold()
    transform_gold()
    print("=== Done Gold ETL ===")