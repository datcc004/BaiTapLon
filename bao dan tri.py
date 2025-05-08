import requests
from bs4 import BeautifulSoup
import pandas as pd
import schedule
import time
from datetime import datetime

# Lấy nội dung từ 1 bài viết
def get_article_data(url):
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')

        title = soup.find('h1').text.strip()
        description = soup.find('h2').text.strip() if soup.find('h2') else ''
        image_tag = soup.find('figure')
        image = image_tag.find('img')['src'] if image_tag and image_tag.find('img') else ''
        content = ' '.join([p.text.strip() for p in soup.select('article p')])

        return {
            'Tiêu đề': title,
            'Mô tả': description,
            'Hình ảnh': image,
            'Nội dung': content,
            'Link': url
        }
    except Exception as e:
        print(f"[LỖI] Không thể lấy bài viết {url} - {e}")
        return None

# Lấy danh sách link bài viết từ nhiều trang
def get_all_article_links(start_url, max_pages=3):
    article_links = set()
    for page in range(1, max_pages + 1):
        url = f"{start_url}/trang-{page}.htm"
        try:
            res = requests.get(url, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            for a in soup.select('h3 a'):
                link = a['href']
                if link.startswith('/'):
                    link = 'https://dantri.com.vn' + link
                article_links.add(link)
        except Exception as e:
            print(f"[LỖI] Trang {url} không tải được - {e}")
    return list(article_links)

# Lưu vào CSV
def save_to_csv(data):
    today = datetime.now().strftime('%Y-%m-%d')
    df = pd.DataFrame(data)
    df.to_csv(f'dantri_articles_{today}.csv', index=False, encoding='utf-8-sig')
    print(f" Đã lưu {len(data)} bài viết vào file CSV.")

# Công việc hàng ngày
def daily_job():
    print(" Bắt đầu thu thập dữ liệu...")
    links = get_all_article_links("https://dantri.com.vn", max_pages=3)
    print(f" Đã lấy {len(links)} link bài viết.")
    data = []
    for link in links:
        article = get_article_data(link)
        if article:
            data.append(article)
    save_to_csv(data)

# Lên lịch chạy mỗi ngày lúc 6h sáng
schedule.every().day.at("06:00").do(daily_job)

print(" Đang chờ đến 6h sáng để chạy tự động...")
while True:
    schedule.run_pending()
    time.sleep(60)
