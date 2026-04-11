/* ====================================
   Top Bangladeshi Companies - Main AJAX Script
   ==================================== */

// Store companies for filtering
let allStartups = [];

// Pagination variables
let currentPage = 1;
let totalPages = 1;
let currentLimit = 50;
let currentSearch = '';
let currentSector = '';

// Sorting variables
let currentSort = 'name';
let currentOrder = 'asc';

// Selected startup for detail view
let selectedStartup = null;

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

// ===== Startup List & Search Functions =====

/**
 * Load companies from API
 */
async function loadStartups() {
    const tableBody = document.getElementById('startupsTableBody');
    
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
        
        const url = `/api/startups/?${params.toString()}`;
        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to load companies');
        
        const data = await response.json();
        allStartups = data.companies || [];
        
        // Store pagination info
        if (data.pagination) {
            window.paginationInfo = data.pagination;
        }
        
        displayStartupsInTable(allStartups);
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
function displayStartupsInTable(companies) {
    const tableBody = document.getElementById('startupsTableBody');
    const noResultsMessage = document.getElementById('noResultsMessage');
    const resultsInfo = document.getElementById('resultsInfo');
    const resultsCount = document.getElementById('resultsCount');
    const totalCount = document.getElementById('totalCount');
    
    // Detect if user is admin by checking for edit/delete buttons capability
    const adminBtn = document.getElementById('addStartupBtn');
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
        totalCount.textContent = allStartups.length;
    }
    
    let html = '';
    
    companies.forEach((startup, index) => {
        // Logo HTML
        const logoHtml = startup.logo_url 
            ? `<img src="${startup.logo_url}" alt="${escapeHtml(startup.name)}" class="startup-logo" onerror="this.style.display='none'; this.nextElementSibling?.style.display='flex';">`
            : '';
        
        const logoPlaceholder = !startup.logo_url 
            ? `<div class="logo-placeholder" style="display: flex;">Logo</div>`
            : `<div class="logo-placeholder" style="display: none;">Logo</div>`;
        
        // Action buttons (admin only)
        const actionButtons = isAdmin ? `
            <div class="btn-group-sm" role="group">
                <button class="btn btn-sm btn-warning" onclick="handleEditStartup(${startup.id}); event.stopPropagation();" title="Edit">
                    Edit
                </button>
                <button class="btn btn-sm btn-danger" onclick="handleDeleteStartup(${startup.id}); event.stopPropagation();" title="Delete">
                    Delete
                </button>
            </div>
        ` : '';
        
        // Table row - clickable to show detail
        const actionsCol = isAdmin ? `<td class="actions-col">${actionButtons}</td>` : '';
        
        html += `
            <tr onclick="showStartupDetail(${startup.id})" style="cursor: pointer;">
                <td class="rank-col">${index + 1}</td>
                <td class="logo-col">
                    ${logoHtml}
                    ${logoPlaceholder}
                </td>
                <td class="name-col">${escapeHtml(startup.name)}</td>
                <td class="sector-col">
                    <span class="sector-badge">${escapeHtml(startup.sector)}</span>
                </td>
                <td class="founders-col">${escapeHtml(startup.founders)}</td>
                <td class="hq-col">${escapeHtml(startup.headquarters)}</td>
                <td class="founded-col">${startup.year_founded}</td>
                <td class="funding-col">${escapeHtml(startup.total_funding)}</td>
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
    loadStartups();
}

/**
 * Filter and display companies based on search and sector
 */
function filterAndDisplayCompanies() {
    const searchTerm = document.getElementById('searchInput')?.value.toLowerCase() || '';
    const sectorFilter = document.getElementById('sectorFilter')?.value || '';
    
    let filtered = allStartups;
    
    // Filter by search term
    if (searchTerm) {
        filtered = filtered.filter(startup =>
            startup.name.toLowerCase().includes(searchTerm) ||
            startup.sector.toLowerCase().includes(searchTerm) ||
            startup.headquarters.toLowerCase().includes(searchTerm)
        );
    }
    
    // Filter by sector
    if (sectorFilter) {
        filtered = filtered.filter(startup =>
            startup.sector.toLowerCase() === sectorFilter.toLowerCase()
        );
    }
    
    displayStartupsInTable(filtered);
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

// ===== Add/Edit Startup Functions =====

/**
 * Initialize add startup button
 */
function initAddStartup() {
    const addBtn = document.getElementById('addStartupBtn');
    const submitBtn = document.getElementById('submitStartupBtn');
    
    addBtn?.addEventListener('click', showAddModal);
    submitBtn?.addEventListener('click', handleSaveStartup);
}

/**
 * Show add startup modal
 */
function showAddModal() {
    clearStartupForm();
    document.getElementById('startupModalTitle').textContent = 'Add New Startup';
    document.getElementById('startupId').value = '';
    document.getElementById('submitStartupBtn').textContent = 'Save Startup';
    
    const modal = new bootstrap.Modal(document.getElementById('startupModal'));
    modal.show();
}

/**
 * Clear startup form
 */
function clearStartupForm() {
    document.getElementById('startupForm').reset();
    document.getElementById('startupId').value = '';
}

/**
 * Handle edit startup
 */
function handleEditStartup(id) {
    const startup = allStartups.find(c => c.id === id);
    if (!startup) return;
    
    // Populate form with startup data
    document.getElementById('startupId').value = startup.id;
    document.getElementById('startupName').value = startup.name;
    document.getElementById('startupSector').value = startup.sector;
    document.getElementById('startupFounders').value = startup.founders || '';
    document.getElementById('startupLogoUrl').value = startup.logo_url || '';
    document.getElementById('startupHeadquarters').value = startup.headquarters;
    document.getElementById('startupYearFounded').value = startup.year_founded;
    document.getElementById('startupTotalFunding').value = startup.total_funding || '';
    
    // Update modal title
    document.getElementById('startupModalTitle').textContent = 'Edit Startup';
    document.getElementById('submitStartupBtn').textContent = 'Update Startup';
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('startupModal'));
    modal.show();
}

/**
 * Handle save startup (add or edit)
 */
async function handleSaveStartup() {
    const startupId = document.getElementById('startupId').value;
    const csrfToken = getCsrfToken();
    
    const data = {
        name: document.getElementById('startupName').value,
        sector: document.getElementById('startupSector').value,
        founders: document.getElementById('startupFounders').value,
        logo_url: document.getElementById('startupLogoUrl').value,
        headquarters: document.getElementById('startupHeadquarters').value,
        year_founded: parseInt(document.getElementById('startupYearFounded').value),
        total_funding: document.getElementById('startupTotalFunding').value
    };
    
    // Validate required fields
    if (!data.name || !data.sector || !data.founders || !data.headquarters || !data.year_founded) {
        showAlert('Please fill in all required fields', 'warning');
        return;
    }
    
    try {
        const url = startupId ? 
            `/api/startups/${startupId}/edit/` : 
            '/api/startups/add/';
        
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
            showAlert(result.message || 'Startup saved successfully!', 'success');
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('startupModal'));
            modal?.hide();
            
            // Reload companies list
            loadStartups();
            clearStartupForm();
        } else {
            showAlert(result.message || 'Error saving startup', 'danger');
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert('An error occurred', 'danger');
    }
}

/**
 * Handle delete startup
 */
async function handleDeleteStartup(id) {
    if (!confirm('Are you sure you want to delete this startup? This action cannot be undone.')) {
        return;
    }
    
    const csrfToken = getCsrfToken();
    
    try {
        const response = await fetch(`/api/startups/${id}/delete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('Startup deleted successfully!', 'success');
            loadStartups();
        } else {
            showAlert(result.message || 'Error deleting startup', 'danger');
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
    loadStartups();
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
 * Show startup detail modal
 */
function showStartupDetail(id) {
    const startup = allStartups.find(c => c.id === id);
    if (!startup) return;
    
    selectedStartup = startup;
    
    // Populate modal with data
    document.getElementById('detailLogo').src = startup.logo_url || '';
    document.getElementById('detailName').textContent = startup.name;
    document.getElementById('detailSector').textContent = startup.sector;
    document.getElementById('detailFounders').textContent = startup.founders || 'Not specified';
    document.getElementById('detailHQ').textContent = startup.headquarters;
    document.getElementById('detailFounded').textContent = startup.year_founded;
    document.getElementById('detailFunding').textContent = startup.total_funding || 'Not disclosed';
    
    // Format dates
    const createdDate = new Date(startup.created_at).toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
    document.getElementById('detailCreated').textContent = createdDate;
    
    // Show updated field only if created and updated are different
    const updatedField = document.getElementById('updatedField');
    if (startup.created_at !== startup.updated_at) {
        updatedField.style.display = 'flex';
        const updatedDate = new Date(startup.updated_at).toLocaleDateString('en-US', { 
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
 * Edit startup from detail modal
 */
function editStartupFromDetail() {
    if (!selectedStartup) return;
    
    // Close detail modal
    const detailModal = bootstrap.Modal.getInstance(document.getElementById('detailModal'));
    detailModal?.hide();
    
    // Open edit modal
    setTimeout(() => {
        handleEditStartup(selectedStartup.id);
    }, 300);
}

/**
 * Delete startup from detail modal
 */
function deleteStartupFromDetail() {
    if (!selectedStartup) return;
    
    // Close detail modal
    const detailModal = bootstrap.Modal.getInstance(document.getElementById('detailModal'));
    detailModal?.hide();
    
    // Delete startup
    setTimeout(() => {
        handleDeleteStartup(selectedStartup.id);
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
    loadStartups();
    
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
    loadStartups();
    
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
        loadStartups();
    });
}

// ===== PHASE 12: ADVANCED FILTERING =====

/**
 * Search History Management
 */
const SearchHistory = {
    storageKey: 'bd_startup_search_history',
    maxItems: 10,
    
    /**
     * Add search to history
     */
    add(search, sector) {
        if (!search && !sector) return;
        
        const history = this.getAll();
        const entry = {
            search: search || '',
            sector: sector || '',
            timestamp: new Date().toISOString()
        };
        
        // Remove duplicate if exists
        const filtered = history.filter(h => 
            !(h.search === entry.search && h.sector === entry.sector)
        );
        
        // Add new entry at beginning
        filtered.unshift(entry);
        
        // Keep only maxItems
        if (filtered.length > this.maxItems) {
            filtered.pop();
        }
        
        localStorage.setItem(this.storageKey, JSON.stringify(filtered));
    },
    
    /**
     * Get all search history
     */
    getAll() {
        try {
            const data = localStorage.getItem(this.storageKey);
            return data ? JSON.parse(data) : [];
        } catch (e) {
            console.error('Error reading search history:', e);
            return [];
        }
    },
    
    /**
     * Clear search history
     */
    clear() {
        localStorage.removeItem(this.storageKey);
        updateHistoryUI();
        showAlert('Search history cleared! 🗑️', 'success');
    },
    
    /**
     * Get recent searches (last N)
     */
    getRecent(count = 5) {
        return this.getAll().slice(0, count);
    }
};

/**
 * Filter Presets Management
 */
const FilterPresets = {
    storageKey: 'bd_startup_filter_presets',
    
    /**
     * Save current filters as preset
     */
    save(name) {
        if (!name || name.trim() === '') {
            showAlert('Please enter a preset name', 'error');
            return false;
        }
        
        const presets = this.getAll();
        
        // Check for duplicate name
        if (presets.some(p => p.name.toLowerCase() === name.toLowerCase())) {
            showAlert('Preset with this name already exists', 'error');
            return false;
        }
        
        const preset = {
            id: Date.now(),
            name: name.trim(),
            search: currentSearch,
            sector: currentSector,
            sort: currentSort,
            order: currentOrder,
            limit: currentLimit,
            createdAt: new Date().toISOString()
        };
        
        presets.unshift(preset);
        localStorage.setItem(this.storageKey, JSON.stringify(presets));
        showAlert(`Preset "${name}" saved! 💾`, 'success');
        updatePresetsUI();
        return true;
    },
    
    /**
     * Load preset
     */
    load(id) {
        const presets = this.getAll();
        const preset = presets.find(p => p.id === id);
        
        if (!preset) return false;
        
        // Apply preset filters
        currentSearch = preset.search;
        currentSector = preset.sector;
        currentSort = preset.sort;
        currentOrder = preset.order;
        currentLimit = preset.limit;
        currentPage = 1;
        
        // Update UI
        document.getElementById('searchInput').value = currentSearch;
        document.getElementById('sectorFilter').value = currentSector;
        document.getElementById('pageLimitSelect').value = currentLimit;
        
        // Reload data
        loadStartups();
        showAlert(`Loaded preset: "${preset.name}" 📋`, 'success');
        return true;
    },
    
    /**
     * Delete preset
     */
    delete(id) {
        const presets = this.getAll();
        const filtered = presets.filter(p => p.id !== id);
        localStorage.setItem(this.storageKey, JSON.stringify(filtered));
        updatePresetsUI();
    },
    
    /**
     * Get all presets
     */
    getAll() {
        try {
            const data = localStorage.getItem(this.storageKey);
            return data ? JSON.parse(data) : [];
        } catch (e) {
            console.error('Error reading presets:', e);
            return [];
        }
    },
    
    /**
     * Clear all presets
     */
    clear() {
        localStorage.removeItem(this.storageKey);
        updatePresetsUI();
        showAlert('All presets cleared! 🗑️', 'success');
    },
    
    /**
     * Export presets as JSON
     */
    export() {
        const presets = this.getAll();
        const dataStr = JSON.stringify(presets, null, 2);
        const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
        
        const exportFileDefaultName = 'filter_presets.json';
        const linkElement = document.createElement('a');
        linkElement.setAttribute('href', dataUri);
        linkElement.setAttribute('download', exportFileDefaultName);
        linkElement.click();
        
        showAlert('Presets exported! 📥', 'success');
    },
    
    /**
     * Import presets from JSON
     */
    import(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const imported = JSON.parse(e.target.result);
                if (!Array.isArray(imported)) throw new Error('Invalid format');
                
                const existing = this.getAll();
                const merged = [...imported, ...existing];
                
                localStorage.setItem(this.storageKey, JSON.stringify(merged));
                updatePresetsUI();
                showAlert(`Imported ${imported.length} presets! 📤`, 'success');
            } catch (err) {
                showAlert('Invalid preset file!', 'error');
            }
        };
        reader.readAsText(file);
    }
};

/**
 * Update search history UI dropdown
 */
function updateHistoryUI() {
    const dropdown = document.getElementById('searchHistoryDropdown');
    if (!dropdown) return;
    
    const history = SearchHistory.getRecent(8);
    
    if (history.length === 0) {
        dropdown.innerHTML = '<div class="dropdown-item disabled text-muted">No search history</div>';
        return;
    }
    
    let html = '';
    history.forEach((entry, index) => {
        const search = entry.search || '(no search)';
        const sector = entry.sector ? ` • ${entry.sector}` : '';
        const label = `${search}${sector}`;
        html += `<a class="dropdown-item" href="#" onclick="applyHistoryEntry(${index}); return false;">
            <small>${label}</small>
        </a>`;
    });
    
    html += '<div class="dropdown-divider"></div>';
    html += '<a class="dropdown-item" href="#" onclick="SearchHistory.clear(); return false;">🗑️ Clear History</a>';
    
    dropdown.innerHTML = html;
}

/**
 * Apply history entry
 */
function applyHistoryEntry(index) {
    const history = SearchHistory.getRecent(8);
    const entry = history[index];
    
    if (!entry) return;
    
    currentSearch = entry.search;
    currentSector = entry.sector;
    currentPage = 1;
    
    document.getElementById('searchInput').value = currentSearch;
    document.getElementById('sectorFilter').value = currentSector;
    
    loadStartups();
    showAlert('Applied history entry', 'info');
}

/**
 * Update presets UI dropdown
 */
function updatePresetsUI() {
    const dropdown = document.getElementById('presetsDropdown');
    if (!dropdown) return;
    
    const presets = FilterPresets.getAll();
    
    if (presets.length === 0) {
        dropdown.innerHTML = '<div class="dropdown-item disabled text-muted">No saved presets</div>';
        return;
    }
    
    let html = '<div style="max-height: 300px; overflow-y: auto;">';
    presets.forEach(preset => {
        html += `<div class="dropdown-item" style="display: flex; justify-content: space-between; align-items: center;">
            <a href="#" onclick="FilterPresets.load(${preset.id}); return false;" style="flex: 1; text-decoration: none; color: inherit;">
                <small><strong>${preset.name}</strong></small><br>
                <small style="color: #666;">${preset.search || '(no filter)'}${preset.sector ? ' • ' + preset.sector : ''}</small>
            </a>
            <button class="btn btn-sm btn-link text-danger" onclick="FilterPresets.delete(${preset.id}); updatePresetsUI(); return false;" title="Delete preset">🗑️</button>
        </div>`;
    });
    html += '</div>';
    html += '<div class="dropdown-divider"></div>';
    html += `<a class="dropdown-item" href="#" onclick="savePresetDialog(); return false;">➕ Save Current</a>`;
    html += `<a class="dropdown-item" href="#" onclick="document.getElementById('presetsImport').click(); return false;">📤 Import</a>`;
    html += `<a class="dropdown-item" href="#" onclick="FilterPresets.export(); return false;">📥 Export</a>`;
    html += `<a class="dropdown-item" href="#" onclick="FilterPresets.clear(); return false;">🗑️ Clear All</a>`;
    
    dropdown.innerHTML = html;
}

/**
 * Show save preset dialog
 */
function savePresetDialog() {
    const name = prompt('Enter preset name:', '');
    if (name !== null) {
        FilterPresets.save(name);
    }
}

/**
 * Handle preset file import
 */
function handlePresetsImport(event) {
    const file = event.target.files[0];
    if (file) {
        FilterPresets.import(file);
        event.target.value = ''; // Reset file input
    }
}

/**
 * Initialize advanced filtering
 */
function initAdvancedFiltering() {
    // Update history when search changes
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        const originalOninput = searchInput.oninput;
        searchInput.addEventListener('change', function() {
            SearchHistory.add(this.value, currentSector);
            updateHistoryUI();
        });
    }
    
    // Update history when sector changes
    const sectorFilter = document.getElementById('sectorFilter');
    if (sectorFilter) {
        sectorFilter.addEventListener('change', function() {
            SearchHistory.add(currentSearch, this.value);
            updateHistoryUI();
        });
    }
    
    // Create hidden file input for preset import
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.id = 'presetsImport';
    fileInput.accept = '.json';
    fileInput.style.display = 'none';
    fileInput.addEventListener('change', handlePresetsImport);
    document.body.appendChild(fileInput);
    
    // Initialize UI
    updateHistoryUI();
    updatePresetsUI();
}

// ===== PHASE 13B: ANALYTICS DASHBOARD =====

let analyticCharts = {}; // Store chart instances for cleanup

/**
 * Show analytics dashboard modal
 */
function showAnalyticsDashboard() {
    const modal = new bootstrap.Modal(document.getElementById('analyticsDashboardModal'));
    modal.show();
    
    // Load analytics data
    loadAnalyticsData();
}

/**
 * Load analytics data from backend
 */
function loadAnalyticsData() {
    fetch('/api/analytics/dashboard/')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayAnalyticsData(data);
            } else {
                showAlert('Error loading analytics', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('Failed to load analytics', 'error');
        });
}

/**
 * Display analytics data and create charts
 */
function displayAnalyticsData(data) {
    const stats = data.statistics;
    const sectors = data.sector_distribution;
    const decades = data.decade_stats;
    const recent = data.recent_companies;
    
    // Update stat cards
    document.getElementById('totalCompaniesCard').textContent = stats.total_companies;
    document.getElementById('totalSectorsCard').textContent = stats.total_sectors;
    document.getElementById('avgFoundedCard').textContent = stats.avg_founded_year || '--';
    
    const yearRange = stats.founded_year_range;
    if (yearRange.min && yearRange.max) {
        document.getElementById('yearRangeCard').textContent = 
            `${yearRange.min} - ${yearRange.max}`;
    }
    
    // Create sector chart
    createSectorChart(sectors);
    
    // Create decade chart
    createDecadeChart(decades);
    
    // Display recent companies
    displayRecentCompanies(recent);
}

/**
 * Create sector distribution chart
 */
function createSectorChart(sectors) {
    // Destroy existing chart if it exists
    if (analyticCharts.sectorChart) {
        analyticCharts.sectorChart.destroy();
    }
    
    const ctx = document.getElementById('sectorChart');
    if (!ctx) return;
    
    const labels = sectors.map(s => s.sector);
    const data = sectors.map(s => s.count);
    
    const colors = [
        '#0a66bd', '#2c5aa0', '#d4af37', '#ff6b6b', '#4dabf7',
        '#51cf66', '#ffd43b', '#a78bfa', '#fb7185', '#06b6d4'
    ];
    
    analyticCharts.sectorChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors.slice(0, data.length),
                borderColor: '#fff',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

/**
 * Create decade distribution chart
 */
function createDecadeChart(decades) {
    // Destroy existing chart if it exists
    if (analyticCharts.decadeChart) {
        analyticCharts.decadeChart.destroy();
    }
    
    const ctx = document.getElementById('decadeChart');
    if (!ctx) return;
    
    const labels = Object.keys(decades).sort();
    const data = labels.map(label => decades[label]);
    
    analyticCharts.decadeChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Companies Founded',
                data: data,
                backgroundColor: '#0a66bd',
                borderColor: '#083f87',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            },
            plugins: {
                legend: {
                    display: true
                }
            }
        }
    });
}

