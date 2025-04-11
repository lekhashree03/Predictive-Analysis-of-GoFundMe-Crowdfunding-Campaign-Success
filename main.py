#!/usr/bin/env python3
import gofund_links_scraper    # for link discovery :contentReference[oaicite:0]{index=0}
import scrape_by_campaign      # for campaign‐page scraping :contentReference[oaicite:1]{index=1}

def unique_links():
    """
    Deduplicate campaign_links.txt → urllist_master.txt
    (logic from is_unique.py) :contentReference[oaicite:2]{index=2}
    """
    with open('campaign_links.txt', 'r', encoding='utf-8') as fin:
        lines = fin.readlines()

    seen = set()
    uniq = []
    for url in lines:
        if url not in seen:
            uniq.append(url)
            seen.add(url)

    print(f"Deduplicated: {len(uniq)} unique links")
    with open('urllist_master.txt', 'w', encoding='utf-8') as fout:
        fout.writelines(uniq)

def main():
    # 1) scrape all GoFundMe links into campaign_links.txt
    # gofund_links_scraper.main()

    # 2) filter out duplicates into urllist_master.txt
    # unique_links()

    # 3) scrape each campaign URL into a CSV
    scrape_by_campaign.main()

    print("✅ All steps completed successfully!")

if __name__ == "__main__":
    main()
