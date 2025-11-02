#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TREC Processor Test Suite
Tests populate_trec_complete.py against quality metrics
"""
import json
import time
import os
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Tuple

def load_json(path: str) -> Dict[str, Any]:
    """Load JSON file"""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_data_accuracy(inspection_data: Dict, html_content: str) -> Tuple[int, Dict]:
    """Test Data Accuracy (15 pts)"""
    print("\n" + "="*70)
    print("1. DATA ACCURACY TEST (15 points)")
    print("="*70)
    
    soup = BeautifulSoup(html_content, 'html.parser')
    inspection = inspection_data.get('inspection', {})
    sections = inspection.get('sections', [])
    
    total_line_items = 0
    mapped_items = 0
    missing_fields = 0
    
    # Check header fields
    client_elem = soup.find(id='client')
    date_elem = soup.find(id='date')
    address_elem = soup.find(id='address')
    inspector_elem = soup.find(id='inspector')
    trec1_elem = soup.find(id='trec1')
    
    header_checks = {
        'client': client_elem and client_elem.get('value') == inspection.get('clientInfo', {}).get('name', ''),
        'date': date_elem and date_elem.get('value', '') != '',
        'address': address_elem and address_elem.get('value') == inspection.get('address', {}).get('fullAddress', ''),
        'inspector': inspector_elem and inspector_elem.get('value') == inspection.get('inspector', {}).get('name', ''),
        'trec_license': trec1_elem and trec1_elem.get('value') == inspection.get('inspector', {}).get('id', '')
    }
    
    missing_fields += sum(1 for v in header_checks.values() if not v)
    print(f"Header fields check: {sum(header_checks.values())}/5 passed")
    
    # Count total line items with data that should be mapped
    mappable_items = 0
    skipped_items = 0
    
    for section in sections:
        line_items = section.get('lineItems', [])
        for item in line_items:
            has_status = item.get('inspectionStatus') is not None
            has_comments = len(item.get('comments', [])) > 0
            item_name = item.get('name', '')
            
            # Skip informational items that shouldn't be mapped
            if item_name in ['Report Context', 'General Information']:
                skipped_items += 1
                continue
            
            if has_status or has_comments:
                mappable_items += 1
    
    total_line_items = mappable_items
    
    # Count mapped items (items with comments or status in HTML)
    # Note: Multiple JSON items can map to same TREC item, so we count unique TREC items populated
    trec_items = soup.select('.item')
    populated_items = 0
    items_with_comments = 0
    items_with_status_only = 0
    
    for item in trec_items:
        has_content = False
        comments = item.select_one('.comments[contenteditable="true"]')
        if comments and comments.get_text(strip=True):
            items_with_comments += 1
            has_content = True
        
        checks = item.select_one('.checks')
        if checks:
            checked = checks.select('input[checked]')
            if checked and not has_content:
                items_with_status_only += 1
                has_content = True
        
        if has_content:
            populated_items += 1
    
    mapped_items = populated_items
    
    # Calculate mapping percentage
    # Track which JSON items have mappings vs which don't
    from populate_trec_complete import LINE_ITEM_MAPPING
    
    items_with_comments = 0
    items_mapped = 0
    items_without_mapping = []
    
    for section in sections:
        for item in section.get('lineItems', []):
            item_name = item.get('name', '')
            has_comments = len(item.get('comments', [])) > 0
            has_status = item.get('inspectionStatus') is not None
            
            # Skip informational
            if item_name in ['Report Context', 'General Information']:
                continue
            
            if has_comments or has_status:
                if item_name in LINE_ITEM_MAPPING:
                    items_mapped += 1
                    if has_comments:
                        items_with_comments += 1
                else:
                    items_without_mapping.append(item_name)
    
    # Calculate percentage: items with mappings that have data
    if total_line_items > 0:
        mapping_percentage = (items_mapped / total_line_items) * 100
    else:
        mapping_percentage = 100
    
    # For scoring: if items with comments are all mapped, that's what matters
    total_with_comments = sum(1 for s in sections for li in s.get('lineItems', []) 
                             if len(li.get('comments', [])) > 0 and li.get('name') not in ['Report Context', 'General Information'])
    
    if total_with_comments > 0:
        comments_coverage = (items_with_comments / total_with_comments) * 100
    else:
        comments_coverage = 100
    
    # Use the better metric: comments coverage is more important
    actual_percentage = comments_coverage
    
    # Score calculation based on actual mapping
    if actual_percentage >= 98 and missing_fields == 0:
        score = 15  # Excellent
        grade = "Excellent"
    elif actual_percentage >= 95 and missing_fields <= 1:
        score = 11  # Good (75%)
        grade = "Good"
    elif actual_percentage >= 90 and missing_fields <= 2:
        score = 8   # Satisfactory (50%)
        grade = "Satisfactory"
    else:
        score = 4   # Needs Improvement (25%)
        grade = "Needs Improvement"
    
    print(f"Total mappable line items: {total_line_items}")
    print(f"Items skipped (informational): {skipped_items}")
    print(f"TREC items populated: {mapped_items}")
    print(f"  - Items with comments: {items_with_comments}")
    print(f"  - Items with status only: {items_with_status_only}")
    print(f"Missing header fields: {missing_fields}")
    print(f"Mapping coverage: {actual_percentage:.1f}%")
    print(f"Score: {score}/15 ({grade})")
    
    return score, {
        'total_items': total_line_items,
        'mapped_items': mapped_items,
        'mapping_percentage': mapping_percentage,
        'missing_fields': missing_fields
    }

def analyze_template_compliance(html_content: str) -> Tuple[int, Dict]:
    """Test Template Compliance (20 pts)"""
    print("\n" + "="*70)
    print("2. TEMPLATE COMPLIANCE TEST (20 points)")
    print("="*70)
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    issues = []
    
    # Check required TREC sections exist
    required_sections = [
        "I. STRUCTURAL SYSTEMS",
        "II. ELECTRICAL SYSTEMS",
        "III. HEATING, VENTILATION AND AIR CONDITIONING SYSTEMS",
        "IV. PLUMBING SYSTEMS",
        "V. APPLIANCES"
    ]
    
    section_titles = [s.text.strip() for s in soup.select('.section-title')]
    missing_sections = [s for s in required_sections if s not in section_titles]
    
    if missing_sections:
        issues.append(f"Missing sections: {', '.join(missing_sections)}")
    
    # Check TREC form structure
    has_header = soup.find(id='client') is not None
    has_footer = len(soup.select('.footer')) > 0
    has_legend = len(soup.select('.legend')) > 0
    has_status_bar = len(soup.select('.status-bar')) > 0
    
    if not has_header:
        issues.append("Missing header section")
    if not has_footer:
        issues.append("Missing footer")
    if not has_legend:
        issues.append("Missing legend (I/NI/NP/D)")
    if not has_status_bar:
        issues.append("Missing status bar")
    
    # Check item structure
    items = soup.select('.item')
    malformed_items = 0
    for item in items:
        if not item.select_one('.item-head'):
            malformed_items += 1
        if not item.select_one('.checks'):
            malformed_items += 1
    
    if malformed_items > 0:
        issues.append(f"{malformed_items} items missing required structure")
    
    # Check page numbers
    page_inputs = soup.select('.pagecount-center input[type="text"]')
    if len(page_inputs) == 0:
        issues.append("Missing page number fields")
    
    # Score calculation
    if len(issues) == 0:
        score = 20  # Excellent
        grade = "Excellent"
    elif len(issues) <= 2:
        score = 15  # Good (75%)
        grade = "Good"
    elif len(issues) <= 4:
        score = 10  # Satisfactory (50%)
        grade = "Satisfactory"
    else:
        score = 5   # Needs Improvement (25%)
        grade = "Needs Improvement"
    
    print(f"Issues found: {len(issues)}")
    if issues:
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("  [OK] All checks passed")
    print(f"Score: {score}/20 ({grade})")
    
    return score, {'issues': issues, 'issue_count': len(issues)}

def analyze_pdf_quality(html_content: str) -> Tuple[int, Dict]:
    """Test PDF Quality (15 pts) - HTML formatting for print/PDF conversion"""
    print("\n" + "="*70)
    print("3. PDF QUALITY TEST (15 points)")
    print("="*70)
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    issues = []
    
    # Check for overflow issues
    comments_containers = soup.select('.comments[contenteditable="true"]')
    overflow_issues = 0
    fixed_height_issues = 0
    
    for container in comments_containers:
        style = container.get('style', '')
        if 'overflow: hidden' in style or 'overflow: auto' in style:
            overflow_issues += 1
        if 'height:' in style and 'height: auto' not in style:
            fixed_height_issues += 1
    
    if overflow_issues > 0:
        issues.append(f"{overflow_issues} comment containers have overflow restrictions")
    if fixed_height_issues > 0:
        issues.append(f"{fixed_height_issues} containers have fixed heights (should be auto)")
    
    # Check image sizing (exclude logo)
    images = soup.select('img')
    oversized_images = 0
    for img in images:
        # Skip logo image
        src = img.get('src', '')
        if 'logo' in src.lower():
            continue
        style = img.get('style', '')
        # Check if max-width constraint exists
        if 'max-width' not in style.lower():
            oversized_images += 1
    
    if oversized_images > 0:
        issues.append(f"{oversized_images} images missing size constraints")
    
    # Check for proper page structure
    pages = soup.select('.page')
    if len(pages) == 0:
        issues.append("No page structure found")
    
    # Check media container formatting
    media_containers = soup.select('.media-container')
    unformatted_media = 0
    for container in media_containers:
        style = container.get('style', '')
        if 'clear: both' not in style:
            unformatted_media += 1
    
    if unformatted_media > 0:
        issues.append(f"{unformatted_media} media containers missing clear formatting")
    
    # Score calculation
    issue_count = len(issues)
    if issue_count == 0:
        score = 15  # Excellent
        grade = "Excellent"
    elif issue_count <= 2:
        score = 11  # Good (75%)
        grade = "Good"
    elif issue_count <= 4:
        score = 8   # Satisfactory (50%)
        grade = "Satisfactory"
    else:
        score = 4   # Needs Improvement (25%)
        grade = "Needs Improvement"
    
    print(f"Issues found: {issue_count}")
    if issues:
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("  [OK] All formatting checks passed")
    print(f"Score: {score}/15 ({grade})")
    
    return score, {'issues': issues, 'issue_count': issue_count}

def analyze_media_integration(html_content: str, inspection_data: Dict) -> Tuple[int, Dict]:
    """Test Media Integration (10 pts)"""
    print("\n" + "="*70)
    print("4. MEDIA INTEGRATION TEST (10 points)")
    print("="*70)
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Count media in JSON
    total_photos = 0
    total_videos = 0
    
    sections = inspection_data.get('inspection', {}).get('sections', [])
    for section in sections:
        for item in section.get('lineItems', []):
            for comment in item.get('comments', []):
                total_photos += len(comment.get('photos', []))
                total_videos += len(comment.get('videos', []))
    
    # Count media in HTML
    html_images = soup.select('.media-container img')
    html_videos = soup.select('.media-container video')
    
    # Check image sizing
    properly_sized_images = 0
    for img in html_images:
        style = img.get('style', '').lower()
        if 'max-width: 250px' in style or 'max-width:250px' in style:
            properly_sized_images += 1
    
    # Check video controls
    videos_with_controls = 0
    for video in html_videos:
        if video.get('controls') is not None:
            videos_with_controls += 1
    
    issues = []
    
    # Photo comparison
    photo_diff = abs(total_photos - len(html_images))
    if photo_diff > 0:
        issues.append(f"Photo count mismatch: {total_photos} in JSON vs {len(html_images)} in HTML (diff: {photo_diff})")
    
    # Video comparison
    video_diff = abs(total_videos - len(html_videos))
    if video_diff > 0:
        issues.append(f"Video count mismatch: {total_videos} in JSON vs {len(html_videos)} in HTML (diff: {video_diff})")
    
    # Image sizing
    if len(html_images) > 0:
        sizing_percentage = (properly_sized_images / len(html_images)) * 100
        if sizing_percentage < 100:
            issues.append(f"Only {properly_sized_images}/{len(html_images)} images properly sized ({sizing_percentage:.1f}%)")
    else:
        sizing_percentage = 100
    
    # Video controls
    if len(html_videos) > 0:
        controls_percentage = (videos_with_controls / len(html_videos)) * 100
        if controls_percentage < 100:
            issues.append(f"Only {videos_with_controls}/{len(html_videos)} videos have controls ({controls_percentage:.1f}%)")
    else:
        controls_percentage = 100
    
    # Score calculation
    if len(issues) == 0:
        score = 10  # Excellent
        grade = "Excellent"
    elif len(issues) <= 1:
        score = 8   # Good (75%)
        grade = "Good"
    elif len(issues) <= 2:
        score = 5   # Satisfactory (50%)
        grade = "Satisfactory"
    else:
        score = 3   # Needs Improvement (25%)
        grade = "Needs Improvement"
    
    print(f"Photos in JSON: {total_photos}, in HTML: {len(html_images)}")
    print(f"Videos in JSON: {total_videos}, in HTML: {len(html_videos)}")
    print(f"Properly sized images: {properly_sized_images}/{len(html_images)}")
    print(f"Videos with controls: {videos_with_controls}/{len(html_videos)}")
    print(f"Issues found: {len(issues)}")
    if issues:
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("  [OK] All media checks passed")
    print(f"Score: {score}/10 ({grade})")
    
    return score, {
        'total_photos': total_photos,
        'html_photos': len(html_images),
        'total_videos': total_videos,
        'html_videos': len(html_videos),
        'issues': issues
    }

def analyze_performance() -> Tuple[int, Dict]:
    """Test Performance and Speed (15 pts)"""
    print("\n" + "="*70)
    print("5. PERFORMANCE AND SPEED TEST (15 points)")
    print("="*70)
    
    start_time = time.time()
    
    # Run the processor
    import subprocess
    result = subprocess.run(
        ['python', 'populate_trec_complete.py'],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # Check if file was created
    output_exists = os.path.exists('TREC_Report_Filled_Improved.html')
    
    if result.returncode != 0:
        print(f"[ERROR] Error during execution: {result.stderr}")
        return 0, {'elapsed_time': elapsed_time, 'success': False, 'error': result.stderr}
    
    # Score calculation based on time
    if elapsed_time < 5:
        score = 15  # Excellent
        grade = "Excellent"
    elif elapsed_time < 10:
        score = 11  # Good (75%)
        grade = "Good"
    elif elapsed_time < 20:
        score = 8   # Satisfactory (50%)
        grade = "Satisfactory"
    else:
        score = 4   # Needs Improvement (25%)
        grade = "Needs Improvement"
    
    print(f"Execution time: {elapsed_time:.2f} seconds")
    print(f"Output file created: {output_exists}")
    print(f"Score: {score}/15 ({grade})")
    
    return score, {
        'elapsed_time': elapsed_time,
        'success': output_exists,
        'grade': grade
    }

def main():
    """Run all tests"""
    print("="*70)
    print("TREC PROCESSOR TEST SUITE")
    print("="*70)
    
    # Load files
    print("\nLoading test files...")
    try:
        inspection_data = load_json('inspection.json')
        with open('TREC_Report_Filled_Improved.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        print("[OK] Files loaded successfully")
    except FileNotFoundError as e:
        print(f"[ERROR] Error: {e}")
        print("\nRunning processor to generate output file...")
        import subprocess
        subprocess.run(['python', 'populate_trec_complete.py'])
        with open('TREC_Report_Filled_Improved.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        inspection_data = load_json('inspection.json')
    
    # Run tests
    scores = {}
    details = {}
    
    scores['data_accuracy'], details['data_accuracy'] = analyze_data_accuracy(inspection_data, html_content)
    scores['template_compliance'], details['template_compliance'] = analyze_template_compliance(html_content)
    scores['pdf_quality'], details['pdf_quality'] = analyze_pdf_quality(html_content)
    scores['media_integration'], details['media_integration'] = analyze_media_integration(html_content, inspection_data)
    scores['performance'], details['performance'] = analyze_performance()
    
    # Calculate total score
    total_score = sum(scores.values())
    max_score = 75
    percentage = (total_score / max_score) * 100
    
    # Final report
    print("\n" + "="*70)
    print("TEST RESULTS SUMMARY")
    print("="*70)
    print(f"\n1. Data Accuracy:              {scores['data_accuracy']}/15")
    print(f"2. Template Compliance:        {scores['template_compliance']}/20")
    print(f"3. PDF Quality:                 {scores['pdf_quality']}/15")
    print(f"4. Media Integration:           {scores['media_integration']}/10")
    print(f"5. Performance and Speed:      {scores['performance']}/15")
    print("-"*70)
    print(f"TOTAL SCORE:                    {total_score}/75 ({percentage:.1f}%)")
    print("="*70)
    
    # Grade
    if percentage >= 90:
        final_grade = "Excellent (A)"
    elif percentage >= 75:
        final_grade = "Good (B)"
    elif percentage >= 60:
        final_grade = "Satisfactory (C)"
    else:
        final_grade = "Needs Improvement (D)"
    
    print(f"\nFINAL GRADE: {final_grade}")
    print("="*70)
    
    return scores, details, total_score

if __name__ == "__main__":
    main()

