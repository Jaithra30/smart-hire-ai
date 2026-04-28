const API_BASE = 'https://smart-hire-ai-d2zm.onrender.com';

// DOM Elements
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const fileNameDisplay = document.getElementById('file-name');
const uploadForm = document.getElementById('upload-form');
const hrUploadForm = document.getElementById('hr-upload-form');
const debugForm = document.getElementById('debug-form');
const submitBtn = document.getElementById('submit-btn');
const spinner = document.getElementById('spinner');
const errorBox = document.getElementById('error-box');
const uploadContainer = document.getElementById('upload-container');
const resultsContainer = document.getElementById('results-container');
const resultsGrid = document.getElementById('results-grid');

let currentCandidates = [];

// Setup Drag & Drop
if (dropZone) {
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.add('dragover');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.remove('dragover');
        }, false);
    });

    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        fileInput.files = files;
        updateFileName();
    });

    fileInput.addEventListener('change', updateFileName);
}

function updateFileName() {
    if (fileInput.files.length === 1) {
        fileNameDisplay.textContent = fileInput.files[0].name;
    } else if (fileInput.files.length > 1) {
        fileNameDisplay.textContent = `${fileInput.files.length} files selected`;
    } else {
        fileNameDisplay.textContent = '';
    }
}

function showError(msg) {
    if(errorBox) {
        errorBox.textContent = msg;
        errorBox.style.display = 'block';
    }
}

function hideError() {
    if(errorBox) errorBox.style.display = 'none';
}

function resetView() {
    resultsContainer.style.display = 'none';
    uploadContainer.style.display = 'block';
    if(fileInput) fileInput.value = '';
    if(fileNameDisplay) fileNameDisplay.textContent = '';
    hideError();
    currentCandidates = [];
}

function createCard(candidate) {
    const card = document.createElement('div');
    card.className = 'candidate-card';
    card.onclick = () => openModal(candidate);
    
    let scoreClass = 'score-low';
    if(candidate.score >= 75) scoreClass = 'score-high';
    else if(candidate.score >= 50) scoreClass = 'score-medium';
    
    const skillsHtml = candidate.skills && candidate.skills.length > 0 
        ? candidate.skills.map(s => `<span class="skill-tag">${s}</span>`).join('')
        : '<span class="skill-tag">No skills matched</span>';

    card.innerHTML = `
        <div class="card-top-border ${scoreClass}"></div>
        <div class="card-header">
            <div>
                <div class="candidate-name">${candidate.name || 'Unknown'}</div>
                <div class="candidate-role">${candidate.role || 'Unknown Role'}</div>
            </div>
            <div class="score-badge ${scoreClass}">${candidate.score || 0}/100</div>
        </div>
        <div class="card-body">
            <p><i class="fa-solid fa-envelope"></i> ${candidate.email || 'N/A'}</p>
            <p><i class="fa-solid fa-phone"></i> ${candidate.phone || 'N/A'}</p>
            <div class="skills-tags">
                ${skillsHtml}
            </div>
        </div>
    `;
    return card;
}

function renderCandidates(candidates) {
    resultsGrid.innerHTML = '';
    if (candidates && candidates.length > 0) {
        candidates.forEach(c => resultsGrid.appendChild(createCard(c)));
    } else {
        resultsGrid.innerHTML = '<p style="text-align:center; grid-column: 1/-1;">No candidates match.</p>';
    }
}

function applyFilters() {
    if(!currentCandidates || currentCandidates.length === 0) return;
    
    const roleFilter = document.getElementById('filter-role').value;
    const scoreFilter = parseInt(document.getElementById('filter-score').value) || 0;
    
    const skillCheckboxes = document.querySelectorAll('#filter-skills input:checked');
    const selectedSkills = Array.from(skillCheckboxes).map(cb => cb.value.toLowerCase());
    
    const expCheckboxes = document.querySelectorAll('#filter-experience input:checked');
    const selectedExp = Array.from(expCheckboxes).map(cb => cb.value.toLowerCase());
    
    const filtered = currentCandidates.filter(c => {
        if(roleFilter !== 'All' && c.role !== roleFilter) return false;
        if(c.score < scoreFilter) return false;
        
        if(selectedSkills.length > 0) {
            const cSkills = (c.skills || []).map(s => s.toLowerCase());
            const hasSkill = selectedSkills.some(skill => cSkills.includes(skill));
            if(!hasSkill) return false;
        }
        
        if(selectedExp.length > 0) {
            const cExp = (c.experience_keywords || []).map(e => e.toLowerCase());
            const hasExp = selectedExp.some(exp => cExp.includes(exp));
            if(!hasExp) return false;
        }
        
        return true;
    });
    
    renderCandidates(filtered);
}

