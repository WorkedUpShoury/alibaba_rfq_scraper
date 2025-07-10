# RFQHarvester

**RFQHarvester** is a general-purpose Python web scraper for extracting RFQ (Request for Quotation) data from sourcing platforms like Alibaba and others with similar page structures.

---

### 🌐 Features

- Extracts RFQ metadata (title, buyer name, country, quantity, quotes left, etc.)
- Supports platform-specific flags (Email Confirmed, Experienced Buyer, etc.)
- Outputs structured CSV data
- Supports command-line argument for input URL
- Deduplicates by RFQ ID and Title

---

### 📦 Output CSV Format

```csv
RFQ ID,Title,Buyer Name,Buyer Image,Inquiry Time,Quotes Left,Country,
Quantity Required,Email Confirmed,Experienced Buyer,Complete Order via RFQ,
Typical Replies,Interactive User,Inquiry URL,Inquiry Date,Scraping Date
```

---

### ⚙️ Requirements

- Python 3.8+
- Google Chrome + ChromeDriver
- `selenium`
- `pandas`

Install dependencies:

```bash
pip install selenium pandas
```

---

### 🚀 Usage

Run the scraper by passing the RFQ listing page URL as an argument:

```bash
python scraper.py "https://sourcing.alibaba.com/rfq/rfq_search_list.htm?country=AE&recently=Y"
```

### 📄 License

MIT License

---

### 👤 Author

Built by Shoury Sinha