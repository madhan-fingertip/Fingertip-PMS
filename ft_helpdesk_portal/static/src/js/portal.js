/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

/**
 * FT Helpdesk Portal JavaScript
 * Handles dynamic form interactions on the ticket creation page.
 */
function _initPortal() {

    // =============================
    // Category -> Subcategory
    // =============================
    const categorySelect = document.getElementById('category_id');
    const subcategoryWrapper = document.getElementById('subcategory_wrapper');
    const subcategorySelect = document.getElementById('subcategory_id');

    if (categorySelect) {
        categorySelect.addEventListener('change', async function () {
            const categoryId = this.value;
            if (!categoryId) {
                if (subcategoryWrapper) subcategoryWrapper.style.display = 'none';
                return;
            }
            try {
                const response = await fetch('/my/support/subcategories', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        jsonrpc: '2.0',
                        method: 'call',
                        params: { category_id: parseInt(categoryId) },
                    }),
                });
                const data = await response.json();
                const subcategories = data.result || [];

                if (subcategories.length > 0) {
                    subcategorySelect.innerHTML = '<option value="">-- Select Subcategory --</option>';
                    subcategories.forEach(function (sub) {
                        const opt = document.createElement('option');
                        opt.value = sub.id;
                        opt.textContent = sub.name;
                        subcategorySelect.appendChild(opt);
                    });
                    subcategoryWrapper.style.display = '';
                } else {
                    subcategoryWrapper.style.display = 'none';
                }
            } catch (e) {
                console.error('Error fetching subcategories:', e);
            }
        });
    }

    // =============================
    // Type -> Dynamic Fields
    // =============================
    const typeSelect = document.getElementById('type_id');
    const dynamicContainer = document.getElementById('dynamic_fields_container');
    const dynamicBody = document.getElementById('dynamic_fields_body');

    if (typeSelect) {
        typeSelect.addEventListener('change', async function () {
            const typeId = this.value;
            if (!typeId) {
                if (dynamicContainer) dynamicContainer.style.display = 'none';
                return;
            }
            try {
                const response = await fetch('/my/support/dynamic_fields', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        jsonrpc: '2.0',
                        method: 'call',
                        params: { type_id: parseInt(typeId) },
                    }),
                });
                const data = await response.json();
                const fields = data.result || [];

                if (fields.length > 0) {
                    dynamicBody.innerHTML = '';
                    fields.forEach(function (field) {
                        const col = document.createElement('div');
                        col.className = 'col-md-6 mb-3';
                        let inputHtml = '';
                        const fieldName = 'dynamic_' + field.name;
                        const required = field.required ? 'required' : '';

                        switch (field.type) {
                            case 'text':
                                inputHtml = `<textarea name="${fieldName}" class="form-control"
                                    placeholder="${field.placeholder}" rows="3" ${required}></textarea>`;
                                break;
                            case 'boolean':
                                inputHtml = `<div class="form-check mt-2">
                                    <input type="checkbox" name="${fieldName}" class="form-check-input"
                                        id="field_${field.name}" value="1">
                                    <label class="form-check-label" for="field_${field.name}">${field.label}</label>
                                </div>`;
                                break;
                            case 'selection':
                                let options = '<option value="">-- Select --</option>';
                                (field.options || []).forEach(function (opt) {
                                    options += `<option value="${opt}">${opt}</option>`;
                                });
                                inputHtml = `<select name="${fieldName}" class="form-select" ${required}>
                                    ${options}</select>`;
                                break;
                            case 'date':
                                inputHtml = `<input type="date" name="${fieldName}" class="form-control"
                                    placeholder="${field.placeholder}" ${required}>`;
                                break;
                            case 'datetime':
                                inputHtml = `<input type="datetime-local" name="${fieldName}" class="form-control"
                                    placeholder="${field.placeholder}" ${required}>`;
                                break;
                            case 'integer':
                                inputHtml = `<input type="number" name="${fieldName}" class="form-control"
                                    placeholder="${field.placeholder}" step="1" ${required}>`;
                                break;
                            case 'float':
                                inputHtml = `<input type="number" name="${fieldName}" class="form-control"
                                    placeholder="${field.placeholder}" step="0.01" ${required}>`;
                                break;
                            case 'url':
                                inputHtml = `<input type="url" name="${fieldName}" class="form-control"
                                    placeholder="${field.placeholder || 'https://...'}" ${required}>`;
                                break;
                            case 'email':
                                inputHtml = `<input type="email" name="${fieldName}" class="form-control"
                                    placeholder="${field.placeholder || 'email@example.com'}" ${required}>`;
                                break;
                            default:
                                inputHtml = `<input type="text" name="${fieldName}" class="form-control"
                                    placeholder="${field.placeholder}" ${required}>`;
                        }

                        const label = field.type !== 'boolean'
                            ? `<label class="form-label fw-medium">
                                ${field.label}${field.required ? ' <span class="text-danger">*</span>' : ''}
                               </label>`
                            : '';
                        const helpText = field.help_text
                            ? `<div class="form-text">${field.help_text}</div>`
                            : '';

                        col.innerHTML = label + inputHtml + helpText;
                        dynamicBody.appendChild(col);
                    });
                    dynamicContainer.style.display = '';
                } else {
                    dynamicContainer.style.display = 'none';
                }
            } catch (e) {
                console.error('Error fetching dynamic fields:', e);
            }
        });
    }

    // =============================
    // KB Suggestions (on subject input)
    // =============================
    const subjectInput = document.getElementById('ticket_subject');
    const kbSuggestions = document.getElementById('kb_suggestions');
    const kbSuggestionsList = document.getElementById('kb_suggestions_list');
    let suggestTimeout = null;

    if (subjectInput && kbSuggestions) {
        subjectInput.addEventListener('input', function () {
            clearTimeout(suggestTimeout);
            const query = this.value.trim();
            if (query.length < 3) {
                kbSuggestions.style.display = 'none';
                return;
            }
            suggestTimeout = setTimeout(async function () {
                try {
                    const catId = categorySelect ? categorySelect.value : '';
                    let url = `/my/support/kb/suggest?q=${encodeURIComponent(query)}`;
                    if (catId) url += `&category_id=${catId}`;

                    const response = await fetch(url);
                    if (!response.ok) {
                        kbSuggestions.style.display = 'none';
                        return;
                    }
                    const articles = await response.json();

                    if (articles && articles.length > 0) {
                        kbSuggestionsList.innerHTML = '';
                        articles.forEach(function (article) {
                            const link = document.createElement('a');
                            link.href = `/my/support/kb/${article.slug}`;
                            link.target = '_blank';
                            link.className = 'kb-suggestion-item';
                            link.innerHTML = `<i class="fa fa-file-text-o me-2"></i>${article.title}`;
                            kbSuggestionsList.appendChild(link);
                        });
                        kbSuggestions.style.display = '';
                    } else {
                        kbSuggestions.style.display = 'none';
                    }
                } catch (e) {
                    kbSuggestions.style.display = 'none';
                }
            }, 500);
        });
    }

    // =============================
    // AJAX Tab Switching
    // =============================
    // (Handled by publicWidget below)
}

