
from playwright.sync_api import sync_playwright
import time

START_URL = "https://sanand0.github.io/tdsdata/cdp_trap/index.html?student=23f3003994%40ds.study.iitm.ac.in"
BASE = "https://sanand0.github.io/tdsdata/cdp_trap/"
STUDENT_PARAM = "?student=23f3003994%40ds.study.iitm.ac.in"

visited = set()
error_pages = []
first_error_page = None
current_page_name = None  # track active page


def normalize(url):
    if "student=" not in url:
        if "?" in url:
            return url + "&student=23f3003994%40ds.study.iitm.ac.in"
        else:
            return url + STUDENT_PARAM
    return url


def visit(page, url):
    global first_error_page, current_page_name

    url = normalize(url)

    if url in visited:
        return
    visited.add(url)

    page.goto(url, wait_until="load")

    current_page_name = page.url.split("/")[-1].split("?")[0]
    print(f"Navigating to : {current_page_name}")

    # wait for async failures (seed delay + 1000)
    time.sleep(5)

    # collect links BEFORE navigating
    hrefs = page.eval_on_selector_all("a", "els => els.map(e => e.getAttribute('href'))")

    for href in hrefs:
        if href and "page_" in href:
            next_url = BASE + href
            visit(page, next_url)


def run():
    global first_error_page

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Attach listener ONLY ONCE
        def on_page_error(err):
            global first_error_page
            print(f"  [!] UNCAUGHT EXCEPTION on {current_page_name}: {err.message}")

            if current_page_name not in error_pages:
                error_pages.append(current_page_name)
                if not first_error_page:
                    first_error_page = current_page_name

        page.on("pageerror", on_page_error)

        visit(page, START_URL)
        browser.close()

    print(f"\nTOTAL_PAGES_VISITED={len(visited)}")
    print(f"TOTAL_ERRORS={len(error_pages)}")
    print(f"ERROR_PAGES={error_pages}")


if __name__ == "__main__":
    run()



## not working code with listener inside visit() which causes multiple listeners to be attached and messes up the error page tracking
# from playwright.sync_api import sync_playwright
# import time

# START_URL = "https://sanand0.github.io/tdsdata/cdp_trap/index.html?student=23f3003994%40ds.study.iitm.ac.in"
# BASE = "https://sanand0.github.io/tdsdata/cdp_trap/"
# STUDENT_PARAM = "?student=23f3003994%40ds.study.iitm.ac.in"

# visited = set()
# error_pages = []
# first_error_page = None


# def normalize(url):
#     if "student=" not in url:
#         if "?" in url:
#             return url + "&student=23f3003994%40ds.study.iitm.ac.in"
#         else:
#             return url + STUDENT_PARAM
#     return url


# def visit(page, url):
#     global first_error_page

#     url = normalize(url)

#     if url in visited:
#         return
#     visited.add(url)

#     page.goto(url, wait_until="load")

#     page_name = page.url.split("/")[-1].split("?")[0]

#     error_flag = False

# # 1️⃣ Catch real uncaught exceptions
#     def on_page_error(err):
#         nonlocal error_flag
#         error_flag = True

#     page.on("pageerror", on_page_error)



#     # wait for async failures
#     time.sleep(7)

#     if error_flag:
#         error_pages.append(page_name)
#         if not first_error_page:
#             first_error_page = page_name

#     # IMPORTANT: collect hrefs BEFORE navigation
#     hrefs = page.eval_on_selector_all("a", "els => els.map(e => e.getAttribute('href'))")

#     for href in hrefs:
#         if href and "page_" in href:
#             next_url = BASE + href
#             visit(page, next_url)


# def run():
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=False)
#         page = browser.new_page()

#         visit(page, START_URL)

#         browser.close()

#     print(f"TOTAL_PAGES_VISITED={len(visited)}")
#     print(f"TOTAL_ERRORS={len(error_pages)}")
#     print(f"FIRST_ERROR_PAGE={first_error_page}")


# if __name__ == "__main__":
#     run()





## gemini -- working code
# import time
# from playwright.sync_api import sync_playwright


# # Configuration
# STUDENT_EMAIL = "23f3003994@ds.study.iitm.ac.in"
# BASE_URL = "https://sanand0.github.io/tdsdata/cdp_trap/"
# START_URL = f"{BASE_URL}index.html?student={STUDENT_EMAIL}"

# # Tracking State
# visited = set()
# error_pages = []  # We will store the names of pages that crash here

# def normalize(href):
#     if not href.startswith("http"):
#         href = BASE_URL + href
#     if "student=" not in href:
#         connector = "&" if "?" in href else "?"
#         href = f"{href}{connector}student={STUDENT_EMAIL}"
#     return href

# def visit(page, url):
#     url = normalize(url)
#     if url in visited:
#         return
#     visited.add(url)

#     page_name = url.split("/")[-1].split("?")[0]
#     print(f"Navigating to: {page_name}")
    
#     # Navigate
#     page.goto(url, wait_until="load")
    
#     # Wait for the async "trap" errors to trigger (usually 1-3 seconds)
#     time.sleep(5)

#     # Discover links for the next crawl step
#     hrefs = page.eval_on_selector_all("a", "els => els.map(e => e.getAttribute('href'))")
#     for href in hrefs:
#         if href and "page_" in href:
#             visit(page, href)

# def run():
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=True)
#         context = browser.new_context()
#         page = context.new_page()

#         # UPDATED LISTENER: Appends directly to the error_pages list
#         def handle_page_error(exception):
#             # Get the filename of the current page at the moment of the crash
#             current_filename = page.url.split("/")[-1].split("?")[0]
#             if current_filename not in error_pages:
#                 error_pages.append(current_filename)
#             print(f"  [!] UNCAUGHT EXCEPTION on {current_filename}: {exception.message}")

#         # Attach the listener to the page
#         page.on("pageerror", handle_page_error)

#         # Start Crawling
#         visit(page, START_URL)
#         browser.close()

#     # Final Diagnostic Report
#     first_error = error_pages[0] if error_pages else "None"
    
#     print("\n" + "="*30)
#     print(f"TOTAL_PAGES_VISITED={len(visited)}")
#     print(f"TOTAL_ERRORS={len(error_pages)}")
#     print(f"FIRST_ERROR_PAGE={first_error}")
#     print(f"ALL_ERROR_PAGES={error_pages}")
#     print("="*30)

# if __name__ == "__main__":
#     run()