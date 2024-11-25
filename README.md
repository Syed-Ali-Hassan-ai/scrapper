
# LinkedIn Post Scraper

This script uses Playwright to scrape posts from a LinkedIn company page, including details about reposted content. It handles authentication, cookie management, and pagination for efficient data collection.

---

## Features

- **Cookie Management:** Saves and loads cookies to bypass login during repeated runs.
- **LinkedIn Authentication:** Automates the login process using credentials.
- **Post Scraping:** Extracts post details such as author, text, timestamp, and reposted content.
- **Pagination:** Scrolls through multiple screens to gather more posts.
- **JSON Export:** Saves the scraped data into a JSON file for further analysis.

---

## Requirements

### Dependencies

The following Python packages are required:
- `playwright`
- `asyncio`

Install them using pip:

```bash
pip install playwright asyncio
```

Ensure you install Playwright's browser binaries:

```bash
playwright install
```

---

## Setup and Usage

1. **Prepare Credentials:**
   Replace the placeholders for email (`Harsztraders@gmail.com`) and password (`SYEDali1957`) with your LinkedIn credentials.

2. **Run the Script:**
   Execute the script using Python:

   ```bash
   python your_script_name.py
   ```

3. **Output:**
   - Posts are saved in `linkedin_posts.json` in the current working directory.
   - Cookies are saved in `cookies.json` for reuse.

---

## Code Breakdown

### Authentication
- Checks if login is required using a selector.
- Automatically fills in email and password if necessary.
- Stores cookies after successful login to reduce login prompts.

### Post Scraping
- Locates post elements on the LinkedIn page using CSS selectors.
- Extracts the following details:
  - Post author and text
  - Timestamp of the post
  - Reposted content, including author, text, timestamp, and designation.

### Pagination
- Scrolls down the page a set number of times (`NUM_SCREENS`) to load additional posts.

### JSON Export
- Scraped data is stored in a structured JSON format, making it easy to analyze or import into other tools.

---

## Configuration

### Adjustable Parameters
- **Cookie File:** `COOKIE_FILE` can be updated to change the path where cookies are stored.
- **Number of Screens to Scroll:** Update `NUM_SCREENS` to control how many pages of posts are loaded.

---

## Future Improvements
- Add support for scraping post engagement metrics (likes, comments, etc.).
- Implement headless scraping to improve performance.
- Add CLI arguments for dynamic input of LinkedIn credentials and company page URLs.

---

## License

This project is released under the MIT License. Feel free to use, modify, and distribute the code.

---

## Credits

Developed using:
- [Playwright](https://playwright.dev/)
- [AsyncIO](https://docs.python.org/3/library/asyncio.html)
