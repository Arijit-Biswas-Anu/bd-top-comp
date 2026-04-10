/* ====================================
   Top Bangladeshi Companies - Main AJAX Script
   ==================================== */

// Store companies for filtering
let allCompanies = [];

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
 * Load companies from API
 */
async function loadCompanies() {
    const tableBody = document.getElementById('companiesTableBody');
    
    if (!tableBody) return;
    
    try {
        const response = await fetch('/api/companies/');
        if (!response.ok) throw new Error('Failed to load companies');
        
        const data = await response.json();
        allCompanies = data.companies || [];
        
        // Store pagination info
        if (data.pagination) {
            window.paginationInfo = data.pagination;
        }
        
        displayCompaniesInTable(allCompanies);
    } catch (error) {
        console.error('Error:', error);
        tableBody.innerHTML = '<tr><td colspan="7" class="text-center text-danger py-4">Error loading companies</td></tr>';
    }
}

/**
 * Load statistics
 */
async function loadStats() {
    try {
        const response = await fetch('/api/stats/');
        if (!response.ok) throw new Error('Failed to load stats');
        
        const data = await response.json();
        
        // Update sector filter with stats
        const sectorFilter = document.getElementById('sectorFilter');
        if (sectorFilter && data.all_sectors) {
            // Clear existing options except "All Sectors"
            const firstOption = sectorFilter.options[0];
            sectorFilter.innerHTML = '';
            sectorFilter.appendChild(firstOption);
            
            // Add sectors with count
            data.all_sectors.forEach(sector => {
                const count = data.sectors.find(s => s.name === sector)?.count || 0;
                const option = document.createElement('option');
                option.value = sector;
                option.textContent = `${sector} (${count})`;
                sectorFilter.appendChild(option);
            });
        }
        
        // Display sector statistics if we have a stats container
        if (data.sectors) {
            console.log('Sector Stats:', data.sectors);
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

/**
 * Display companies in table format
 */
function displayCompaniesInTable(companies) {
    const tableBody = document.getElementById('companiesTableBody');
    const noResultsMessage = document.getElementById('noResultsMessage');
    const resultsInfo = document.getElementById('resultsInfo');
    const resultsCount = document.getElementById('resultsCount');
    const totalCount = document.getElementById('totalCount');
    
    // Detect if user is admin by checking for edit/delete buttons capability
    const adminBtn = document.getElementById('addCompanyBtn');
    const isAdmin = adminBtn !== null;
    
    if (!tableBody) return;
    
    if (companies.length === 0) {
        tableBody.innerHTML = '';
        noResultsMessage.style.display = 'block';
        if (resultsInfo) resultsInfo.style.display = 'none';
        return;
    }
    
    noResultsMessage.style.display = 'none';
    if (resultsInfo) {
        resultsInfo.style.display = 'block';
        resultsCount.textContent = companies.length;
        totalCount.textContent = allCompanies.length;
    }
    
    let html = '';
    
    companies.forEach((company, index) => {
        // Logo HTML
        const logoHtml = company.logo_url 
            ? `<img src="${company.logo_url}" alt="${escapeHtml(company.name)}" class="company-logo" onerror="this.style.display='none'; this.nextElementSibling?.style.display='flex';">`
            : '';
        
        const logoPlaceholder = !company.logo_url 
            ? `<div class="logo-placeholder" style="display: flex;">Logo</div>`
            : `<div class="logo-placeholder" style="display: none;">Logo</div>`;
        
        // Action buttons (admin only)
        const actionButtons = isAdmin ? `
            <div class="btn-group-sm" role="group">
                <button class="btn btn-sm btn-warning" onclick="handleEditCompany(${company.id})" title="Edit">
                    Edit
                </button>
                <button class="btn btn-sm btn-danger" onclick="handleDeleteCompany(${company.id})" title="Delete">
                    Delete
                </button>
            </div>
        ` : '';
        
        // Table row
        const actionsCol = isAdmin ? `<td class="actions-col">${actionButtons}</td>` : '';
        
        html += `
            <tr>
                <td class="rank-col">${index + 1}</td>
                <td class="logo-col">
                    ${logoHtml}
                    ${logoPlaceholder}
                </td>
                <td class="name-col">${escapeHtml(company.name)}</td>
                <td class="sector-col">
                    <span class="sector-badge">${escapeHtml(company.sector)}</span>
                </td>
                <td class="hq-col">${escapeHtml(company.headquarters)}</td>
                <td class="founded-col">${company.founded}</td>
                ${actionsCol}
            </tr>
        `;
    });
    
    tableBody.innerHTML = html;
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
 * Filter and display companies based on search and sector
 */
function filterAndDisplayCompanies() {
    const searchTerm = document.getElementById('searchInput')?.value.toLowerCase() || '';
    const sectorFilter = document.getElementById('sectorFilter')?.value || '';
    
    let filtered = allCompanies;
    
    // Filter by search term
    if (searchTerm) {
        filtered = filtered.filter(company =>
            company.name.toLowerCase().includes(searchTerm) ||
            company.sector.toLowerCase().includes(searchTerm) ||
            company.headquarters.toLowerCase().includes(searchTerm)
        );
    }
    
    // Filter by sector
    if (sectorFilter) {
        filtered = filtered.filter(company =>
            company.sector.toLowerCase() === sectorFilter.toLowerCase()
        );
    }
    
    displayCompaniesInTable(filtered);
}

/**
 * Initialize search functionality
 */
function initSearch() {
    const searchInput = document.getElementById('searchInput');
    
    if (!searchInput) return;
    
    // Search with debouncing
    let searchTimeout;
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            filterAndDisplayCompanies();
        }, 300);
    });
}

/**
 * Initialize sector filter
 */
function initSectorFilter() {
    const sectorFilter = document.getElementById('sectorFilter');
    
    if (!sectorFilter) return;
    
    sectorFilter.addEventListener('change', function() {
        filterAndDisplayCompanies();
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
    document.getElementById('companyModalTitle').textContent = 'Add New Company';
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
    const company = allCompanies.find(c => c.id === id);
    if (!company) return;
    
    // Populate form with company data
    document.getElementById('companyId').value = company.id;
    document.getElementById('companyName').value = company.name;
    document.getElementById('companySector').value = company.sector;
    document.getElementById('companyLogoUrl').value = company.logo_url || '';
    document.getElementById('companyHeadquarters').value = company.headquarters;
    document.getElementById('companyFounded').value = company.founded;
    document.getElementById('companyDescription').value = company.description || '';
    
    // Update modal title
    document.getElementById('companyModalTitle').textContent = 'Edit Company';
    document.getElementById('submitCompanyBtn').textContent = 'Update Company';
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('companyModal'));
    modal.show();
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
    if (!confirm('Are you sure you want to delete this company? This action cannot be undone.')) {
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
    loadCompanies();
    loadStats();
    initSearch();
    initSectorFilter();
    initAddCompany();
});