const filterRole = document.getElementById('filter-role');
const filterScore = document.getElementById('filter-score');
const scoreVal = document.getElementById('score-val');
if(filterRole) filterRole.addEventListener('change', applyFilters);
if(filterScore) {
    filterScore.addEventListener('input', (e) => {
        if(scoreVal) scoreVal.textContent = e.target.value;
        applyFilters();
    });
}
const filterCheckboxes = document.querySelectorAll('.filter-checkboxes input');
filterCheckboxes.forEach(cb => cb.addEventListener('change', applyFilters));


function openModal(candidate) {
    const modal = document.getElementById('candidate-modal');
    const modalBody = document.getElementById('modal-body');
    if(!modal || !modalBody) return;
    
    let decisionClass = 'decision-not';
    if(candidate.decision === 'Hire') decisionClass = 'decision-hire';
    else if(candidate.decision === 'Consider') decisionClass = 'decision-consider';
    
    let scoreClass = 'score-low';
    if(candidate.score >= 75) scoreClass = 'score-high';
    else if(candidate.score >= 50) scoreClass = 'score-medium';
    
    const skillsHtml = candidate.skills && candidate.skills.length > 0 
        ? candidate.skills.map(s => `<span class="skill-tag">${s}</span>`).join('')
        : '<span class="skill-tag">No skills matched</span>';
        
    const missingHtml = candidate.missing_skills && candidate.missing_skills.length > 0
        ? `<div class="missing-skills" style="margin-top:0;"><strong>Missing:</strong> ${candidate.missing_skills.join(', ')}</div>`
        : '';
        
    const suggestionsHtml = candidate.suggestions && candidate.suggestions.length > 0
        ? `<ul style="margin-left:1.5rem; font-size:0.875rem; margin-top:0.5rem; color:var(--text-muted)">${candidate.suggestions.map(s => `<li>${s}</li>`).join('')}</ul>`
        : '';

    modalBody.innerHTML = `
        <h2 style="margin-bottom:0.25rem;">${candidate.name || 'Unknown'}</h2>
        <p style="color:var(--text-muted); margin-bottom:1rem;">${candidate.role} • ${candidate.email} • ${candidate.phone}</p>
        
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.5rem;">
            <div class="decision-badge ${decisionClass}">${candidate.decision || 'N/A'}</div>
            <div class="score-badge ${scoreClass}" style="font-size:1.25rem; padding:0.5rem 1rem;">Score: ${candidate.score || 0}</div>
        </div>
        
        <div style="background:#f8fafc; padding:1rem; border-radius:8px; margin-bottom:1.5rem; border:1px solid var(--border);">
            <h3 style="font-size:1rem; margin-bottom:0.5rem;"><i class="fa-solid fa-robot" style="color:var(--primary)"></i> AI Summary</h3>
            <p style="font-size:0.875rem; line-height:1.5;">${candidate.ai_summary || 'No summary available.'}</p>
        </div>
        
        <h3 style="font-size:1rem; margin-bottom:0.5rem;">Skills</h3>
        <div class="skills-tags" style="margin-bottom:1.5rem;">${skillsHtml}</div>
        
        <h3 style="font-size:1rem; margin-bottom:0.5rem;">Skill Gap Analysis</h3>
        ${missingHtml}
        ${suggestionsHtml}
    `;
    modal.classList.add('show');
}

function closeModal() {
    const modal = document.getElementById('candidate-modal');
    if(modal) modal.classList.remove('show');
}

