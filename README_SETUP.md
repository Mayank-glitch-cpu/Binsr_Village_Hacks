# TREC Report Generator - Setup Instructions

## Quick Start

### Option 1: Use the Python Server (Recommended)

1. **Start the server:**
   ```bash
   python server.py
   ```

2. **Open your browser:**
   - The browser should open automatically to `http://localhost:8000/index.html`
   - Or manually navigate to: `http://localhost:8000/index.html`

3. **Stop the server:**
   - Press `Ctrl+C` in the terminal

### Option 2: Use Python's Built-in Server

If `server.py` doesn't work, use Python's built-in HTTP server:

```bash
python -m http.server 8000
```

Then open: `http://localhost:8000/index.html`

### Option 3: Use Node.js Server (if you have Node.js)

```bash
npx http-server -p 8000
```

Then open: `http://localhost:8000/index.html`

## Why Do I Need a Server?

Browsers block loading local files due to security restrictions (CORS policy). Using a local web server allows the application to:
- Load the TREC template HTML file
- Load external resources (CSS, images)
- Work properly with all features

## Troubleshooting

### Error: "CORS policy" or "Failed to load template"
- **Solution:** Use a local web server (see options above)
- Do NOT open `index.html` directly by double-clicking

### Port 8000 Already in Use
- Use a different port:
  ```bash
  python -m http.server 8080
  ```
- Then open: `http://localhost:8080/index.html`

### Server.py Not Working
- Make sure you have Python installed
- Try: `python3 server.py` instead
- Or use the built-in server: `python -m http.server 8000`

## Required Files

Make sure these files are in the same directory:
- `index.html`
- `app.js`
- `server.py` (optional, but recommended)
- `TREC_Report_All.html` (the template)
- `trec_styles.css` (styles)
- `TREC_Report_Filled_Improved.pdf` (for download)

## Usage

1. Start the server
2. Open the app in your browser
3. Upload `inspection.json`
4. Click "Generate Report"
5. Wait for the report to populate
6. Click "Download PDF" (10-second loading, then download)

That's it! 🎉
