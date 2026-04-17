class AdminDashboard {
    constructor() {
        this.chart = null;
    }

    async init() {
        if (this.initialized) {
            this.refreshData();
            return;
        }
        this.initChart();
        this.refreshData();
        // Auto refresh every 10 seconds for Demo responsiveness
        setInterval(() => this.refreshData(), 10000);
        this.initialized = true;
    }

    initChart() {
        if (this.chart) {
            this.chart.destroy();
        }
        const ctx = document.getElementById('activityChart').getContext('2d');
        this.chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Total Queries',
                    data: [],
                    backgroundColor: 'rgba(99, 102, 241, 0.8)',
                    borderColor: '#6366f1',
                    borderWidth: 2,
                    borderRadius: 15,
                    borderSkipped: false,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { 
                        grid: { display: false }, 
                        ticks: { color: '#94a3b8' } 
                    },
                    y: { 
                        beginAtZero: true,
                        // Remove suggestedMax to allow Autoscale (Senior UX choice)
                        grid: { 
                            color: 'rgba(255,255,255,0.08)',
                            drawBorder: false 
                        }, 
                        ticks: { 
                            color: '#94a3b8', 
                            precision: 0 // Only whole numbers for chats
                        } 
                    }
                }
            }
        });
    }

    async refreshData() {
        try {
            const data = await auth.fetchWithAuth('/admin/analytics');
            this.updateStats(data);
            this.updateChart(data.activity_trend);
            this.updateHealth(data.system_health);
            
            const logs = await auth.fetchWithAuth('/admin/logs');
            this.updateLogsTable(logs);
            
            const users = await auth.fetchWithAuth('/admin/users');
            this.updateUserTable(users);
        } catch (err) {
            console.error("Admin refresh failed", err);
        }
    }

    updateStats(data) {
        document.getElementById('stat-chats').innerText = data.total_chats;
        document.getElementById('stat-docs').innerText = data.total_documents;
    }

    updateChart(trend) {
        if (!this.chart) return;
        this.chart.data.labels = trend.map(t => t.date);
        this.chart.data.datasets[0].data = trend.map(t => t.count);
        this.chart.update();
    }

    updateHealth(health) {
        document.getElementById('cpu-bar').style.width = `${health.cpu_usage}%`;
        document.getElementById('cpu-text').innerText = `${health.cpu_usage}%`;
        
        document.getElementById('ram-bar').style.width = `${health.memory_usage}%`;
        document.getElementById('ram-text').innerText = `${health.memory_usage}%`;
    }

    updateUserTable(users) {
        const tbody = document.querySelector('#user-table tbody');
        if (!tbody) return;
        tbody.innerHTML = '';
        
        // Sort by Newest First for Demo
        users.sort((a, b) => (b.id || 0) > (a.id || 0) ? 1 : -1);

        users.forEach(user => {
            const tr = document.createElement('tr');
            const statusText = user.is_verified ? 'Authorized' : 'Pending';
            const statusClass = user.is_verified ? 'text-success' : 'text-danger';
            
            tr.innerHTML = `
                <td>${user.name || 'Staff User'}</td>
                <td>${user.email}</td>
                <td><span class="badge">${user.role}</span></td>
                <td><span class="status-cell ${statusClass}">${statusText}</span></td>
                <td>
                    <button onclick="adminDashboard.deleteUser('${user.id}')" class="btn-delete-doc" style="position:static; padding: 6px 10px;">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    }

    async deleteUser(userId) {
        if (!confirm("Are you sure you want to PERMANENTLY delete this employee account? This cannot be undone.")) {
            return;
        }

        try {
            const res = await auth.fetchWithAuth(`/admin/users/${userId}`, {
                method: 'DELETE'
            });
            alert("Employee account removed successfully.");
            this.refreshData(); // Live refresh
        } catch (err) {
            alert("Error: " + err.message);
        }
    }

    updateLogsTable(logs) {
        const tbody = document.querySelector('#logs-table tbody');
        if (!tbody) return;
        tbody.innerHTML = '';
        
        logs.forEach(log => {
            const tr = document.createElement('tr');
            
            // Standardize Date Parsing
            const timeStr = log.timestamp || log.created_at;
            const time = timeStr ? new Date(timeStr).toLocaleTimeString() : 'Recent';
            
            // Support multiple possible field names to prevent 'undefined' (Migration Resilience)
            const userEmail = log.user_email || log.user_id || 'System';
            const userRef = userEmail.includes('@') ? userEmail.split('@')[0] : userEmail;
            
            const queryText = log.message || log.query || 'Admin Interaction';
            const responseText = log.response || log.content || 'Processing...';
            const preview = responseText.length > 70 ? responseText.substring(0, 70) + '...' : responseText;
            
            tr.innerHTML = `
                <td style="color: var(--primary); font-weight: bold">${time}</td>
                <td style="text-transform: capitalize">${userRef}</td>
                <td style="max-width: 250px; overflow: hidden; text-overflow: ellipsis">${queryText}</td>
                <td style="color: var(--text-muted); font-size: 0.85rem; font-style: italic">${preview}</td>
            `;
            tbody.appendChild(tr);
        });
    }
}

const adminDashboard = new AdminDashboard();
