// Application Glue & Tab Switching Logic
window.addEventListener('load', () => {
    // Hide loader
    setTimeout(() => {
        document.getElementById('loader').classList.add('hidden');
    }, 1000);

    if (auth.token && auth.user) {
        showApp();
    }
});

function showApp() {
    document.getElementById('auth-section').classList.add('hidden');
    document.getElementById('app-section').classList.remove('hidden');
    
    // Update User Profile UI
    document.getElementById('user-name').innerText = auth.user.email.split('@')[0];
    document.getElementById('user-role').innerText = auth.user.role.toUpperCase();
    
    // Role-based Nav
    if (auth.user.role === 'admin') {
        document.getElementById('admin-nav').classList.remove('hidden');
    }

    // Initialize Components
    chatEngine.loadHistory();
    loadDocuments();
}

function showTab(tabName) {
    // Nav links update
    document.querySelectorAll('.nav-links li').forEach(li => li.classList.remove('active'));
    document.querySelector(`[onclick="showTab('${tabName}')"]`).classList.add('active');

    // Content update
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    document.getElementById(`${tabName}-tab`).classList.add('active');

    // Trigger component refresh if needed
    if (tabName === 'admin') adminDashboard.init();
    if (tabName === 'documents') loadDocuments();

    // Responsive: Close sidebar on tab selection (Mobile)
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    if (window.innerWidth <= 768) {
        sidebar.classList.remove('active');
        overlay.classList.remove('active');
    }
}

function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    sidebar.classList.toggle('active');
    overlay.classList.toggle('active');
}

// Global Login Handler
async function handleLogin() {
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    
    try {
        await auth.login(email, password);
        document.getElementById('login-form').classList.add('hidden');
        document.getElementById('signup-form').classList.add('hidden');
        document.getElementById('otp-form').classList.remove('hidden');
    } catch (err) {
        alert(err.message);
    }
}

async function handleRegister() {
    const name = document.getElementById('signup-name').value;
    const email = document.getElementById('signup-email').value;
    const password = document.getElementById('signup-password').value;
    
    if (!name || !email || !password) return alert("Please fill all fields");
    
    try {
        // Use Employee as default role
        const result = await auth.fetchWithAuth('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ name, email, password, role: 'employee' })
        });
        
        alert("Account created for " + name + "! Please log in to receive your OTP.");
        toggleAuthForm('login');
    } catch (err) {
        alert(err.message || "Registration failed");
    }
}

function toggleAuthForm(type) {
    if (type === 'signup') {
        document.getElementById('login-form').classList.add('hidden');
        document.getElementById('signup-form').classList.remove('hidden');
    } else {
        document.getElementById('signup-form').classList.add('hidden');
        document.getElementById('login-form').classList.remove('hidden');
    }
}

async function handleVerifyOTP() {
    const otp = document.getElementById('otp-code').value;
    try {
        await auth.verifyOTP(otp);
        showApp();
    } catch (err) {
        alert(err.message);
    }
}

// Knowledge Base Logic
async function loadDocuments() {
    try {
        const docs = await auth.fetchWithAuth('/documents');
        const grid = document.getElementById('doc-list');
        grid.innerHTML = '';
        
        docs.forEach(doc => {
            const isImage = (doc.content_type || '').startsWith('image/');
            const icon = isImage ? 'fa-file-image' : 'fa-file-lines';
            
            // Map MIME types to pure short extensions
            let typeLabel = 'DOC';
            if (doc.content_type?.includes('pdf')) typeLabel = 'PDF';
            if (doc.content_type?.includes('word')) typeLabel = 'DOCX';
            if (doc.content_type?.includes('image')) typeLabel = 'IMG';

            const card = document.createElement('div');
            card.className = 'glass-card doc-card';
            const isAdmin = auth.user && auth.user.role === 'admin';
            card.innerHTML = `
                <span class="type-badge">${typeLabel}</span>
                ${isAdmin ? `
                <button class="btn-delete-doc" onclick="deleteDocument('${doc.id}')" title="Delete Document">
                    <i class="fas fa-trash-can"></i>
                </button>
                ` : ''}
                <div style="display:flex; gap:15px; align-items:start">
                    <i class="fas ${icon}" style="font-size: 1.5rem; color: var(--primary)"></i>
                    <div class="doc-info">
                        <h4>${doc.filename}</h4>
                        <p style="font-size: 0.85rem; color: var(--text-muted); line-height: 1.4">${doc.summary || 'AI Analysis pending...'}</p>
                        <div class="keywords">
                            ${(doc.keywords || []).map(k => `<span class="keyword">#${k}</span>`).join('')}
                        </div>
                    </div>
                </div>
            `;
            grid.appendChild(card);
        });
    } catch (err) {
        console.error("Doc load failed", err);
    }
}

async function deleteDocument(docId) {
    if (!confirm("Are you sure you want to delete this document?")) return;
    
    try {
        const response = await auth.fetchWithAuth(`/documents/${docId}`, {
            method: 'DELETE'
        });
        
        if (response.message) {
            loadDocuments(); // Refresh the list
        }
    } catch (err) {
        console.error("Deletion failed", err);
        alert("Failed to delete document");
    }
}

async function uploadDocument(file) {
    if (!file) return;
    
    const zone = document.querySelector('.upload-zone');
    const originalContent = zone.innerHTML;
    
    // Visual Feedback: Start Processing
    zone.innerHTML = `<i class="fas fa-spinner fa-spin"></i><p>Analyzing document with AI... Please wait</p>`;
    zone.style.pointerEvents = 'none';
    zone.style.opacity = '0.7';

    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch(`${API_URL}/documents/upload/`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${auth.token}` },
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Instant UI Refresh
            await loadDocuments();
            alert("Document uploaded and analyzed successfully!");
        } else {
            alert(data.detail || "Upload failed");
        }
    } catch (err) {
        alert("Network error during upload");
    } finally {
        // Reset UI
        zone.innerHTML = originalContent;
        zone.style.pointerEvents = 'all';
        zone.style.opacity = '1';
    }
}
