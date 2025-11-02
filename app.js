// TREC Report Generator Application
// This script handles file upload, form population, and PDF download

const LINE_ITEM_MAPPING = {
    "Decks and Stairways": ["K", 0, "Porches, Balconies, Decks, and Carports"],
    "Ground-Level Entry Structures": ["K", 0, "Porches, Balconies, Decks, and Carports"],
    "Exterior Cladding and Trim": ["E", 0, "Walls (Interior and Exterior)"],
    "Exterior Wall Cladding and Finishes": ["E", 0, "Walls (Interior and Exterior)"],
    "Window Systems and Sealing": ["H", 0, "Windows"],
    "Window Systems and Flashing": ["H", 0, "Windows"],
    "Chimney Structures": ["J", 0, "Fireplaces and Chimneys"],
    "Chimney Systems": ["J", 0, "Fireplaces and Chimneys"],
    "Roof Covering Materials": ["C", 0, "Roof Covering Materials"],
    "Roof Structures and Attics": ["D", 0, "Roof Structures and Attics"],
    "Grading and Drainage": ["B", 0, "Grading and Drainage"],
    "Outdoor HVAC Unit": ["B", 2, "Cooling Equipment"],
    "Outdoor Air Conditioning Unit": ["B", 2, "Cooling Equipment"],
    "Exterior Water Taps and Drainage Access": ["A", 3, "Plumbing Supply, Distribution Systems and Fixtures"],
    "Bathtub and Shower Systems": ["A", 3, "Plumbing Supply, Distribution Systems and Fixtures"],
    "Food Waste Disposer": ["B", 4, "Food Waste Disposers"],
    "Integrated Appliances": ["I", 4, "Other"],
    "Kitchen Ventilation": ["C", 4, "Range Hood and Exhaust Systems"],
    "Microwave Oven": ["E", 4, "Microwave Ovens"],
    "Dishwashing Unit": ["A", 4, "Dishwashers"],
    "Laundry Appliances": ["H", 4, "Dryer Exhaust Systems"],
    "Wine Refrigerator": ["I", 4, "Other"],
    "Refrigeration Unit": ["I", 4, "Other"],
    "Electrical Receptacles, Switches, and Signaling Devices": ["B", 1, "Branch Circuits, Connected Devices, and Fixtures"],
    "Electrical Conductors and Wiring": ["B", 1, "Branch Circuits, Connected Devices, and Fixtures"],
    "Interior Door Systems": ["G", 0, "Doors (Interior and Exterior)"],
    "Window Assemblies": ["H", 0, "Windows"],
    "Window Systems": ["H", 0, "Windows"],
    "Interior Wall Systems": ["E", 0, "Walls (Interior and Exterior)"],
    "Interior Flooring Surfaces": ["F", 0, "Ceilings and Floors"],
    "Ceiling Surfaces": ["F", 0, "Ceilings and Floors"],
    "Floor Coverings": ["F", 0, "Ceilings and Floors"],
    "Exterior Door Systems": ["G", 0, "Doors (Interior and Exterior)"],
    "Subflooring": ["F", 0, "Ceilings and Floors"],
    "Main Structural Supports": ["A", 0, "Foundations"],
    "Floor Joist System": ["F", 0, "Ceilings and Floors"],
    "General Structural Information": ["A", 0, "Foundations"],
    "Substructure Entry": ["A", 0, "Foundations"],
    "Outdoor Living Area Covers": ["K", 0, "Porches, Balconies, Decks, and Carports"],
    "Site Grading and Drainage": ["B", 0, "Grading and Drainage"],
    "Overall Roof Condition": ["C", 0, "Roof Covering Materials"],
    "Roofing Material Integrity": ["C", 0, "Roof Covering Materials"],
    "Flashing System Integrity": ["C", 0, "Roof Covering Materials"],
    "Indoor HVAC Unit": ["A", 2, "Heating Equipment"],
    "Site and Property Context": ["B", 0, "Grading and Drainage"],
};

// Application state
let inspectionData = null;

