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
                # 'size': int(row['size']),
                'httpOnly': row['httpOnly'].lower() == '✓',
                'secure': row['secure'].lower() == '✓',
                'sameSite': row['sameSite'] if row['sameSite'] else 'None',
                # 'priority': row['priority'],
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

        for post_element in posts_elements:
            try:
                post_text = await post_element.locator('.update-components-text').first.inner_text()
                post_author = await post_element.locator('.update-components-actor__title').first.inner_text()
                post_timestamp = await post_element.locator('.update-components-actor__sub-description').first.inner_text()

                posts_data.append({
                    'author': post_author,
                    'text': post_text,
                    'timestamp': post_timestamp,
                })
            except Exception as e:
                print(f"Error extracting post data: {e}")

        with open('linkedin_posts.json', 'w', encoding='utf-8') as json_file:
            json.dump(posts_data, json_file, ensure_ascii=False, indent=4)

        await browser.close()

# Run the function
asyncio.run(scrape_linkedin_posts("state.json"))
