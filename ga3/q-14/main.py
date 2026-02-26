from playwright.sync_api import sync_playwright

total_sum = 0

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True) #launch browser in backgroud, ie we cant see it as headless=false
    page = browser.new_page()#open a new tab

    # Loop through seeds 84 to 93
    for seed in range(84, 94):
        url = f"https://sanand0.github.io/tdsdata/js_table/?seed={seed}"
        page.goto(url)

        # Wait for table to load
        page.wait_for_selector("table")

        # Get all numbers from table cells
        cells = page.locator("td").all_inner_texts()

        # Convert to integers and sum
        numbers = [int(x) for x in cells]
        page_sum = sum(numbers)

        print(f"Seed {seed} sum:", page_sum)

        total_sum += page_sum

    browser.close()

print("FINAL TOTAL SUM:", total_sum)