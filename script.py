import mysql.connector
import praw #Reddit API
from datetime import datetime
import json
import time
from langdetect import detect, LangDetectException

with open("secrets.json", "r") as f:
    secrets = json.load(f)

reddit = praw.Reddit(
    client_id=secrets["client_id"],
    client_secret=secrets["client_secret"],
    user_agent=secrets["user_agent"],
    username=secrets["username"],
    password=secrets["password"]
)

conn = mysql.connector.connect(
    host='localhost',
    user=secrets["SQLuser"],
    password=secrets["SQLpassword"],
    database='reddit_data'
)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS posts (
    id VARCHAR(10) PRIMARY KEY,
    title TEXT,
    author VARCHAR(255),
    score INT,
    created_at DATETIME,
    num_comments INT,
    subreddit VARCHAR(225),
    content TEXT,
    image_url TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS posts_with_lang (
    id VARCHAR(10) PRIMARY KEY,
    title TEXT,
    author VARCHAR(255),
    score INT,
    created_at DATETIME,
    num_comments INT,
    subreddit VARCHAR(225),
    content TEXT,
    image_url TEXT,
    language VARCHAR(20)
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS last_fetched (
    subreddit VARCHAR(225) PRIMARY KEY,
    last_timestamp BIGINT
)
""")

def get_image_url(post):
    if hasattr(post, "url") and post.url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
        return post.url
    return None

def get_last_timestamp(subreddit):
    cursor.execute("SELECT last_timestamp FROM last_fetched WHERE subreddit = %s", (subreddit,))
    row = cursor.fetchone()
    return row[0] if row else 0

def update_last_timestamp(subreddit, timestamp):
    cursor.execute("""
        INSERT INTO last_fetched (subreddit, last_timestamp)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE last_timestamp = VALUES(last_timestamp)
    """, (subreddit, int(timestamp)))

def detect_language(text):
    try:
        return detect(text)
    except LangDetectException:
        return "unknown"

log_file = open("reddit_data.log", "a", encoding="utf-8")
lang_log_file = open("bengali_assamese.log", "a", encoding="utf-8")

subreddits = [
    "books","cybersecurity","hacking","malware","technology","chatgpt","stories","ocpoetry","ocpoetryfree","shakespeare","assam","westbengal","cricket","askreddit",
    "technicallythetruth","clevercomebacks","creativeinsults","funny","worldnews","music","memes","gaming","science","movies","law","adulting","subredditdrama","advice",
    "marvelrivals","valorant","teachers","alien","india","interesting","notinteresting","news","wordnews","datascience","data","python","snakes","blog","instagram",
    "facebook","facepalm","scams","fish","aww","animals","police","time","timetravel","microsoft","google","amazon","netflix","europe","asia","america","australia","penguin",
    "panda","china","ukraine","war","vietnam","sleep","rant","morality","judge","legal","bible","thegita","BhagavadGita","hinduism","Christianity","Jesus","git","github","unity",
    "Unity3D","Unity2D","vns","visualnovels","dev","gamedev","devil","engineering","doctor","horror","mentalhealth","friends","forensics","detective","sherlock","agathachristie",
    "marvel","youtube","program","matrix","maths","student","cars","weird","college","school","photography","family","conspiracy","shitpost","bollywood","BangladeshMedia",
    "ipl","Original_Poetry","Best_Poetry","KeepWriting","BanglaPokkho","Banglasahityo","AssameseFeed","bengalilanguage","kolkata","guwahati"
]

while True:
    total_activity = 0

    for sub in subreddits:
        last_ts = get_last_timestamp(sub)
        new_max_ts = last_ts

        subreddit = reddit.subreddit(sub)
        print(f"Fetching from r/{sub}...")
        log_file.write(f"Fetching from r/{sub}...\n")

        for post in subreddit.new(limit=1000):
        
            if int(post.created_utc) <= last_ts:
                continue

            post_id = post.id
            created_at = datetime.fromtimestamp(post.created_utc)
            content = post.selftext if hasattr(post, "selftext") else ""
            img_url = get_image_url(post)
            lang = detect_language(post.title + " " + content)

            data = (
                post_id, post.title, str(post.author), post.score,
                created_at, post.num_comments, sub, content, img_url
            )

            cursor.execute("""
                INSERT INTO posts (id, title, author, score, created_at, num_comments, subreddit, content, image_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    score=VALUES(score),
                    num_comments=VALUES(num_comments)
            """, data)
            post_url = f"https://reddit.com{post.permalink}"
            log_entry = (
                f"[ADDED] r/{sub} - {post_id} - \"{post.title[:60]}\" (Score: {post.score}, Comments: {post.num_comments})\n"
                f"    URL: {post_url}\n"
                f"    Timestamp: {created_at}\n"
            )
            if lang in ("bn", "as"):
                log_entry += f"    Language: {lang}\n"
            log_entry += "-" * 80 + "\n"

            log_file.write(log_entry)
            log_file.flush()
            print(log_entry.strip())  # strip to avoid double spacing

            # Insert into posts_with_lang only if bn or as
            if lang in ("bn", "as"):
                data_lang = data + (lang,)
                cursor.execute("""
                    INSERT INTO posts_with_lang (id, title, author, score, created_at, num_comments, subreddit, content, image_url, language)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        score=VALUES(score),
                        num_comments=VALUES(num_comments),
                        language=VALUES(language)
                """, data_lang)

                # Log in separate file
                lang_log_file.write(f"[{lang.upper()}] {post.id} - {post.title[:60]}\n")
                if content:
                    lang_log_file.write(f"Content: {content[:100]}...\n")
                if img_url:
                    lang_log_file.write(f"Image: {img_url}\n")
                lang_log_file.write("-" * 80 + "\n")
                lang_log_file.flush()
            
            total_activity += 1
            new_max_ts = max(new_max_ts, int(post.created_utc))

        update_last_timestamp(sub, new_max_ts)
        conn.commit()

    if total_activity == 0:
        print("No new posts found. Sleeping for 60 seconds.")
        time.sleep(60)
    else:
        print(f"Processed {total_activity} posts. Continuing immediately...")
