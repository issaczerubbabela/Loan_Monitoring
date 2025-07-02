# 📄 Project README

## Overview

This project builds a full pipeline to **search, collect, analyze, and score web content** using a combination of SERP API, Playwright automation, and a Gemini Flash 2.5 LLM running in Tachyon.

The final goal is to generate a **scored output with explanations**, which can be displayed in a UI.

---

## 🔎 Workflow Overview

### 1️⃣ Web Search and Article Collection

* Perform a web search using **SERP API** for a given query.
* From the SERP results, collect the **full web content** (clean text from each webpage).
* Save each article as a file inside a folder named \`\`.

---

### 2️⃣ Document Injection and LLM Querying

* Use **Playwright** to automate interactions with Tachyon (since direct API access is not available).
* Inject the collected articles into Tachyon using Playwright (simulate file uploads or copy-paste injection as needed).
* Provide a **user prompt** to the system along with these articles.
* The LLM (Gemini Flash 2.5 inside Tachyon) returns an **analysis output as a JSON file**.

---

### 3️⃣ JSON Storage

* Save the returned JSON file locally in your codebase.
* This JSON file typically contains:

  * Scores
  * Explanations
  * Other relevant metadata

---

### 4️⃣ Scoring and UI Output

* Read the stored JSON file.
* Process it to extract:

  * A final **score** for each article or analysis case.
  * A detailed **explanation** for that score.
* Display the results in a **user-friendly UI**.

---

## 💡 Key Tools Used

* **SERP API**: To perform robust and customizable web searches.
* **Playwright**: To automate browser-based interactions with Tachyon.
* **Gemini Flash 2.5 LLM (via Tachyon)**: To analyze content and generate scores.
* **Local file storage**: For saving articles and JSON results.

---

## ⚙️ Folder Structure

```
project-root/
│
├── Articles/          # Contains all raw web articles collected
│   ├── article1.txt
│   ├── article2.txt
│   └── ...
│
├── results/           # Contains JSON files returned from Tachyon
│   ├── analysis1.json
│   ├── analysis2.json
│   └── ...
│
├── scripts/           # Automation scripts (e.g., Playwright scripts)
│
├── ui/                # UI code to display final scores
│
└── README.md          # This file
```

---

## 🧑‍💻 Usage

1. **Search and download articles**
   Run your SERP API script to populate the `Articles` folder.

2. **Inject articles and get analysis**
   Run Playwright automation to upload articles to Tachyon and fetch JSON results.

3. **Store and process**
   Save JSON outputs in the `results` folder and parse them as needed.

4. **View results in UI**
   Start the UI app to see final scores and explanations.

---

## 💬 Notes

* The scraping logic and detailed Playwright automation steps are described in separate scripts and chats (refer to "automating file upload" instructions).
* Always verify and comply with website scraping and usage policies when using SERP API and web content.

---

## ✅ Future Enhancements

* Add direct API access for Tachyon (when available) to remove the need for Playwright.
* Implement automated article pre-filtering before injection.
* Add batch processing and progress monitoring in UI.
ess monitoring in UI.


