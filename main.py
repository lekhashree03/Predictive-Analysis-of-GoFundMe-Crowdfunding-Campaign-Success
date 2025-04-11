#!/usr/bin/env python3
import gofund_links_scraper    # for link discovery :contentReference[oaicite:0]{index=0}
import scrape_by_campaign      # for campaign‐page scraping :contentReference[oaicite:1]{index=1}
import sys

def unique_links():
    """
    Deduplicate campaign_links.txt → urllist_master.txt
    (logic from is_unique.py) :contentReference[oaicite:2]{index=2}
    """
    INFILE = 'campaign_links.txt'
    OUTFILE = 'urllist_master.txt'
    
    seen = set()
    uniq = []
    
    with open(INFILE, 'r') as fin:
        for line in fin:
            url = line.strip().split('?', 1)[0]
            if url and url not in seen:
                seen.add(url)
                uniq.append(url)
    
    print(f"unique URLs: {len(uniq)}")
    
    with open(OUTFILE, 'w') as fout:
        for url in uniq:
            fout.write(url + '\n')
        
def main():
    # 1) scrape all GoFundMe links into campaign_links.txt
    gofund_links_scraper.main()

    # 2) filter out duplicates into urllist_master.txt
    unique_links()

    # 3) scrape each campaign URL into a CSV
    scrape_by_campaign.main()

    print("✅ All steps completed successfully!")

if __name__ == "__main__":
    main()