/**
 * Display recently added companies
 */
function displayRecentCompanies(companies) {
    const container = document.getElementById('recentCompaniesList');
    
    if (!companies || companies.length === 0) {
        container.innerHTML = '<p class="text-muted text-center">No recent companies</p>';
        return;
    }
    
    let html = '<div class="recent-list">';
    companies.forEach(startup => {
        html += `
            <div class="recent-item">
                <div class="recent-header">
                    <strong>${startup.name}</strong>
                    <span class="badge bg-primary">${startup.sector}</span>
                </div>
                <div class="recent-details">
                    <small>Founded: ${startup.founded} | Added: ${startup.created_at}</small>
                </div>
            </div>
        `;
    });
    html += '</div>';
    
    container.innerHTML = html;
}

/**
 * Export analytics report as PDF/JSON
 */
function exportAnalytics() {
    fetch('/api/analytics/dashboard/')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const dataStr = JSON.stringify(data, null, 2);
                const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
                
                const exportFileDefaultName = 'analytics_report.json';
                const linkElement = document.createElement('a');
                linkElement.setAttribute('href', dataUri);
                linkElement.setAttribute('download', exportFileDefaultName);
                linkElement.click();
                
                showAlert('Analytics report exported! 📥', 'success');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('Failed to export analytics', 'error');
        });
}

/**
 * Compare multiple companies
 */
function compareCompanies(ids) {
    const queryString = ids.map(id => `ids=${id}`).join('&');
    
    fetch(`/api/analytics/comparison/?${queryString}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert(`Comparing ${data.companies.length} companies`, 'info');
                console.log('Comparison data:', data);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('Failed to compare companies', 'error');
        });
}

/**
 * Get sector insights
 */
function getSectorInsights(sector) {
    fetch(`/api/analytics/sector/?sector=${encodeURIComponent(sector)}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Sector insights:', data.insights);
                showAlert(`${sector}: ${data.insights.startup_count} companies`, 'info');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('Failed to get sector insights', 'error');
        });
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('App initialized');
    loadStartups();
    loadStats();
    initSearch();
    initSectorFilter();
    initAddStartup();
    initKeyboardNavigation();
    initPaginationSizeSelector();
    initAdvancedFiltering();
});

