import argparse
import asyncio
import logging
import os
import uuid
import json
from datetime import datetime
from dotenv import load_dotenv
import csv

# Load environment variables from .env file
load_dotenv()

from config.config import CONFIG
from fetchers.reddit_fetcher import RedditFetcher
from fetchers.linkedin_fetcher import LinkedInFetcher
from fetchers.google_fetcher import GoogleFetcher
from summarizer.gpt_summarizer import GPTSummarizer
from emailer.sender import EmailSender

OUTPUT_DIR = "output"
PREVIEW_DIR = "previews"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ULTRATHINK")

def deduplicate_content(items):
    """Remove duplicate items based on title similarity"""
    seen_titles = set()
    unique_items = []
    
    for item in items:
        # Create a normalized title for comparison
        title = item.get('title', item.get('text', ''))[:100].lower().strip()
        
        if title and title not in seen_titles:
            seen_titles.add(title)
            unique_items.append(item)
    
    return unique_items

def save_output(run_id, summary_dict, preview_html=None):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = os.path.join(OUTPUT_DIR, f"ultrathink_{run_id}.json")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary_dict, f, indent=2, ensure_ascii=False)

    if preview_html:
        html_path = os.path.join(PREVIEW_DIR, f"preview_{timestamp}.html")
        os.makedirs(PREVIEW_DIR, exist_ok=True)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(preview_html)
        return json_path, html_path

    return json_path, None

async def run_pipeline(preview=False):
    run_id = str(uuid.uuid4())
    logger.info(f"Starting run ID: {run_id}")

    config = CONFIG
    
    # ✅ ADD THIS: Load employees from CSV
    try:
        employees = []
        with open(config['email']['employee_csv'], 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert 'active' string to boolean
                if row['active'].lower() == 'true':
                    employees.append({
                        'name': row['name'],
                        'email': row['email'],
                        'role': row['role'],
                        'active': True,
                        'keywords': row['keywords']
                    })
        config['employees'] = employees
        logger.info(f"Loaded {len(config['employees'])} active employees")
    except Exception as e:
        logger.error(f"Failed to load employees: {e}")
        config['employees'] = []

    sources = {
        "reddit": deduplicate_content(await RedditFetcher(config).fetch()),
        "linkedin": deduplicate_content(await LinkedInFetcher(config).fetch()),
        "google": deduplicate_content(await GoogleFetcher(config).fetch()),
    }

    summarizer = GPTSummarizer()

    try:
        summary_raw = summarizer.generate_summary(sources, config)
        summary = json.loads(summary_raw) if isinstance(summary_raw, str) else summary_raw
    except Exception as e:
        logger.error(f"❌ GPT summary generation failed: {e}")
        return

    emailer = EmailSender(config)

    if preview:
        preview_path = os.path.join(PREVIEW_DIR, f"preview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
        emailer.save_preview(summary, preview_path)
        json_path, _ = save_output(run_id, summary)
        logger.info(f"✅ HTML preview saved at: {preview_path}")
        logger.info(f"✅ Summary JSON saved at: {json_path}")
    else:
        emailer.send_digest(summary)
        json_path, _ = save_output(run_id, summary)
        logger.info(f"✅ Emails sent. Summary JSON saved at: {json_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview", action="store_true", help="Only generate preview, don't send emails")
    args = parser.parse_args()

    asyncio.run(run_pipeline(preview=args.preview))
