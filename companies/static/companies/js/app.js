/* ====================================
   Top Bangladeshi Companies - Main AJAX Script
   ==================================== */

// ===== Utility Functions =====

/**
 * Get CSRF token from cookie or DOM
 */
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
           getCookie('csrftoken');
}

/**
 * Get cookie by name
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Show alert message
 */
function showAlert(message, type = 'success') {
    const alertContainer = document.getElementById('alertContainer');
    if (!alertContainer) return;
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.innerHTML = '';
    alertContainer.appendChild(alertDiv);
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// ===== Company List & Search Functions =====

/**
 * Load companies from API (with optional search)
 */
async function loadCompanies(searchTerm = '') {
    const companiesContainer = document.getElementById('companiesContainer');
    const noResultsMessage = document.getElementById('noResultsMessage');
    
    if (!companiesContainer) return;
    
    try {
        let url = '/api/companies/';
        if (searchTerm) {
            url += '?search=' + encodeURIComponent(searchTerm);
        }
        
        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to load companies');
        
        const data = await response.json();
        const companies = data.companies || [];
        
        if (companies.length === 0) {
            companiesContainer.innerHTML = '';
            noResultsMessage.style.display = 'block';
            return;
        }
        
        noResultsMessage.style.display = 'none';
        displayCompanies(companies);
    } catch (error) {
        console.error('Error:', error);
        companiesContainer.innerHTML = '<div class="alert alert-danger">Error loading companies</div>';
    }
}

/**
 * Display companies in DOM
 */
function displayCompanies(companies) {
    const container = document.getElementById('companiesContainer');
    const isAdmin = document.querySelector('nav .nav-link[href="/dashboard/"]') !== null;
    
    let html = '<div class="row">';
    
    companies.forEach(company => {
        const logoHtml = company.logo_url ? 
            `<img src="${company.logo_url}" alt="${company.name}" class="company-logo me-3">` : 
            `<div style="width: 60px; height: 60px; background: #e9ecef; border-radius: 4px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; color: #666; font-weight: bold;">NO LOGO</div>`;
        
        const actionButtons = isAdmin ? `
            <div class="btn-group btn-group-sm" role="group">
                <button class="btn btn-warning" onclick="handleEditCompany(${company.id})">
                    ✏️ Edit
                </button>
                <button class="btn btn-danger" onclick="handleDeleteCompany(${company.id})">
                    🗑️ Delete
                </button>
            </div>
        ` : '';
        
        html += `
            <div class="col-md-6 col-lg-4 mb-4">
                <div class="card company-card h-100">
                    <div class="card-body">
                        <div class="d-flex align-items-start mb-3">
                            ${logoHtml}
                            <div>
                                <h5 class="company-name mb-1">${escapeHtml(company.name)}</h5>
                                <span class="company-sector">${escapeHtml(company.sector)}</span>
                            </div>
                        </div>
                        
                        <div class="company-info">
                            <p class="mb-2">
                                <span class="company-info-label">📍 HQ:</span> ${escapeHtml(company.headquarters)}
                            </p>
                            <p class="mb-3">
                                <span class="company-info-label">📅 Founded:</span> ${company.founded}
                            </p>
                            ${company.description ? `
                                <p class="mb-3 text-muted">
                                    <small>${escapeHtml(company.description).substring(0, 100)}...</small>
                                </p>
                            ` : ''}
                        </div>
                        
                        ${actionButtons}
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    if (!text) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

/**
 * Initialize search functionality
 */
function initSearch() {
    const searchInput = document.getElementById('searchInput');
    const clearBtn = document.getElementById('clearSearchBtn');
    
    if (!searchInput) return;
    
    // Search on input with debouncing
    let searchTimeout;
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            loadCompanies(this.value);
        }, 300);
    });
    
    // Clear search
    clearBtn?.addEventListener('click', function() {
        searchInput.value = '';
        loadCompanies();
        searchInput.focus();
    });
}

// ===== Add/Edit Company Functions =====

/**
 * Initialize add company button
 */
function initAddCompany() {
    const addBtn = document.getElementById('addCompanyBtn');
    const submitBtn = document.getElementById('submitCompanyBtn');
    
    addBtn?.addEventListener('click', showAddModal);
    submitBtn?.addEventListener('click', handleSaveCompany);
}

/**
 * Show add company modal
 */
function showAddModal() {
    clearCompanyForm();
    document.getElementById('companyModalTitle').textContent = '➕ Add New Company';
    document.getElementById('companyId').value = '';
    document.getElementById('submitCompanyBtn').textContent = 'Save Company';
    
    const modal = new bootstrap.Modal(document.getElementById('companyModal'));
    modal.show();
}

/**
 * Clear company form
 */
function clearCompanyForm() {
    document.getElementById('companyForm').reset();
    document.getElementById('companyId').value = '';
}

/**
 * Handle edit company
 */
function handleEditCompany(id) {
    // Placeholder - will be implemented in next phase
    console.log('Edit company:', id);
}

/**
 * Handle save company (add or edit)
 */
async function handleSaveCompany() {
    const companyId = document.getElementById('companyId').value;
    const csrfToken = getCsrfToken();
    
    const data = {
        name: document.getElementById('companyName').value,
        sector: document.getElementById('companySector').value,
        logo_url: document.getElementById('companyLogoUrl').value,
        headquarters: document.getElementById('companyHeadquarters').value,
        founded: parseInt(document.getElementById('companyFounded').value),
        description: document.getElementById('companyDescription').value
    };
    
    // Validate required fields
    if (!data.name || !data.sector || !data.headquarters || !data.founded) {
        showAlert('Please fill in all required fields', 'warning');
        return;
    }
    
    try {
        const url = companyId ? 
            `/api/companies/${companyId}/edit/` : 
            '/api/companies/add/';
        
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message || 'Company saved successfully!', 'success');
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('companyModal'));
            modal?.hide();
            
            // Reload companies list
            loadCompanies();
            clearCompanyForm();
        } else {
            showAlert(result.message || 'Error saving company', 'danger');
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert('An error occurred', 'danger');
    }
}

/**
 * Handle delete company
 */
async function handleDeleteCompany(id) {
    if (!confirm('Are you sure you want to delete this company?')) {
        return;
    }
    
    const csrfToken = getCsrfToken();
    
    try {
        const response = await fetch(`/api/companies/${id}/delete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('Company deleted successfully!', 'success');
            loadCompanies();
        } else {
            showAlert(result.message || 'Error deleting company', 'danger');
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert('An error occurred', 'danger');
    }
}

/**
 * Handle logout
 */
function handleLogout() {
    if (confirm('Are you sure you want to logout?')) {
        const csrfToken = getCsrfToken();
        
        fetch('/logout/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
            }
        })
        .then(() => {
            window.location.href = '/';
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('Logout error', 'danger');
        });
    }
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('App initialized');
});
