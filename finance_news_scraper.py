#!/usr/bin/env python3
"""
財經新聞自動化系統
每日抓取 Yahoo奇摩股市 RSS 真實新聞，產生網站首頁 docs/index.html
"""

import html
import logging
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

RSS_URL = "https://tw.stock.yahoo.com/rss?category=tw-market"
OUTPUT_PATH = "docs/index.html"
MAX_ITEMS = 10
TAIPEI_TZ = timezone(timedelta(hours=8))
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}


def fetch_news():
    """從 Yahoo奇摩股市 RSS 抓取真實新聞列表"""
    logger.info(f"正在抓取新聞：{RSS_URL}")

    response = requests.get(RSS_URL, headers=HEADERS, timeout=15)
    response.raise_for_status()

    root = ET.fromstring(response.content)
    items = []

    for item in root.findall("./channel/item")[:MAX_ITEMS]:
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        description = (item.findtext("description") or "").strip()
        pub_date_raw = item.findtext("pubDate")

        if not title or not link:
            continue

        pub_date_display = ""
        if pub_date_raw:
            try:
                dt = parsedate_to_datetime(pub_date_raw).astimezone(TAIPEI_TZ)
                pub_date_display = dt.strftime("%m/%d %H:%M")
            except (TypeError, ValueError):
                pass

        items.append({
            "title": title,
            "link": link,
            "description": description,
            "pub_date": pub_date_display,
        })

    logger.info(f"成功取得 {len(items)} 則新聞")
    return items


def render_html(news_items):
    timestamp = datetime.now(TAIPEI_TZ).strftime("%Y年%m月%d日 %H:%M")

    cards = []
    for i, news in enumerate(news_items, 1):
        title = html.escape(news["title"])
        link = html.escape(news["link"])
        description = html.escape(news["description"])[:80]
        pub_date = html.escape(news["pub_date"])

        cards.append(f"""
                <a class="news-card" href="{link}" target="_blank" rel="noopener">
                    <div class="card-header">
                        <div class="card-number">{i:02d}</div>
                        <div class="card-title">{title}</div>
                    </div>
                    <div class="card-body">
                        <p class="card-desc">{description}</p>
                        <div class="card-meta">
                            <span>📰 Yahoo股市</span>
                            <span>{pub_date}</span>
                        </div>
                    </div>
                </a>""")

    news_grid_html = "".join(cards) if cards else '<p class="empty">目前沒有可顯示的新聞，請稍後再試。</p>'

    return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>財經新聞自動化 | 台灣人必看的股市消息</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Microsoft JhengHei', 'Segoe UI', sans-serif;
            background: #1a1a2e;
            color: #e0e0e0;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .banner {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            padding: 50px 40px;
            text-align: center;
            margin-bottom: 40px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}
        .banner h1 {{ font-size: 2.4em; color: white; margin-bottom: 10px; }}
        .banner p {{ font-size: 1.05em; color: rgba(255,255,255,0.9); margin-bottom: 20px; }}
        .ig-badge {{
            display: inline-block;
            background: rgba(255,255,255,0.15);
            padding: 10px 22px;
            border-radius: 25px;
        }}
        .ig-badge a {{ color: white; text-decoration: none; font-weight: bold; }}
        .ig-badge a:hover {{ text-decoration: underline; }}
        .section-title {{
            font-size: 1.6em;
            color: white;
            margin: 40px 0 25px 0;
            padding-left: 15px;
            border-left: 4px solid #667eea;
        }}
        .news-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        .news-card {{
            display: block;
            background: #2d2d44;
            border-radius: 12px;
            overflow: hidden;
            text-decoration: none;
            color: inherit;
            box-shadow: 0 6px 18px rgba(0,0,0,0.25);
            transition: transform 0.2s ease;
        }}
        .news-card:hover {{ transform: translateY(-4px); }}
        .card-header {{
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 18px 20px 10px 20px;
        }}
        .card-number {{
            font-size: 1.6em;
            font-weight: bold;
            color: #a0c4ff;
            min-width: 36px;
        }}
        .card-title {{ font-size: 1.05em; font-weight: bold; color: white; line-height: 1.4; }}
        .card-body {{ padding: 0 20px 18px 20px; }}
        .card-desc {{ font-size: 0.9em; color: #b8b8c8; line-height: 1.5; margin-bottom: 12px; }}
        .card-meta {{
            display: flex;
            justify-content: space-between;
            font-size: 0.8em;
            color: #888;
            border-top: 1px solid rgba(255,255,255,0.08);
            padding-top: 10px;
        }}
        .empty {{ color: #999; }}
        .footer {{ text-align: center; color: #999; margin-top: 50px; padding: 20px; }}
        .update-info {{
            background: rgba(102, 126, 234, 0.1);
            padding: 15px;
            border-radius: 8px;
            color: #a0c4ff;
        }}
        @media (max-width: 768px) {{
            .banner h1 {{ font-size: 1.8em; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="banner">
            <h1>📈 財經新聞自動化平台</h1>
            <p>台灣人必看的股市消息｜每日自動更新</p>
            <div class="ig-badge">
                <a href="https://instagram.com/wu_wealth_lab" target="_blank" rel="noopener">📱 追蹤 Instagram: @wu_wealth_lab</a>
            </div>
        </div>

        <div class="section-title">🔥 今日焦點新聞</div>
        <div class="news-grid">{news_grid_html}
        </div>

        <div class="footer">
            <div class="update-info">
                📊 資料來源：Yahoo股市<br>
                🔄 每天自動更新<br>
                ⏰ 最後更新：{timestamp}（台灣時間）
            </div>
        </div>
    </div>
</body>
</html>
"""


def main():
    try:
        news_items = fetch_news()
    except Exception as e:
        logger.error(f"抓取新聞失敗，保留現有頁面：{e}")
        sys.exit(1)

    if not news_items:
        logger.error("沒有抓到任何新聞，保留現有頁面")
        sys.exit(1)

    html_content = render_html(news_items)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)

    logger.info(f"✅ 已更新 {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
