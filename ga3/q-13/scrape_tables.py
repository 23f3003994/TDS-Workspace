from playwright.sync_api import sync_playwright

total_sum = 0

print("Starting Playwright scraping...")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    for seed in range(3, 13):  # seeds 3 to 12
        url = f"https://sanand0.github.io/tdsdata/js_table/?seed={seed}"
        print(f"\nOpening page: {url}")

        page.goto(url)
        page.wait_for_selector("table")

        cells = page.locator("td").all_inner_texts()
        print(f"Extracted {len(cells)} numbers")

        numbers = [int(x) for x in cells]
        page_sum = sum(numbers)

        print(f"Sum for seed {seed}: {page_sum}")

        total_sum += page_sum

    browser.close()

print("\nFINAL TOTAL SUM:", total_sum)
print("Scraping completed successfully.")