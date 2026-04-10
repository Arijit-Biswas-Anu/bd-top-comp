/* ====================================
   Top Bangladeshi Companies - Main AJAX Script
   ==================================== */

// Store companies for filtering
let allCompanies = [];

// Pagination variables
let currentPage = 1;
let totalPages = 1;
let currentLimit = 50;
let currentSearch = '';
let currentSector = '';

// Sorting variables
let currentSort = 'name';
let currentOrder = 'asc';

// Selected company for detail view
let selectedCompany = null;

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
        // Build API URL with search, filter, sort, and pagination parameters
        const params = new URLSearchParams();
        if (currentSearch) params.append('search', currentSearch);
        if (currentSector) params.append('sector', currentSector);
        if (currentSort && currentSort !== 'name') params.append('sort', currentSort);
        if (currentOrder && currentOrder !== 'asc') params.append('order', currentOrder);
        if (currentPage) params.append('page', currentPage);
        if (currentLimit) params.append('limit', currentLimit);
        
        const url = `/api/companies/?${params.toString()}`;
        const response = await fetch(url);
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
        
        // Display sector statistics on the page
        if (data.sectors && data.sectors.length > 0) {
            const statsSection = document.getElementById('statsSection');
            const statsList = document.getElementById('sectorStatsList');
            
            if (statsSection && statsList) {
                statsSection.style.display = 'block';
                
                // Create HTML for sector stats
                let statsHtml = '';
                data.sectors.forEach(sector => {
                    statsHtml += `
                        <div class="sector-stat-item">
                            <strong>${sector.count}</strong>
                            <small>${sector.name}</small>
                        </div>
                    `;
                });
                
                statsList.innerHTML = statsHtml;
            }
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
                <button class="btn btn-sm btn-warning" onclick="handleEditCompany(${company.id}); event.stopPropagation();" title="Edit">
                    Edit
                </button>
                <button class="btn btn-sm btn-danger" onclick="handleDeleteCompany(${company.id}); event.stopPropagation();" title="Delete">
                    Delete
                </button>
            </div>
        ` : '';
        
        // Table row - clickable to show detail
        const actionsCol = isAdmin ? `<td class="actions-col">${actionButtons}</td>` : '';
        
        html += `
            <tr onclick="showCompanyDetail(${company.id})" style="cursor: pointer;">
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
    
    // Display pagination controls if available
    if (window.paginationInfo) {
        displayPaginationControls(window.paginationInfo);
    }
    
    // Update sort indicators
    updateSortIndicators();
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
 * Display pagination controls
 */
function displayPaginationControls(pagination) {
    if (!pagination || pagination.pages <= 1) {
        document.getElementById('paginationControls').style.display = 'none';
        return;
    }
    
    const paginationControls = document.getElementById('paginationControls');
    const pageInfo = document.getElementById('pageInfo');
    
    if (paginationControls) {
        paginationControls.style.display = 'block';
    }
    
    if (pageInfo) {
        pageInfo.innerHTML = `<span class="page-link">Page ${pagination.page} of ${pagination.pages}</span>`;
    }
    
    // Update global variables
    currentPage = pagination.page;
    totalPages = pagination.pages;
}

/**
 * Go to a specific page
 */
function goToPage(page) {
    if (page < 1 || page > totalPages) return;
    currentPage = page;
    
    // Reload companies for this page
    loadCompanies();
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

/**
 * Handle sorting by column
 */
function handleSort(sortField) {
    // Toggle sort order if clicking the same field
    if (currentSort === sortField) {
        currentOrder = currentOrder === 'asc' ? 'desc' : 'asc';
    } else {
        currentSort = sortField;
        currentOrder = 'asc';
    }
    
    // Reset to page 1 when sorting changes
    currentPage = 1;
    
    // Update table headers to show sort indicator
    updateSortIndicators();
    
    // Reload companies with new sort
    loadCompanies();
}

/**
 * Update sort indicators on table headers
 */
function updateSortIndicators() {
    // Remove sorted class from all headers
    document.querySelectorAll('th.sortable').forEach(th => {
        th.classList.remove('sorted-asc', 'sorted-desc');
    });
    
    // Add sorted class to current sort column
    const fieldMap = {
        'name': document.querySelector('th.name-col'),
        'sector': document.querySelector('th.sector-col'),
        'founded': document.querySelector('th.founded-col')
    };
    
    if (fieldMap[currentSort]) {
        fieldMap[currentSort].classList.add(`sorted-${currentOrder}`);
    }
}

/**
 * Show company detail modal
 */
function showCompanyDetail(id) {
    const company = allCompanies.find(c => c.id === id);
    if (!company) return;
    
    selectedCompany = company;
    
    // Populate modal with data
    document.getElementById('detailLogo').src = company.logo_url || '';
    document.getElementById('detailName').textContent = company.name;
    document.getElementById('detailSector').textContent = company.sector;
    document.getElementById('detailHQ').textContent = company.headquarters;
    document.getElementById('detailFounded').textContent = company.founded;
    document.getElementById('detailDescription').textContent = company.description || 'No description available';
    
    // Format dates
    const createdDate = new Date(company.created_at).toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
    document.getElementById('detailCreated').textContent = createdDate;
    
    // Show updated field only if created and updated are different
    const updatedField = document.getElementById('updatedField');
    if (company.created_at !== company.updated_at) {
        updatedField.style.display = 'flex';
        const updatedDate = new Date(company.updated_at).toLocaleDateString('en-US', { 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        document.getElementById('detailUpdated').textContent = updatedDate;
    } else {
        updatedField.style.display = 'none';
    }
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('detailModal'));
    modal.show();
}

/**
 * Edit company from detail modal
 */
function editCompanyFromDetail() {
    if (!selectedCompany) return;
    
    // Close detail modal
    const detailModal = bootstrap.Modal.getInstance(document.getElementById('detailModal'));
    detailModal?.hide();
    
    // Open edit modal
    setTimeout(() => {
        handleEditCompany(selectedCompany.id);
    }, 300);
}

/**
 * Delete company from detail modal
 */
function deleteCompanyFromDetail() {
    if (!selectedCompany) return;
    
    // Close detail modal
    const detailModal = bootstrap.Modal.getInstance(document.getElementById('detailModal'));
    detailModal?.hide();
    
    // Delete company
    setTimeout(() => {
        handleDeleteCompany(selectedCompany.id);
    }, 300);
}

/**
 * Show advanced filters panel
 */
function showAdvancedFilters() {
    const panel = document.getElementById('advancedFilterPanel');
    if (panel) {
        panel.style.display = 'flex';
        
        // Close panel when clicking outside
        setTimeout(() => {
            panel.addEventListener('click', function(e) {
                if (e.target === panel) {
                    closeAdvancedFilters();
                }
            });
        }, 0);
    }
}

/**
 * Close advanced filters panel
 */
function closeAdvancedFilters() {
    const panel = document.getElementById('advancedFilterPanel');
    if (panel) {
        panel.style.display = 'none';
    }
}

/**
 * Apply advanced filters
 */
function applyAdvancedFilters() {
    const search = document.getElementById('filterSearch').value;
    const sector = document.getElementById('filterSector').value;
    const founded = document.getElementById('filterFounded').value;
    const hq = document.getElementById('filterHQ').value;
    const sort = document.getElementById('filterSort').value;
    const order = document.getElementById('filterOrder').value;
    
    // Update global search and sector
    currentSearch = search;
    currentSector = sector;
    currentSort = sort;
    currentOrder = order;
    currentPage = 1; // Reset to page 1
    
    // Close the filter panel
    closeAdvancedFilters();
    
    // Reload companies with new filters
    loadCompanies();
    
    // Show feedback
    showAlert('Filters applied! 🎯', 'info');
}

/**
 * Clear all filters
 */
function clearAllFilters() {
    // Reset search input
    const searchInput = document.getElementById('searchInput');
    if (searchInput) searchInput.value = '';
    
    // Reset sector dropdown
    const sectorFilter = document.getElementById('sectorFilter');
    if (sectorFilter) sectorFilter.value = '';
    
    // Reset filter panel inputs
    document.getElementById('filterSearch').value = '';
    document.getElementById('filterSector').value = '';
    document.getElementById('filterFounded').value = '';
    document.getElementById('filterHQ').value = '';
    document.getElementById('filterSort').value = 'name';
    document.getElementById('filterOrder').value = 'asc';
    
    // Reset global variables
    currentSearch = '';
    currentSector = '';
    currentSort = 'name';
    currentOrder = 'asc';
    currentPage = 1;
    
    // Close filter panel
    closeAdvancedFilters();
    
    // Reload companies
    loadCompanies();
    
    // Show feedback
    showAlert('Filters cleared! 🔄', 'info');
}

/**
 * Keyboard Navigation Support
 */
function initKeyboardNavigation() {
    document.addEventListener('keydown', function(e) {
        // Escape key closes modals and filter panel
        if (e.key === 'Escape') {
            closeAdvancedFilters();
            
            // Close any open modals
            const modals = document.querySelectorAll('.modal.show');
            modals.forEach(modal => {
                const bsModal = bootstrap.Modal.getInstance(modal);
                if (bsModal) bsModal.hide();
            });
        }
        
        // Ctrl/Cmd + F opens search focus
        if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
            e.preventDefault();
            const searchInput = document.getElementById('searchInput');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Ctrl/Cmd + K opens advanced filters
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            showAdvancedFilters();
        }
        
        // Arrow keys for pagination
        if (e.key === 'ArrowRight' && e.ctrlKey) {
            e.preventDefault();
            if (currentPage < totalPages) {
                goToPage(currentPage + 1);
            }
        }
        
        if (e.key === 'ArrowLeft' && e.ctrlKey) {
            e.preventDefault();
            if (currentPage > 1) {
                goToPage(currentPage - 1);
            }
        }
    });
}

/**
 * Export data to CSV
 */
function exportToCSV() {
    const search = document.getElementById('searchInput')?.value || '';
    const sector = document.getElementById('sectorFilter')?.value || '';
    
    // Build query parameters
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    if (sector) params.append('sector', sector);
    if (currentSort) params.append('sort', currentSort);
    if (currentOrder) params.append('order', currentOrder);
    
    // Trigger download
    window.location.href = `/api/export/csv/?${params.toString()}`;
    
    showAlert('Companies exported to CSV! 📥', 'success');
}

/**
 * Export summary report
 */
function exportSummary() {
    window.location.href = '/api/export/summary/';
    showAlert('Summary report exported! 📊', 'success');
}

/**
 * Initialize pagination size selector
 */
function initPaginationSizeSelector() {
    const selector = document.getElementById('pageLimitSelect');
    if (!selector) return;
    
    selector.addEventListener('change', function() {
        currentLimit = parseInt(this.value);
        currentPage = 1; // Reset to page 1
        loadCompanies();
    });
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('App initialized');
    loadCompanies();
    loadStats();
    initSearch();
    initSectorFilter();
    initAddCompany();
    initKeyboardNavigation();
    initPaginationSizeSelector();
});

