# TREC Report Generator

A Python pipeline to convert inspection JSON data into a populated TREC (Texas Real Estate Commission) HTML report.

## Overview

This pipeline takes inspection data from `inspection.json` and populates a TREC HTML template (`TREC_Report_All.html`) with all sections, line items, comments, and media.

## Pipeline Flow

```
inspection.json → populate_trec_complete.py → TREC_Report_Filled_Improved.html
```

1. **Input**: `inspection.json` - Contains inspection data with sections, line items, comments, and media
2. **Processor**: `populate_trec_complete.py` - Maps and populates the HTML template
3. **Output**: `TREC_Report_Filled_Improved.html` - Fully populated TREC report

## Files Structure

### Essential Files
- `inspection.json` - Source inspection data
- `TREC_Report_All.html` - Blank TREC HTML template
- `populate_trec_complete.py` - Main population script
- `trec_styles.css` - CSS styling for the report
- `TREC_Report_Filled_Improved.html` - Generated output (created by script)

## Usage

### Prerequisites
```bash
pip install beautifulsoup4
```

### Run the Pipeline
```bash
python populate_trec_complete.py
```

The script will:
1. Load `inspection.json` and `TREC_Report_All.html`
2. Populate header fields (client, date, address, inspector, licenses)
3. Process all sections and line items from inspection.json
4. Map line items to appropriate TREC sections
5. Remove empty sections/items
6. Format comments, images, and videos
7. Update page numbers
8. Save to `TREC_Report_Filled_Improved.html`

## Features

### ✅ Complete Processing
- Processes **ALL sections** from `inspection.json`
- Maps line items to TREC sections (I-VI)
- Handles multiple items mapping to same TREC item (adds as "Additional Finding")

### ✅ Smart Mapping
Comprehensive mapping covers:
- **Structural Systems** (Section I)
- **Electrical Systems** (Section II)
- **HVAC Systems** (Section III)
- **Plumbing Systems** (Section IV)
- **Appliances** (Section V)
- **Optional Systems** (Section VI)

### ✅ Empty Removal
- Automatically removes TREC sections with no data
- Skips line items with no `inspectionStatus` and no comments

### ✅ Proper Formatting
- Comments formatted with locations
- Images sized correctly (250x200px max)
- Videos embedded with controls
- No scrollable content - everything expands naturally
- Page numbers automatically updated

### ✅ Header Population
All header fields populated from `inspection.json`:
- Client name
- Inspection date
- Property address
- Inspector name
- Inspector TREC license
- Sponsor name (if applicable)
- Sponsor TREC license (if applicable)

## Output

The generated `TREC_Report_Filled_Improved.html` file:
- Contains all populated sections with data
- Has empty sections automatically removed
- Is properly formatted for viewing/printing
- Ready to be converted to PDF if needed

## Customization

### Adding New Line Item Mappings

Edit `populate_trec_complete.py` and add entries to `LINE_ITEM_MAPPING`:

```python
LINE_ITEM_MAPPING = {
    "Your Line Item Name": ("TREC_CODE", SECTION_INDEX, "TREC Item Title"),
    # Example:
    "Custom Item": ("A", 0, "Foundations"),
}
```

**Section Indices:**
- `0` = I. Structural Systems
- `1` = II. Electrical Systems
- `2` = III. HVAC Systems
- `3` = IV. Plumbing Systems
- `4` = V. Appliances
- `5` = VI. Optional Systems

## Technical Details

### Data Structure
- **Input JSON**: Follows inspection.json structure with `inspection.sections[]` containing `lineItems[]` with `comments[]`
- **HTML Template**: TREC standard form structure with `.item` elements and `.comments` containers
- **Mapping**: Hardcoded in `LINE_ITEM_MAPPING` dictionary for performance

### CSS Styling
- Overrides fixed heights to allow natural expansion
- Images constrained to 250x200px max
- Comments and media properly spaced
- Page breaks handled automatically

## Notes

- The script uses BeautifulSoup4 for HTML parsing and manipulation
- All data is extracted directly from `inspection.json`
- Empty sections/items are automatically filtered out
- The output maintains the TREC form structure and styling

