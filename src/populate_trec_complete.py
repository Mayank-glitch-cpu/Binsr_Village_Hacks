#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete TREC HTML Populator
Processes ALL sections from inspection.json, removes empty items, uses actual names
"""
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import re
import html

try:
    from bs4 import BeautifulSoup, Tag
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False
    print("Error: BeautifulSoup4 is required. Install with: pip install beautifulsoup4")
    exit(1)

# Comprehensive mapping of inspection line items to TREC sections/items
TREC_MAPPING = {
    # Structural Systems (Section I - index 0)
    "structural": {
        "Foundation": ("A", 0),
        "Grading and Drainage": ("B", 0),
        "Roof Covering Materials": ("C", 0),
        "Roof Structures and Attics": ("D", 0),
        "Walls": ("E", 0),
        "Ceilings and Floors": ("F", 0),
        "Doors": ("G", 0),
        "Windows": ("H", 0),
        "Stairways": ("I", 0),
        "Fireplaces and Chimneys": ("J", 0),
        "Porches, Balconies, Decks, and Carports": ("K", 0),
        "Other": ("L", 0),
    },
    # Electrical Systems (Section II - index 1)
    "electrical": {
        "Service Entrance and Panels": ("A", 1),
        "Branch Circuits": ("B", 1),
        "Other": ("C", 1),
    },
    # HVAC Systems (Section III - index 2)
    "hvac": {
        "Heating Equipment": ("A", 2),
        "Cooling Equipment": ("B", 2),
        "Duct Systems": ("C", 2),
        "Other": ("D", 2),
    },
    # Plumbing Systems (Section IV - index 3)
    "plumbing": {
        "Plumbing Supply": ("A", 3),
        "Drains, Wastes, and Vents": ("B", 3),
        "Water Heating Equipment": ("C", 3),
        "Hydro-Massage Therapy Equipment": ("D", 3),
        "Gas Distribution": ("E", 3),
        "Other": ("F", 3),
    },
    # Appliances (Section V - index 4)
    "appliances": {
        "Dishwashers": ("A", 4),
        "Food Waste Disposers": ("B", 4),
        "Range Hood": ("C", 4),
        "Ranges, Cooktops, and Ovens": ("D", 4),
        "Microwave Ovens": ("E", 4),
        "Mechanical Exhaust": ("F", 4),
        "Garage Door Operators": ("G", 4),
        "Dryer Exhaust": ("H", 4),
        "Other": ("I", 4),
    },
    # Optional Systems (Section VI - index 5)
    "optional": {
        "Landscape Irrigation": ("A", 5),
        "Swimming Pools": ("B", 5),
        "Outbuildings": ("C", 5),
        "Private Water Wells": ("D", 5),
        "Private Sewage Disposal": ("E", 5),
        "Other Built-in Appliances": ("F", 5),
        "Other": ("G", 5),
    }
}

# Line item name to TREC mapping
LINE_ITEM_MAPPING = {
    # Structural
    "Decks and Stairways": ("K", 0, "Porches, Balconies, Decks, and Carports"),
    "Ground-Level Entry Structures": ("K", 0, "Porches, Balconies, Decks, and Carports"),
    "Exterior Cladding and Trim": ("E", 0, "Walls (Interior and Exterior)"),
    "Exterior Wall Cladding and Finishes": ("E", 0, "Walls (Interior and Exterior)"),
    "Window Systems and Sealing": ("H", 0, "Windows"),
    "Window Systems and Flashing": ("H", 0, "Windows"),
    "Chimney Structures": ("J", 0, "Fireplaces and Chimneys"),
    "Chimney Systems": ("J", 0, "Fireplaces and Chimneys"),
    "Eaves and Soffit Components": ("K", 0, "Porches, Balconies, Decks, and Carports"),
    "Paved Surfaces and Walkways": ("K", 0, "Porches, Balconies, Decks, and Carports"),
    "Perimeter Fencing and Gates": ("L", 0, "Other"),
    "Exterior Elevated Structures": ("K", 0, "Porches, Balconies, Decks, and Carports"),
    "Exterior Entryways": ("G", 0, "Doors (Interior and Exterior)"),
    "Site Grading and Drainage": ("B", 0, "Grading and Drainage"),
    "Roof Covering Materials": ("C", 0, "Roof Covering Materials"),
    "Roof Structures and Attics": ("D", 0, "Roof Structures and Attics"),
    "Overall Roof Condition": ("C", 0, "Roof Covering Materials"),
    "Roofing Material Integrity": ("C", 0, "Roof Covering Materials"),
    "Flashing System Integrity": ("C", 0, "Roof Covering Materials"),
    "Roof Flashing Components": ("C", 0, "Roof Covering Materials"),
    "Roof Penetrations and Ventilation": ("D", 0, "Roof Structures and Attics"),
    "Exterior Drainage Systems": ("B", 0, "Grading and Drainage"),
    "Rainwater Management Systems": ("B", 0, "Grading and Drainage"),
    
    # HVAC
    "Outdoor HVAC Unit": ("B", 2, "Cooling Equipment"),
    "Outdoor Air Conditioning Unit": ("B", 2, "Cooling Equipment"),
    
    # Plumbing
    "Exterior Water Taps and Drainage Access": ("A", 3, "Plumbing Supply, Distribution Systems and Fixtures"),
    "Bathtub and Shower Systems": ("A", 3, "Plumbing Supply, Distribution Systems and Fixtures"),
    
    # Appliances
    "Food Waste Disposer": ("B", 4, "Food Waste Disposers"),
    "Integrated Appliances": ("I", 4, "Other"),
    "Kitchen Ventilation": ("C", 4, "Range Hood and Exhaust Systems"),
    "Microwave Oven": ("E", 4, "Microwave Ovens"),
    "Dishwashing Unit": ("A", 4, "Dishwashers"),
    "Laundry Appliances": ("H", 4, "Dryer Exhaust Systems"),
    "Wine Refrigerator": ("I", 4, "Other"),
    "Refrigeration Unit": ("I", 4, "Other"),
    
    # Electrical
    "Electrical Receptacles, Switches, and Signaling Devices": ("B", 1, "Branch Circuits, Connected Devices, and Fixtures"),
    "Electrical Conductors and Wiring": ("B", 1, "Branch Circuits, Connected Devices, and Fixtures"),
    
    # Structural
    "Interior Door Systems": ("G", 0, "Doors (Interior and Exterior)"),
    "Window Assemblies": ("H", 0, "Windows"),
    "Window Systems": ("H", 0, "Windows"),
    "Interior Wall Systems": ("E", 0, "Walls (Interior and Exterior)"),
    "Interior Flooring Surfaces": ("F", 0, "Ceilings and Floors"),
    "Ceiling Surfaces": ("F", 0, "Ceilings and Floors"),
    "Floor Coverings": ("F", 0, "Ceilings and Floors"),
    "Exterior Door Systems": ("G", 0, "Doors (Interior and Exterior)"),
    "Subflooring": ("F", 0, "Ceilings and Floors"),
    "Main Structural Supports": ("A", 0, "Foundations"),
    "Floor Joist System": ("F", 0, "Ceilings and Floors"),
    "General Structural Information": ("A", 0, "Foundations"),
    "Substructure Entry": ("A", 0, "Foundations"),
    "Outdoor Living Area Covers": ("K", 0, "Porches, Balconies, Decks, and Carports"),
    "Exterior Plantings": ("L", 0, "Other"),
    "Landscape Retaining Structures": ("B", 0, "Grading and Drainage"),
    
    # HVAC
    "Indoor HVAC Unit": ("A", 2, "Heating Equipment"),
    
    # Optional - can map to Other
    "Crawlspace Assessment": ("L", 0, "Other"),
    "Interior Cabinetry and Countertops": ("L", 0, "Other"),
    "Interior Passageways": ("L", 0, "Other"),
    
    # General/Info sections - map to appropriate fields
    "Report Context": None,  # Skip - informational only
    "General Information": None,  # Skip - informational only, not a TREC line item
    "Site and Property Context": ("B", 0, "Grading and Drainage"),  # Keep this mapping
}

class CompleteTRECPopulator:
    """Populates TREC HTML form with complete inspection data"""
    
    def __init__(self, html_path: str, inspection_path: str):
        self.html_path = html_path
        self.inspection_path = inspection_path
        
        # Load files
        with open(html_path, 'r', encoding='utf-8') as f:
            self.soup = BeautifulSoup(f.read(), 'html.parser')
        
        with open(inspection_path, 'r', encoding='utf-8') as f:
            self.inspection_data = json.load(f)
        
        # Add CSS for better formatting
        self.add_formatting_css()
    
    def add_formatting_css(self):
        """Add CSS styles for better comment and media formatting"""
        style_tag = self.soup.find('style')
        if not style_tag:
            head = self.soup.find('head')
            if head:
                style_tag = self.soup.new_tag('style')
                head.append(style_tag)
        
        css = """
        /* Ensure all pages match pages 1-2 height and structure */
        .page {
            min-height: 11in !important;
            display: flex !important;
            flex-direction: column !important;
            overflow: visible !important;
        }
        
        /* Content area should expand to fill available space like pages 1-2 */
        .page .content {
            flex: 1 !important;
            display: flex !important;
            flex-direction: column !important;
            overflow: visible !important;
            padding: 0.6in !important;
        }
        
        /* Ensure pages 3+ match padding-bottom pattern of pages 1-2 */
        .page:nth-child(n+3) .content {
            padding-bottom: calc(0.6in * 0.7) !important;
        }
        
        /* Footer should stay at bottom */
        .footer {
            flex-shrink: 0;
            margin: 0 0.6in 0.6in 0.6in;
        }
        
        /* Content should flow naturally - no clipping */
        .page .content > * {
            flex-shrink: 0;
        }
        
        /* Comment formatting */
        .comment-item {
            margin: 8px 0;
            padding: 4px 0;
            line-height: 1.5;
            page-break-inside: avoid;
        }
        .comment-item p {
            margin: 4px 0;
        }
        
        /* Media container - prevent overflow, allow page breaks */
        .media-container {
            margin: 10px 0;
            clear: both;
            page-break-inside: avoid;
            break-inside: avoid;
            max-width: 100%;
        }
        .media-container img,
        .media-container video {
            max-width: 250px !important;
            max-height: 200px !important;
            width: auto !important;
            height: auto !important;
            display: block;
            clear: both;
            border: 1px solid #ddd;
            padding: 2px;
            margin: 8px 0;
            object-fit: contain;
        }
        
        /* Comments - allow natural growth */
        .comments {
            word-wrap: break-word;
            height: auto !important;
            min-height: 0.5in;
            overflow: visible !important;
            max-height: none !important;
        }
        .comments-inline {
            height: auto !important;
            overflow: visible !important;
        }
        
        /* Items - prevent awkward page breaks */
        .item {
            page-break-inside: avoid;
            break-inside: avoid;
            min-height: auto;
            overflow: visible;
        }
        .item .comments[contenteditable="true"] {
            height: auto !important;
            min-height: 0.5in;
            overflow: visible !important;
        }
        
        /* Section titles - keep with content */
        .section-title {
            page-break-after: avoid;
            break-after: avoid;
        }
        
        /* Print media - proper page breaks and consistent heights */
        @media print {
            @page {
                size: letter;
                margin: 0;
            }
            .page {
                min-height: 11in !important;
                height: auto !important;
                page-break-after: always;
                page-break-inside: avoid;
                break-inside: avoid;
                overflow: visible !important;
            }
            .page:last-child {
                page-break-after: auto;
            }
            .page .content {
                overflow: visible !important;
                height: auto !important;
            }
            .item {
                page-break-inside: avoid;
                break-inside: avoid;
                orphans: 3;
                widows: 3;
            }
            .media-container {
                page-break-inside: avoid;
                break-inside: avoid;
            }
            .section-title {
                page-break-after: avoid;
                break-after: avoid;
            }
        }
        
        /* Screen view - allow natural flow, no clipping */
        @media screen {
            .page {
                overflow: visible !important;
            }
            .page .content {
                overflow: visible !important;
            }
        }
        """
        
        if style_tag:
            # Append CSS if style tag already has content, otherwise set it
            existing_css = style_tag.string if style_tag.string else ""
            style_tag.string = existing_css + "\n" + css if existing_css else css
    
    def get_value_from_path(self, data: Dict[str, Any], path: List[str]) -> Any:
        """Safely get nested value from JSON"""
        current = data
        for key in path:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current
    
    def transform_value(self, value: Any, transform_type: Optional[str] = None) -> str:
        """Transform value based on type"""
        if value is None:
            return ""
        
        if transform_type == "date":
            try:
                if isinstance(value, (int, float)):
                    dt = datetime.fromtimestamp(value / 1000)
                else:
                    dt = datetime.fromisoformat(str(value))
                return dt.strftime("%m/%d/%Y")
            except:
                return str(value)
        
        return str(value)
    
    def check_status_checkbox(self, checks_container: Tag, status: str) -> None:
        """Check the appropriate checkbox based on status"""
        checkboxes = checks_container.select('input[type="checkbox"]')
        status_map = {"I": 0, "NI": 1, "NP": 2, "D": 3}
        idx = status_map.get(status.upper(), -1)
        if 0 <= idx < len(checkboxes):
            checkboxes[idx]['checked'] = 'checked'
    
    def format_comment_text(self, comment: Dict) -> str:
        """Format a single comment's text"""
        text = comment.get('text') or comment.get('commentText') or comment.get('value') or ''
        location = comment.get('location', '').strip()
        
        parts = []
        
        if location:
            parts.append(f'<p><strong>Location:</strong> {html.escape(location)}</p>')
        
        if text:
            parts.append(f'<p>{html.escape(text)}</p>')
        
        return ''.join(parts)
    
    def format_all_comments(self, comments: List[Dict]) -> str:
        """Format all comments for a line item"""
        if not comments:
            return ''
        
        # Sort by order
        sorted_comments = sorted(comments, key=lambda c: c.get('order', 0))
        
        html_parts = []
        for idx, comment in enumerate(sorted_comments):
            # Format comment text
            comment_html = self.format_comment_text(comment)
            if comment_html:
                html_parts.append(f'<div class="comment-item">{comment_html}</div>')
            
            # Add media
            photos = comment.get('photos', [])
            for photo in photos:
                url = photo.get('url', '')
                caption = photo.get('caption') or photo.get('description') or ''
                if url:
                    img_style = "max-width: 250px; max-height: 200px; margin: 8px 0; display: block; clear: both; border: 1px solid #ddd; padding: 2px;"
                    img_html = f'<img src="{html.escape(url)}" alt="{html.escape(caption)}" style="{img_style}" />'
                    caption_text = f'<p style="font-size: 0.85em; font-style: italic; margin: 4px 0;"><em>{html.escape(caption)}</em></p>' if caption else ''
                    html_parts.append(f'<div class="media-container" style="margin: 10px 0; clear: both;">{caption_text}{img_html}</div>')
            
            videos = comment.get('videos', [])
            for video in videos:
                url = video.get('url', '')
                if url:
                    video_style = "max-width: 250px; max-height: 200px; margin: 8px 0; display: block; clear: both;"
                    video_html = f'<video src="{html.escape(url)}" controls style="{video_style}"></video>'
                    html_parts.append(f'<div class="media-container" style="margin: 10px 0; clear: both;">{video_html}</div>')
            
            if idx < len(sorted_comments) - 1:
                html_parts.append('<hr style="margin: 12px 0; border: none; border-top: 1px solid #eee;"/>')
        
        return '\n'.join(html_parts)
    
    def find_trec_item(self, section_index: int, item_code: str, item_title: str) -> Optional[Tag]:
        """Find TREC item element"""
        sections = self.soup.select('div.section-title')
        if section_index >= len(sections):
            return None
        
        section = sections[section_index]
        current = section.find_next_sibling()
        items = []
        
        while current:
            if current.name == 'div' and 'section-title' in current.get('class', []):
                break
            if current.name == 'div' and 'item' in current.get('class', []):
                items.append(current)
            current = current.find_next_sibling()
        
        # Find by code
        for item in items:
            code_elem = item.select_one('.item-title .code')
            if code_elem and code_elem.text.strip() == item_code + '.':
                return item
        
        # Find by title keywords
        title_keywords = [kw.lower() for kw in item_title.split()]
        for item in items:
            title_elem = item.select_one('.item-title')
            if title_elem:
                title_text = re.sub(r'^[A-Z]\.\s*', '', title_elem.text.strip(), count=1).lower()
                if any(kw in title_text for kw in title_keywords):
                    return item
        
        return items[0] if items else None
    
    def is_empty_item(self, line_item: Dict) -> bool:
        """Check if line item is empty (no status and no comments)"""
        has_status = line_item.get('inspectionStatus') is not None
        has_comments = len(line_item.get('comments', [])) > 0
        return not has_status and not has_comments
    
    def populate_header_fields(self) -> None:
        """Populate header fields from inspection.json"""
        inspection = self.inspection_data.get('inspection', {})
        client_info = inspection.get('clientInfo', {})
        address_info = inspection.get('address', {})
        inspector_info = inspection.get('inspector', {})
        schedule = inspection.get('schedule', {})
        account = self.inspection_data.get('account', {})
        
        # Client name
        client_elem = self.soup.find(id='client')
        if client_elem:
            client_name = client_info.get('name', '')
            client_elem['value'] = client_name
            print(f"   Client: {client_name}")
        
        # Date of Inspection
        date_elem = self.soup.find(id='date')
        if date_elem:
            date_val = schedule.get('date')
            if date_val:
                formatted_date = self.transform_value(date_val, 'date')
                date_elem['value'] = formatted_date
                print(f"   Date: {formatted_date}")
        
        # Address of Inspected Property
        address_elem = self.soup.find(id='address')
        if address_elem:
            full_address = address_info.get('fullAddress', '')
            address_elem['value'] = full_address
            print(f"   Address: {full_address}")
        
        # Name of Inspector
        inspector_elem = self.soup.find(id='inspector')
        if inspector_elem:
            inspector_name = inspector_info.get('name', '')
            inspector_elem['value'] = inspector_name
            print(f"   Inspector: {inspector_name}")
        
        # TREC License # (Inspector)
        trec1_elem = self.soup.find(id='trec1')
        if trec1_elem:
            trec_license = inspector_info.get('id', '')
            trec1_elem['value'] = trec_license
            print(f"   Inspector TREC License: {trec_license}")
        
        # Name of Sponsor (if applicable)
        sponsor_elem = self.soup.find(id='sponsor')
        if sponsor_elem and account:
            sponsor_name = account.get('companyName', '')
            if not sponsor_name:
                # Try alternative paths
                sponsor_name = account.get('name', '')
            if sponsor_name:
                sponsor_elem['value'] = sponsor_name
                print(f"   Sponsor: {sponsor_name}")
        
        # TREC License # (Sponsor)
        trec2_elem = self.soup.find(id='trec2')
        if trec2_elem and account:
            sponsor_license = account.get('id', '')
            if sponsor_license:
                trec2_elem['value'] = sponsor_license
                print(f"   Sponsor TREC License: {sponsor_license}")
    
    def populate_all_sections(self) -> None:
        """Process all sections from inspection.json"""
        sections = self.inspection_data.get('inspection', {}).get('sections', [])
        
        processed_items = {}  # Track processed TREC items
        
        for section in sections:
            section_name = section.get('name', '')
            line_items = section.get('lineItems', [])
            
            # Filter out empty items
            non_empty_items = [li for li in line_items if not self.is_empty_item(li)]
            
            if not non_empty_items:
                print(f"[SKIP] Section '{section_name}' has no data")
                continue
            
            print(f"\nProcessing section: {section_name}")
            print(f"  {len(non_empty_items)} line items with data")
            
            for line_item in non_empty_items:
                line_item_name = line_item.get('name', '')
                
                # Get mapping
                mapping = LINE_ITEM_MAPPING.get(line_item_name)
                
                # Check if explicitly set to None (should be skipped)
                if mapping is None:
                    print(f"  [SKIP] Skipping informational item: {line_item_name}")
                    continue
                
                if not mapping:
                    # Try fuzzy matching
                    mapping = self.fuzzy_match_line_item(line_item_name)
                
                if not mapping:
                    print(f"  [SKIP] No mapping for: {line_item_name}")
                    continue
                
                item_code, section_idx, item_title = mapping
                item_key = f"{section_idx}_{item_code}"
                
                # Find TREC item
                trec_item = self.find_trec_item(section_idx, item_code, item_title)
                if not trec_item:
                    print(f"  [SKIP] Could not find TREC item: {item_code}. {item_title}")
                    continue
                
                print(f"  [OK] {line_item_name} -> {item_code}. {item_title}")
                
                # Handle multiple items mapping to same TREC item
                if item_key in processed_items:
                    # Append as "Additional Finding"
                    existing_item = processed_items[item_key]
                    comments_container = existing_item.select_one('.comments-inline .comments')
                    if comments_container:
                        comments = line_item.get('comments', [])
                        if comments:
                            existing_html = comments_container.decode_contents()
                            new_html = self.format_all_comments(comments)
                            if new_html:
                                separator = '<hr style="margin: 12px 0; border: none; border-top: 2px solid #ccc;"/><p style="font-weight: bold; margin: 8px 0;">Additional Finding:</p>'
                                combined_html = existing_html + separator + new_html
                                comments_container.clear()
                                comments_container.append(BeautifulSoup(combined_html, 'html.parser'))
                else:
                    processed_items[item_key] = trec_item
                    
                    # Set status
                    checks_container = trec_item.select_one('.checks')
                    if checks_container:
                        status = line_item.get('inspectionStatus')
                        if status:
                            self.check_status_checkbox(checks_container, status)
                    
                    # Add comments
                    comments_container = trec_item.select_one('.comments-inline .comments')
                    if comments_container:
                        comments = line_item.get('comments', [])
                        if comments:
                            comments_html = self.format_all_comments(comments)
                            if comments_html:
                                comments_container.clear()
                                comments_container['style'] = 'overflow: visible !important; height: auto !important; min-height: 0.5in; max-height: none !important;'
                                comments_container.append(BeautifulSoup(comments_html, 'html.parser'))
                                print(f"    Added {len(comments)} comment(s)")
                                
                                comments_inline = trec_item.select_one('.comments-inline')
                                if comments_inline:
                                    comments_inline['style'] = 'height: auto; overflow: visible;'
    
    def fuzzy_match_line_item(self, line_item_name: str) -> Optional[tuple]:
        """Try to match line item using keywords"""
        name_lower = line_item_name.lower()
        
        # Try keyword matching
        for mapped_name, (code, idx, title) in LINE_ITEM_MAPPING.items():
            mapped_lower = mapped_name.lower()
            # Check if any significant words match
            mapped_words = set(mapped_lower.split())
            name_words = set(name_lower.split())
            
            if len(mapped_words & name_words) >= 2:  # At least 2 words match
                return (code, idx, title)
        
        return None
    
    def remove_empty_sections(self) -> None:
        """Remove TREC sections that have no populated items"""
        sections = self.soup.select('div.section-title')
        
        for section in sections:
            section_div = section.parent if section.parent else None
            if not section_div:
                continue
            
            # Find all items in this section
            current = section.find_next_sibling()
            has_data = False
            
            while current:
                if current.name == 'div' and 'section-title' in current.get('class', []):
                    break
                if current.name == 'div' and 'item' in current.get('class', []):
                    # Check if item has data
                    comments = current.select_one('.comments[contenteditable="true"]')
                    if comments and comments.get_text(strip=True):
                        has_data = True
                        break
                    checks = current.select_one('.checks input[checked]')
                    if checks:
                        has_data = True
                        break
                current = current.find_next_sibling()
            
            if not has_data:
                # Remove this section and its items
                print(f"[REMOVE] Empty section: {section.text.strip()}")
                # Find end of section (next section-title or page end)
                current = section.find_next_sibling()
                elements_to_remove = [section]
                
                while current:
                    if current.name == 'div' and 'section-title' in current.get('class', []):
                        break
                    if current.name == 'div' and 'item' in current.get('class', []):
                        elements_to_remove.append(current)
                    current = current.find_next_sibling()
                
                for elem in elements_to_remove:
                    elem.decompose()
    
    def update_page_numbers(self) -> int:
        """Update page numbers"""
        pages = self.soup.select('.page')
        total_pages = len(pages)
        
        page_count_inputs = self.soup.select('.pagecount-center input[type="text"]')
        for page_input in page_count_inputs:
            page_input['value'] = str(total_pages)
        
        return total_pages
    
    def save(self, output_path: str) -> None:
        """Save populated HTML"""
        self.update_page_numbers()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(str(self.soup.prettify()))

def main():
    """Main function"""
    print("=" * 70)
    print("Complete TREC HTML Populator")
    print("=" * 70)
    
    html_template = "TREC_Report_All.html"
    inspection_json = "inspection.json"
    output_file = "TREC_Report_Filled_Improved.html"
    
    try:
        populator = CompleteTRECPopulator(html_template, inspection_json)
        
        print("\n[1/4] Populating header fields...")
        populator.populate_header_fields()
        print("   [OK] Header fields populated")
        
        print("\n[2/4] Populating all sections...")
        populator.populate_all_sections()
        print("   [OK] All sections processed")
        
        print("\n[3/4] Removing empty sections...")
        populator.remove_empty_sections()
        print("   [OK] Empty sections removed")
        
        print(f"\n[4/4] Saving to {output_file}...")
        populator.save(output_file)
        print(f"   [OK] Saved to {output_file}")
        
        print("\n" + "=" * 70)
        print(f"[SUCCESS] Populated HTML saved to: {output_file}")
        print("You can now open the file in a web browser to view the filled form.")
        
    except FileNotFoundError as e:
        print(f"Error: File not found: {e}")
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

