# RFQHarvester

**RFQHarvester** is a general-purpose Python-based scraper for extracting **Request for Quotation (RFQ)** data from sourcing platforms with structured listing pages. It is designed for ethical, research-oriented, and compliant usage scenarios.

> ⚠️ *This project is a proof of concept. Please ensure your usage complies with the terms of service and legal requirements of any platform you target.*
> Scraping RFQs must be done ethically and within terms of service. Legitimate uses include:
> Internal automation for companies monitoring buyer activity
> Research and analysis
> Controlled environments where access is permitted

---

### 🌐 Features

* Extracts detailed RFQ metadata: title, buyer info, country, quantity, inquiry status, etc.
* Identifies platform-specific attributes like *email verified*, *experienced buyer*, or *interactive user*
* Exports clean, deduplicated data to CSV
* Supports input via command-line URLs
* Intended for platforms with consistent, paginated HTML RFQ listings

---

### 📦 CSV Output Schema

```csv
RFQ ID,Title,Buyer Name,Buyer Image,Inquiry Time,Quotes Left,Country,
Quantity Required,Email Confirmed,Experienced Buyer,Complete Order via RFQ,
Typical Replies,Interactive User,Inquiry URL,Inquiry Date,Scraping Date
```

---

### ⚙️ Requirements

* Python 3.8+
* Google Chrome & ChromeDriver (installed and available in PATH)
* Python packages:

  * `selenium`
  * `pandas`

Install dependencies using:

```bash
pip install selenium pandas
```

---

### 🚀 Usage

You can run the scraper from the command line by passing a URL that points to a publicly accessible RFQ listing page:

```bash
python scraper.py "https://example.com/rfq/listing"
```

> Note: The scraper assumes a consistent HTML structure. Adjustments may be needed for different platforms.

---

### 📌 Roadmap

* ✅ MVP with working CLI and CSV export
* 🔄 Plan to add Docker-based setup for easier deployment
* 📥 Optionally support headless scraping or scheduling
* 💬 Invite feedback and contributors for improved portability

---

### 📄 License

MIT License — open to use, adapt, and extend.

---

### 👤 Author

Built by [Shoury Sinha](https://github.com/WorkedUpShoury)