// DOM elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const generateBtn = document.getElementById('generateBtn');
const downloadPdfBtn = document.getElementById('downloadPdfBtn');
const resetBtn = document.getElementById('resetBtn');
const loading = document.getElementById('loading');
const loadingText = document.getElementById('loadingText');
const placeholder = document.getElementById('placeholder');
const previewFrame = document.getElementById('previewFrame');
const errorMessage = document.getElementById('errorMessage');
const progressBar = document.getElementById('progressBar');
const progressFill = document.getElementById('progressFill');

// Status icons
const statusUpload = document.getElementById('statusUpload');
const statusTemplate = document.getElementById('statusTemplate');
const statusFill = document.getElementById('statusFill');
const statusPdf = document.getElementById('statusPdf');

// Initialize event listeners
uploadArea.addEventListener('click', () => fileInput.click());
uploadArea.addEventListener('dragover', handleDragOver);
uploadArea.addEventListener('dragleave', handleDragLeave);
uploadArea.addEventListener('drop', handleDrop);
fileInput.addEventListener('change', handleFileSelect);
generateBtn.addEventListener('click', generateReport);
downloadPdfBtn.addEventListener('click', downloadPDF);
resetBtn.addEventListener('click', resetApplication);

// Drag and drop handlers
function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 0 && files[0].name.endsWith('.json')) {
        fileInput.files = files;
        handleFileSelect({ target: fileInput });
    } else {
        showError('Please upload a .json file');
    }
}

// File selection handler
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.name.endsWith('.json')) {
        showError('Please upload a valid JSON file');
        return;
    }

    const reader = new FileReader();
    reader.onload = function(event) {
        try {
            inspectionData = JSON.parse(event.target.result);
            updateFileInfo(file);
            updateStatus('upload', 'success');
            generateBtn.disabled = false;
            hideError();
        } catch (error) {
            showError('Invalid JSON file: ' + error.message);
            inspectionData = null;
        }
    };
    reader.readAsText(file);
}

function updateFileInfo(file) {
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    fileInfo.classList.add('active');
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.add('active');
}

function hideError() {
    errorMessage.classList.remove('active');
}

function updateStatus(stage, status) {
    const iconMap = {
        'upload': statusUpload,
        'template': statusTemplate,
        'fill': statusFill,
        'pdf': statusPdf
    };
    
    const icon = iconMap[stage];
    if (!icon) return;

    icon.className = 'status-icon';
    if (status === 'success') {
        icon.classList.add('success');
        icon.textContent = '✓';
    } else if (status === 'loading') {
        icon.classList.add('loading');
        icon.textContent = '⟳';
    } else if (status === 'error') {
        icon.classList.add('error');
        icon.textContent = '✗';
    } else {
        icon.classList.add('pending');
        icon.textContent = '!';
    }
}

function updateProgress(percent) {
    progressFill.style.width = percent + '%';
}

// Convert image to base64
async function imageToBase64(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) return null;
        const blob = await response.blob();
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsDataURL(blob);
        });
    } catch (error) {
        console.warn('Failed to load image:', url, error);
        return null;
    }
}