// Ensure init runs whether DOMContentLoaded already fired or not
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', _initPortal);
} else {
    _initPortal();
}

// =============================
// AJAX Tab Switching Widget
// =============================
const TAB_URLS = ['/my/support/tickets', '/my/support/milestones', '/my/support/releases', '/my/support/kb'];

function getTabBaseUrl(url) {
    try {
        const path = new URL(url, window.location.origin).pathname;
        return TAB_URLS.find(function (t) { return path.startsWith(t); }) || null;
    } catch (_e) {
        return null;
    }
}

function isTabPageLink(href) {
    if (!href) return false;
    try {
        const path = new URL(href, window.location.origin).pathname;
        return TAB_URLS.some(function (t) {
            if (path === t) return true;
            // Allow filter/sort URLs (same base path, no further sub-path segments)
            var rest = path.replace(t, '').replace(/^\//, '');
            return path.startsWith(t) && !rest.includes('/') && rest === '';
        });
    } catch (_e) {
        return false;
    }
}

publicWidget.registry.FtSupportTabs = publicWidget.Widget.extend({
    selector: '.ft-support-portal',

    start: function () {
        var self = this;
        console.log('[FtSupportTabs] Widget initialized on', this.el);
        this._isLoading = false;
        this._tabContainer = this.el.querySelector('.ft-support-tabs');
        this._contentContainer = this.el.querySelector('.ft-tab-content');
        console.log('[FtSupportTabs] tabContainer:', !!this._tabContainer, 'contentContainer:', !!this._contentContainer);
        if (this._tabContainer && this._contentContainer) {
            this._attachTabListeners();
            this._attachContentListeners();
            history.replaceState({ ftAjax: true, url: window.location.href }, '', window.location.href);
            this._onPopState = this._onPopState.bind(this);
            window.addEventListener('popstate', this._onPopState);
        }
        return this._super.apply(this, arguments);
    },

    destroy: function () {
        if (this._onPopState) {
            window.removeEventListener('popstate', this._onPopState);
        }
        return this._super.apply(this, arguments);
    },

    _onPopState: function (e) {
        if (e.state && e.state.ftAjax && e.state.url) {
            this._loadContent(e.state.url, false);
        }
    },

    _setActiveTab: function (url) {
        var baseUrl = getTabBaseUrl(url);
        if (!baseUrl || !this._tabContainer) return;
        this._tabContainer.querySelectorAll('.nav-link').forEach(function (link) {
            var linkHref = link.getAttribute('href');
            if (linkHref && baseUrl.startsWith(linkHref.split('?')[0])) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    },

    _loadContent: async function (url, doPushState) {
        if (this._isLoading) return;
        this._isLoading = true;
        var contentEl = this._contentContainer;
        contentEl.style.opacity = '0.5';
        contentEl.style.pointerEvents = 'none';
        try {
            var response = await fetch(url, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                credentials: 'same-origin',
            });
            if (!response.ok) throw new Error('Request failed');
            var html = await response.text();
            var parser = new DOMParser();
            var doc = parser.parseFromString(html, 'text/html');
            var newContent = doc.querySelector('.ft-tab-content');
            if (newContent) {
                contentEl.innerHTML = newContent.innerHTML;
            }
            this._setActiveTab(url);
            if (doPushState) {
                history.pushState({ ftAjax: true, url: url }, '', url);
            }
            this._attachContentListeners();
        } catch (_e) {
            window.location.href = url;
        } finally {
            contentEl.style.opacity = '';
            contentEl.style.pointerEvents = '';
            this._isLoading = false;
        }
    },

    _attachTabListeners: function () {
        var self = this;
        this._tabContainer.querySelectorAll('.nav-link').forEach(function (link) {
            link.addEventListener('click', function (e) {
                e.preventDefault();
                self._loadContent(this.getAttribute('href'), true);
            });
        });
    },

    _attachContentListeners: function () {
        var self = this;
        if (!this._contentContainer) return;
        // Intercept filter/sort links
        this._contentContainer.querySelectorAll('a').forEach(function (link) {
            var href = link.getAttribute('href');
            if (href && isTabPageLink(href)) {
                link.addEventListener('click', function (e) {
                    e.preventDefault();
                    self._loadContent(href, true);
                });
            }
        });
        // Intercept search forms
        this._contentContainer.querySelectorAll('form').forEach(function (form) {
            var action = form.getAttribute('action');
            if (action && isTabPageLink(action)) {
                form.addEventListener('submit', function (e) {
                    e.preventDefault();
                    var formData = new FormData(form);
                    var params = new URLSearchParams(formData).toString();
                    var url = action + (params ? '?' + params : '');
                    self._loadContent(url, true);
                });
            }
        });
    },
});
