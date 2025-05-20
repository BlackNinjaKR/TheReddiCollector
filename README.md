# 🧠 Reddit Data Collector (with language detection)

This project is a Python-based Reddit data collector that uses the [PRAW](https://praw.readthedocs.io/) API to scrape posts from a large set of subreddits and store them in a MySQL database for research, analysis, or machine learning projects. It is optimized for long-running operation, duplicate-safe insertion, and extensibility.

> Language detection is included — not because it’s the main feature, but because the author is a nerd and wanted to see how many posts are secretly Bengali/Assamese. (Hint: `langdetect` isn't sure either.)

---

## 🚀 Features

- 🔁 Persistent scraping across hundreds of subreddits
- 💾 Efficient MySQL storage (including schema creation)
- 🧠 Optional language detection using `langdetect`
- 🖼️ Auto-detects image URLs in posts
- 📜 Logs activity for debugging, analysis, or bragging rights
- 📉 Gracefully waits if no new data is found
- 🛠️ Designed for modularity and further extension

---

## 🗃️ Database Schema

Three main tables:

- `posts`: Stores all collected post metadata.
- `posts_with_lang`: Subset of `posts` where language is detected (currently focusing on Bengali and Assamese).
- `last_fetched`: Tracks the last processed post per subreddit to avoid duplication.

---

## 🧰 Requirements

- Python 3.7+
- MySQL Server
- Reddit Developer Credentials
- `praw`, `langdetect`, `mysql-connector-python`

Install dependencies:

```bash
pip install praw langdetect mysql-connector-python
```

---

## 🔐 Setup

1. Create a secrets.json file in the root directory:
    ```json
    {
      "client_id": "your_reddit_client_id",
      "client_secret": "your_reddit_client_secret",
      "user_agent": "your_app_name/0.1 by your_username",
      "username": "your_reddit_username",
      "password": "your_reddit_password",
      "SQLuser": "your_mysql_username",
      "SQLpassword": "your_mysql_password"
    }
    ```

2. Ensure you have a database named `reddit_data` in MySQL.
   ```sql
   CREATE DATABASE reddit_data;
   ```

---

## 🏃‍♂️ Running the Script

```bash
python reddit_collector.py
```

- The script will begin collecting new posts across the pre-defined subreddits.
- Posts will be skipped if already stored.
- Language-specific logs will be saved to `bengali_assamese.log`.

---

## 🧪 Notes on Language Detection

- This is a secondary, optional feature.
- Uses `langdetect`, which struggles with short posts or languages sharing the same script (e.g., Bengali vs. Assamese).
- Posts detected as `bn` or `as` are stored in a separate table for convenience.

---

## 📋 Logging

- `reddit_data.log`: Full log of post insertions and activity.
- `bengali_assamese.log`: Only logs posts detected as Bengali or Assamese.

Pro tip: log files grow fast — rotate them or archive periodically if running long-term.

---

## 🧠 Use Cases

- Data mining & NLP research
- Social media analysis
- Time-series sentiment tracking
- Language-specific content studies (just for fun)
- Feeding your data-hungry ML model

---

## ⚠️ Disclaimer

This script respects Reddit's rate limits and content guidelines. Use responsibly and don't DDOS Reddit unless you want to be banned _and_ morally judged.

---

## 📜 License

MIT License — free to use, modify, and meme responsibly.

---

## 🙏 Acknowledgments

- [PRAW](https://praw.readthedocs.io/en/stable/) for simplifying Reddit API access
- langdetect for trying its best
- Coffee, for keeping this script alive through long nights

---