// Single Upload
if (uploadForm) {
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        hideError();
        
        if (fileInput.files.length === 0) {
            showError("Please select a PDF file first.");
            return;
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        submitBtn.disabled = true;
        spinner.style.display = 'inline-block';

        try {
            const res = await fetch(`${API_BASE}/analyze`, {
                method: 'POST',
                body: formData
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.error || 'Something went wrong');
            
            // Generate modal wrapper for single result to show immediately, or just use the modal
            // The prompt says "When user clicks a candidate card: Open a detailed modal", 
            // For Single Resume, we can just render the card and let them click it
            currentCandidates = [data];
            renderCandidates(currentCandidates);
            
            uploadContainer.style.display = 'none';
            resultsContainer.style.display = 'block';

        } catch (err) {
            showError(err.message);
        } finally {
            submitBtn.disabled = false;
            spinner.style.display = 'none';
        }
    });
}

// HR Multi Upload
if (hrUploadForm) {
    hrUploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        hideError();
        
        if (fileInput.files.length === 0) {
            showError("Please select at least one PDF file.");
            return;
        }

        if (fileInput.files.length > 10) {
            showError("Maximum 10 files allowed at once.");
            return;
        }

        const formData = new FormData();
        for (let i = 0; i < fileInput.files.length; i++) {
            formData.append('files', fileInput.files[i]);
        }

        submitBtn.disabled = true;
        spinner.style.display = 'inline-block';

        try {
            const res = await fetch(`${API_BASE}/hr-upload`, {
                method: 'POST',
                body: formData
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.error || 'Something went wrong');

            currentCandidates = data.candidates || [];
            applyFilters(); // Renders with current filter state
            
            uploadContainer.style.display = 'none';
            resultsContainer.style.display = 'block';

        } catch (err) {
            showError(err.message);
        } finally {
            submitBtn.disabled = false;
            spinner.style.display = 'none';
        }
    });
}

// Code Debugger
if (debugForm) {
    debugForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const codeInput = document.getElementById('code-input').value;
        const languageSelect = document.getElementById('language-select').value;
        const debugSpinner = document.getElementById('debug-spinner');
        const debugSubmitBtn = document.getElementById('debug-submit-btn');
        const errorBox = document.getElementById('debug-error-box');
        const resultsBox = document.getElementById('debug-results');
        const messageBox = document.getElementById('debug-message');
        const errorsList = document.getElementById('debug-errors-list');
        const fixesContainer = document.getElementById('debug-fixes-container');
        const fixesList = document.getElementById('debug-fixes-list');
        
        if(errorBox) errorBox.style.display = 'none';
        resultsBox.style.display = 'none';
        
        // Remove old suggestion code if any
        const oldCode = fixesContainer.querySelector('.suggestion-code');
        if(oldCode) oldCode.remove();
        
        if (!codeInput.trim()) {
            if(errorBox) {
                errorBox.textContent = "Please enter some code to analyze.";
                errorBox.style.display = 'block';
            }
            return;
        }

        debugSubmitBtn.disabled = true;
        debugSpinner.style.display = 'inline-block';

        try {
            const res = await fetch(`${API_BASE}/debug`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ code: codeInput, language: languageSelect })
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.error || 'Something went wrong');

            resultsBox.style.display = 'block';
            messageBox.textContent = data.message;
            
            if (data.valid) {
                resultsBox.className = 'debug-results success';
                errorsList.innerHTML = '';
                fixesContainer.style.display = 'none';
            } else {
                resultsBox.className = 'debug-results error';
                errorsList.innerHTML = data.errors.map(err => `<li>${err}</li>`).join('');
                
                if (data.fixes && data.fixes.length > 0) {
                    fixesContainer.style.display = 'block';
                    fixesList.innerHTML = data.fixes.map(fix => `<li>${fix}</li>`).join('');
                } else {
                    fixesContainer.style.display = 'none';
                }
            }
            
            // Show suggestion code if any
            if (data.suggestion_code && data.suggestion_code.trim()) {
                fixesContainer.style.display = 'block';
                const pre = document.createElement('div');
                pre.className = 'suggestion-code';
                pre.textContent = data.suggestion_code;
                fixesContainer.appendChild(pre);
            }

        } catch (err) {
            if(errorBox) {
                errorBox.textContent = err.message;
                errorBox.style.display = 'block';
            }
        } finally {
            debugSubmitBtn.disabled = false;
            debugSpinner.style.display = 'none';
        }
    });
}
