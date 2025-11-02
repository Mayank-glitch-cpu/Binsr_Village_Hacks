# TREC Report Generator UI

A modern web interface for generating TREC Property Inspection Reports from inspection.json files.

## Features

- 📁 **Easy File Upload**: Drag & drop or click to upload inspection.json
- 🔄 **Real-time Preview**: See the filled report instantly in the preview pane
- 📥 **PDF Export**: Download the complete report as a professional PDF
- ✅ **Status Tracking**: Visual indicators show progress at each step
- 🎨 **Modern UI**: Beautiful, responsive design with smooth animations

## Usage

1. **Open the Application**
   - Open `index.html` in a web browser
   - Or serve it using a local web server (recommended for CORS issues)

2. **Upload Inspection Data**
   - Click the upload area or drag & drop your `inspection.json` file
   - The file will be validated and parsed automatically

3. **Generate Report**
   - Click the "Generate Report" button
   - Wait for the report to be populated (progress bar will show)
   - The filled report will appear in the preview pane

4. **Download PDF**
   - Once the report is generated, click "Download PDF"
   - The PDF will be generated with proper page breaks and formatting
   - Save the file with your preferred name

5. **Reset**
   - Click "Reset" to clear all data and start over

## Requirements

- Modern web browser (Chrome, Firefox, Edge, Safari)
- `TREC_Report_All.html` template file (must be in the same directory)
- `inspection.json` file with valid inspection data

## File Structure

```
.
├── index.html          # Main UI interface
├── app.js             # Application logic and form population
├── TREC_Report_All.html  # TREC template (required)
├── trec_styles.css    # Styles for the TREC form (required)
└── inspection.json    # Your inspection data file
```

## Notes

- The application uses `html2canvas` and `jsPDF` libraries (loaded from CDN)
- For best results, serve the files using a local web server to avoid CORS issues
- Large inspection files may take a few moments to process
- The PDF generation process may take some time for reports with many images

## Troubleshooting

**Template not loading:**
- Ensure `TREC_Report_All.html` is in the same directory as `index.html`
- Use a local web server instead of opening directly in browser

**PDF generation fails:**
- Check browser console for errors
- Ensure all images in the report are accessible (not behind authentication)
- Try a different browser if issues persist

**Report not filling:**
- Verify your `inspection.json` has the correct structure
- Check browser console for parsing errors
- Ensure line item names match the expected format

## Browser Compatibility

- Chrome/Edge: Full support
- Firefox: Full support
- Safari: Full support
- Internet Explorer: Not supported