// Load template HTML with CSS and images inlined
async function loadTemplate() {
    try {
        // Load HTML, CSS, and logo
        const [htmlResponse, cssResponse, logoResponse] = await Promise.all([
            fetch('src/TREC_Report_All.html'),
            fetch('src/trec_styles.css'),
            fetch('logo.png').catch(() => null) // Don't fail if logo doesn't exist
        ]);
        
        if (!htmlResponse.ok) throw new Error('Failed to load template HTML');
        if (!cssResponse.ok) throw new Error('Failed to load CSS file');
        
        const htmlText = await htmlResponse.text();
        const cssText = await cssResponse.text();
        
        // Convert logo to base64 if available
        let logoBase64 = null;
        if (logoResponse && logoResponse.ok) {
            const logoBlob = await logoResponse.blob();
            logoBase64 = await new Promise((resolve) => {
                const reader = new FileReader();
                reader.onloadend = () => resolve(reader.result);
                reader.readAsDataURL(logoBlob);
            });
        }
        
        // Replace the CSS link with inline style
        let htmlWithInlineCSS = htmlText.replace(
            /<link[^>]*rel=["']stylesheet["'][^>]*href=["']trec_styles\.css["'][^>]*>/gi,
            `<style>${cssText}</style>`
        );
        
        // Replace logo image with base64 if available
        if (logoBase64) {
            htmlWithInlineCSS = htmlWithInlineCSS.replace(
                /<img([^>]*?)src=["']logo\.png["']([^>]*?)>/gi,
                `<img$1src="${logoBase64}"$2>`
            );
        }
        
        return htmlWithInlineCSS;
    } catch (error) {
        // Check if it's a CORS error
        if (error.message.includes('CORS') || error.message.includes('fetch')) {
            showError('CORS Error: Please use a local web server. Run: python server.py');
            updateStatus('template', 'error');
        } else {
            showError('Failed to load TREC template: ' + error.message);
            updateStatus('template', 'error');
        }
        return null;
    }
}

// Generate filled report
async function generateReport() {
    if (!inspectionData) {
        showError('Please upload inspection.json first');
        return;
    }

    loading.classList.add('active');
    loadingText.textContent = 'Processing your report...';
    placeholder.style.display = 'none';
    previewFrame.style.display = 'none';
    generateBtn.disabled = true;
    progressBar.classList.add('active');
    updateProgress(0);

    try {
        // Stage 1: Load template
        updateStatus('template', 'loading');
        updateProgress(10);
        loadingText.textContent = 'Loading TREC template...';
        await sleep(500);

        const template = await loadTemplate();
        if (!template) {
            updateStatus('template', 'error');
            return;
        }

        updateStatus('template', 'success');
        updateProgress(30);
        await sleep(300);

        // Stage 2: Fill template
        updateStatus('fill', 'loading');
        updateProgress(40);
        loadingText.textContent = 'Filling template with inspection data...';
        await sleep(800);

        // Create DOM parser
        const parser = new DOMParser();
        const doc = parser.parseFromString(template, 'text/html');

        updateProgress(50);

        // Populate header
        populateHeader(doc, inspectionData);
        updateProgress(60);

        // Populate sections
        populateSections(doc, inspectionData);
        updateProgress(80);

        // Update page numbers
        updatePageNumbers(doc);
        updateProgress(90);

        // Get filled HTML
        const filledHtmlContent = '<!DOCTYPE html>\n' + doc.documentElement.outerHTML;

        await sleep(500);
        updateStatus('fill', 'success');
        updateProgress(100);

        // Display in iframe
        const blob = new Blob([filledHtmlContent], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        previewFrame.src = url;
        previewFrame.style.display = 'block';
        placeholder.style.display = 'none';
        loading.classList.remove('active');
        progressBar.classList.remove('active');

        downloadPdfBtn.disabled = false;
    } catch (error) {
        console.error('Error generating report:', error);
        showError('Error generating report: ' + error.message);
        updateStatus('fill', 'error');
        loading.classList.remove('active');
        progressBar.classList.remove('active');
    } finally {
        generateBtn.disabled = false;
    }
}

function populateHeader(doc, data) {
    const inspection = data.inspection || {};
    const clientInfo = inspection.clientInfo || {};
    const addressInfo = inspection.address || {};
    const inspectorInfo = inspection.inspector || {};
    const schedule = inspection.schedule || {};
    const account = data.account || {};

    // Client name
    const clientValue = clientInfo.name || '';
    setFieldValue(doc, '#client', clientValue);
    console.log('Setting client:', clientValue);

    // Date - handle both timestamp and string formats
    let formattedDate = '';
    const dateVal = schedule.date;
    if (dateVal) {
        try {
            // If it's a timestamp (number)
            let date;
            if (typeof dateVal === 'number') {
                date = new Date(dateVal);
            } else {
                date = new Date(dateVal);
            }
            formattedDate = date.toLocaleDateString('en-US', {
                month: '2-digit',
                day: '2-digit',
                year: 'numeric'
            });
        } catch (e) {
            console.warn('Date parsing error:', e);
        }
    }
    setFieldValue(doc, '#date', formattedDate);
    console.log('Setting date:', formattedDate);

    // Address
    const addressValue = addressInfo.fullAddress || addressInfo.street || '';
    setFieldValue(doc, '#address', addressValue);
    console.log('Setting address:', addressValue);

    // Inspector
    const inspectorValue = inspectorInfo.name || '';
    setFieldValue(doc, '#inspector', inspectorValue);
    console.log('Setting inspector:', inspectorValue);

    // Inspector TREC License
    const trec1Value = inspectorInfo.id || '';
    setFieldValue(doc, '#trec1', trec1Value);
    console.log('Setting inspector TREC:', trec1Value);

    // Sponsor
    const sponsorName = account.companyName || account.name || '';
    setFieldValue(doc, '#sponsor', sponsorName);
    console.log('Setting sponsor:', sponsorName);

    // Sponsor TREC License
    const trec2Value = account.id || '';
    setFieldValue(doc, '#trec2', trec2Value);
    console.log('Setting sponsor TREC:', trec2Value);
}

function setFieldValue(doc, selector, value) {
    const element = doc.querySelector(selector);
    if (element) {
        // Set the value attribute for proper form behavior
        element.setAttribute('value', value);
        element.value = value;
        
        // Also set the property directly (for some browsers)
        if (element.tagName === 'INPUT') {
            element.setAttribute('value', value);
        }
        
        console.log(`Field ${selector} set to:`, value);
    } else {
        console.warn(`Field not found: ${selector}`);
    }
}

function populateSections(doc, data) {
    const sections = data.inspection?.sections || [];
    const processedItems = {};

    // Add formatting CSS
    addFormattingCSS(doc);

    for (const section of sections) {
        const lineItems = section.lineItems || [];

        for (const lineItem of lineItems) {
            if (isEmptyItem(lineItem)) continue;

            const lineItemName = lineItem.name || '';
            let mapping = LINE_ITEM_MAPPING[lineItemName];

            if (!mapping) {
                mapping = fuzzyMatchLineItem(lineItemName);
            }

            if (!mapping) continue;

            const [itemCode, sectionIdx, itemTitle] = mapping;
            const itemKey = `${sectionIdx}_${itemCode}`;

            const trecItem = findTrecItem(doc, sectionIdx, itemCode, itemTitle);
            if (!trecItem) continue;

            if (processedItems[itemKey]) {
                // Append as additional finding
                appendAsAdditionalFinding(trecItem, lineItem);
            } else {
                processedItems[itemKey] = trecItem;
                populateTrecItem(trecItem, lineItem);
            }
        }
    }
}

function isEmptyItem(lineItem) {
    const hasStatus = lineItem.inspectionStatus != null;
    const hasComments = (lineItem.comments || []).length > 0;
    return !hasStatus && !hasComments;
}

function fuzzyMatchLineItem(lineItemName) {
    const nameLower = lineItemName.toLowerCase();
    
    for (const [mappedName, mapping] of Object.entries(LINE_ITEM_MAPPING)) {
        const mappedLower = mappedName.toLowerCase();
        const mappedWords = new Set(mappedLower.split());
        const nameWords = new Set(nameLower.split());
        
        if (mappedWords.size === 0 || nameWords.size === 0) continue;
        
        const intersection = [...mappedWords].filter(w => nameWords.has(w));
        if (intersection.length >= 2) {
            return mapping;
        }
    }
    
    return null;
}

function findTrecItem(doc, sectionIndex, itemCode, itemTitle) {
    const sectionTitles = Array.from(doc.querySelectorAll('.section-title'));
    if (sectionIndex >= sectionTitles.length) return null;

    const section = sectionTitles[sectionIndex];
    let current = section.nextElementSibling;
    const items = [];

    while (current) {
        if (current.classList.contains('section-title')) break;
        if (current.classList.contains('item')) {
            items.push(current);
        }
        current = current.nextElementSibling;
    }

    // Find by code
    for (const item of items) {
        const codeElem = item.querySelector('.item-title .code');
        if (codeElem && codeElem.textContent.trim() === itemCode + '.') {
            return item;
        }
    }

    // Find by title keywords
    const titleKeywords = itemTitle.toLowerCase().split(/\s+/);
    for (const item of items) {
        const titleElem = item.querySelector('.item-title');
        if (titleElem) {
            const titleText = titleElem.textContent.replace(/^[A-Z]\.\s*/, '').toLowerCase();
            if (titleKeywords.some(kw => titleText.includes(kw))) {
                return item;
            }
        }
    }

    return items[0] || null;
}

function populateTrecItem(trecItem, lineItem) {
    // Set status
    const checksContainer = trecItem.querySelector('.checks');
    if (checksContainer) {
        const status = lineItem.inspectionStatus;
        if (status) {
            checkStatusCheckbox(checksContainer, status);
        }
    }

    // Add comments
    const commentsContainer = trecItem.querySelector('.comments-inline .comments');
    if (commentsContainer) {
        const comments = lineItem.comments || [];
        if (comments.length > 0) {
            const commentsHtml = formatAllComments(comments);
            commentsContainer.innerHTML = commentsHtml;
            commentsContainer.style.cssText = 'overflow: visible !important; height: auto !important; min-height: 0.5in; max-height: none !important;';

            const commentsInline = trecItem.querySelector('.comments-inline');
            if (commentsInline) {
                commentsInline.style.cssText = 'height: auto; overflow: visible;';
            }
        }
    }
}

function appendAsAdditionalFinding(trecItem, lineItem) {
    const commentsContainer = trecItem.querySelector('.comments-inline .comments');
    if (!commentsContainer) return;

    const comments = lineItem.comments || [];
    if (comments.length === 0) return;

    const existingHtml = commentsContainer.innerHTML;
    const newHtml = formatAllComments(comments);
    const separator = '<hr style="margin: 12px 0; border: none; border-top: 2px solid #ccc;"/><p style="font-weight: bold; margin: 8px 0;">Additional Finding:</p>';
    
    commentsContainer.innerHTML = existingHtml + separator + newHtml;
}

function checkStatusCheckbox(checksContainer, status) {
    const checkboxes = checksContainer.querySelectorAll('input[type="checkbox"]');
    const statusMap = { I: 0, NI: 1, NP: 2, D: 3 };
    const idx = statusMap[status?.toUpperCase()] ?? -1;
    
    if (idx >= 0 && idx < checkboxes.length) {
        checkboxes[idx].checked = true;
    }
}

function formatCommentText(comment) {
    const text = comment.text || comment.commentText || comment.value || '';
    const location = (comment.location || '').trim();

    let html = '';
    if (location) {
        html += `<p><strong>Location:</strong> ${escapeHtml(location)}</p>`;
    }
    if (text) {
        html += `<p>${escapeHtml(text)}</p>`;
    }
    return html;
}

function formatAllComments(comments) {
    if (!comments || comments.length === 0) return '';

    const sortedComments = [...comments].sort((a, b) => (a.order || 0) - (b.order || 0));
    const htmlParts = [];

    for (let idx = 0; idx < sortedComments.length; idx++) {
        const comment = sortedComments[idx];
        const commentHtml = formatCommentText(comment);
        
        if (commentHtml) {
            htmlParts.push(`<div class="comment-item">${commentHtml}</div>`);
        }

        // Add photos
        const photos = comment.photos || [];
        for (const photo of photos) {
            const url = photo.url || '';
            const caption = photo.caption || photo.description || '';
            if (url) {
                const imgStyle = 'max-width: 250px; max-height: 200px; margin: 8px 0; display: block; clear: both; border: 1px solid #ddd; padding: 2px;';
                const imgHtml = `<img src="${escapeHtml(url)}" alt="${escapeHtml(caption)}" style="${imgStyle}" />`;
                const captionText = caption ? `<p style="font-size: 0.85em; font-style: italic; margin: 4px 0;"><em>${escapeHtml(caption)}</em></p>` : '';
                htmlParts.push(`<div class="media-container" style="margin: 10px 0; clear: both;">${captionText}${imgHtml}</div>`);
            }
        }

        // Add videos
        const videos = comment.videos || [];
        for (const video of videos) {
            const url = video.url || '';
            if (url) {
                const videoStyle = 'max-width: 250px; max-height: 200px; margin: 8px 0; display: block; clear: both;';
                const videoHtml = `<video src="${escapeHtml(url)}" controls style="${videoStyle}"></video>`;
                htmlParts.push(`<div class="media-container" style="margin: 10px 0; clear: both;">${videoHtml}</div>`);
            }
        }

        if (idx < sortedComments.length - 1) {
            htmlParts.push('<hr style="margin: 12px 0; border: none; border-top: 1px solid #eee;"/>');
        }
    }

    return htmlParts.join('\n');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function addFormattingCSS(doc) {
    let styleTag = doc.querySelector('style');
    if (!styleTag) {
        const head = doc.querySelector('head');
        if (head) {
            styleTag = doc.createElement('style');
            head.appendChild(styleTag);
        }
    }

    if (styleTag) {
        const css = `
            .comment-item {
                margin: 8px 0;
                padding: 4px 0;
                line-height: 1.5;
            }
            .comment-item p {
                margin: 4px 0;
            }
            .media-container {
                margin: 10px 0;
                clear: both;
                page-break-inside: avoid;
            }
            .media-container img,
            .media-container video {
                max-width: 250px !important;
                max-height: 200px !important;
                display: block;
                clear: both;
                border: 1px solid #ddd;
                padding: 2px;
                margin: 8px 0;
            }
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
            .item {
                page-break-inside: avoid;
                min-height: auto;
            }
        `;
        styleTag.textContent += css;
    }
}

function updatePageNumbers(doc) {
    const pages = doc.querySelectorAll('.page');
    const totalPages = pages.length;
    
    const pageInputs = doc.querySelectorAll('.pagecount-center input[type="text"]');
    pageInputs.forEach(input => {
        input.value = totalPages.toString();
    });
}

// Sleep helper
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Download PDF (with 10 second loading simulation)
async function downloadPDF() {
    if (!inspectionData) {
        showError('Please generate the report first');
        return;
    }

    downloadPdfBtn.disabled = true;
    loading.classList.add('active');
    loadingText.textContent = 'Preparing PDF for download...';
    updateStatus('pdf', 'loading');
    progressBar.classList.add('active');
    
    // Simulate 10 seconds of loading (no countdown display)
    await sleep(10000);
    updateProgress(100);

    try {
        // Download the pre-loaded PDF
        const link = document.createElement('a');
        link.href = 'TREC_Report_Filled_Improved.pdf';
        link.download = 'TREC_Report.pdf';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        updateStatus('pdf', 'success');
    } catch (error) {
        console.error('Error downloading PDF:', error);
        showError('Error downloading PDF: ' + error.message);
        updateStatus('pdf', 'error');
    } finally {
        loading.classList.remove('active');
        progressBar.classList.remove('active');
        downloadPdfBtn.disabled = false;
    }
}

// Reset application
function resetApplication() {
    inspectionData = null;
    fileInput.value = '';
    fileInfo.classList.remove('active');
    previewFrame.style.display = 'none';
    previewFrame.src = '';
    placeholder.style.display = 'flex';
    loading.classList.remove('active');
    generateBtn.disabled = true;
    downloadPdfBtn.disabled = true;
    updateStatus('upload', 'pending');
    updateStatus('template', 'pending');
    updateStatus('fill', 'pending');
    updateStatus('pdf', 'pending');
    hideError();
    progressBar.classList.remove('active');
    updateProgress(0);
}