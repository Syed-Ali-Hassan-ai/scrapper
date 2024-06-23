import asyncio
import csv
from datetime import datetime
from playwright.async_api import async_playwright
import json
from pathlib import Path

COOKIE_FILE = 'cookies.json'

async def read_cookies_from_tsv(tsv_file):
    cookies = []
    with open(tsv_file, 'r', newline='') as file:
        reader = csv.DictReader(file, delimiter='\t')
        for row in reader:
            if row['expires'] == 'Session':
                expires = -1  # Session cookies have no expiration date
            else:
                expires = float(datetime.strptime(row['expires'], '%Y-%m-%dT%H:%M:%S.%fZ').timestamp())
            cookies.append({
                'name': row['name'],
                'value': row['value'],
                'domain': row['domain'],
                'path': row['path'],
                'expires': expires,
                'httpOnly': row['httpOnly'].lower() == '✓',
                'secure': row['secure'].lower() == '✓',
                'sameSite': row['sameSite'] if row['sameSite'] else 'None',
            })
    return cookies

async def save_cookies(context):
    cookies = await context.cookies()
    with open(COOKIE_FILE, 'w') as file:
        json.dump(cookies, file)

async def load_cookies(context):
    if Path(COOKIE_FILE).exists():
        with open(COOKIE_FILE, 'r') as file:
            cookies = json.load(file)
        await context.add_cookies(cookies)

# Number of screens to scroll
NUM_SCREENS = 3

async def scrape_linkedin_posts(state_path: str | None = None):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        await load_cookies(context)

        page = await context.new_page()
        await page.goto('https://www.linkedin.com/company/openai/posts/?feedView=all', timeout=60000)

        if await page.locator('input[id="username"]').count() > 0:
            await page.fill('input[id="username"]', 'Harsztraders@gmail.com')
            await page.fill('input[id="password"]', 'SYEDali1957')
            await page.click('button[type="submit"]')

            await page.wait_for_selector('div.feed-shared-update-v2', timeout=60000)
            await save_cookies(page.context)
        else:
            await page.wait_for_selector('div.feed-shared-update-v2', timeout=60000)

        for _ in range(NUM_SCREENS):
            await page.evaluate('window.scrollBy(0, window.innerHeight)')
            await page.wait_for_timeout(500)  # Wait for content to load

        posts_elements = await page.locator('div.feed-shared-update-v2').all()
        posts_data = []

        for idx, post_element in enumerate(posts_elements):
            
            post_text = await post_element.locator('.update-components-text').first.inner_text()
            post_author = await post_element.locator('.update-components-actor__title').first.inner_text()
            post_timestamp = await post_element.locator('.update-components-actor__sub-description').first.inner_text()

            repost_text = ""
            repost_author = ""
            repost_timestamp = ""
            repost_author_designation = ""

            repost_element = post_element.locator('div.feed-shared-update-v2__description-wrapper + div.update-components-mini-update-v2')
            if await repost_element.count() > 0:
                await repost_element.wait_for(timeout=30000)
                
                # Debugging information
                print(f"Post {idx}: Found a reposted content")
                
                repost_text = await repost_element.locator('.update-components-text').first.inner_text()
                repost_author = await repost_element.locator('.update-components-actor__title').first.inner_text()
                repost_timestamp = await repost_element.locator('.update-components-actor__sub-description').first.inner_text()
                
                # Extracting repost author's designation from the correct HTML structure
                repost_author_designation = await repost_element.locator('.update-components-actor__description').first.inner_text()

            posts_data.append({
                'author': post_author,
                'text': post_text,
                'timestamp': post_timestamp,
                'repost_author': repost_author,
                'repost_text': repost_text,
                'repost_timestamp': repost_timestamp,
                'repost_author_designation': repost_author_designation,
            })

        with open('linkedin_posts.json', 'w', encoding='utf-8') as json_file:
            json.dump(posts_data, json_file, ensure_ascii=False, indent=4)

        await browser.close()

# Run the function
asyncio.run(scrape_linkedin_posts("state.json"))
