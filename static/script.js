document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('mainForm');
    const loadingOverlay = document.createElement('div');
    loadingOverlay.className = 'loading-overlay';
    loadingOverlay.innerHTML = `
        <div class="loading-content">
            <div class="spinner"></div>
            <h3>Generating Your Master Plan</h3>
            <p>Analyzing market trends · Optimizing strategies</p>
        </div>
    `;
    document.body.appendChild(loadingOverlay);

    form.addEventListener('submit', function(e) {
        loadingOverlay.style.display = 'flex';
    });

    document.querySelectorAll('.accordion-button').forEach(button => {
        button.addEventListener('click', () => {
            button.classList.toggle('active');
        });
    });

    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.forEach(tooltipTriggerEl => {
        new bootstrap.Tooltip(tooltipTriggerEl);
    });

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate__fadeInUp');
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.roadmap-section').forEach((section) => {
        observer.observe(section);
    });
    document.querySelectorAll('.delete-plan').forEach(btn => {
        btn.addEventListener('click', function() {
            const planId = this.dataset.planId;
            const form = document.getElementById('deleteForm');
            form.action = `/admin/plans/${planId}/delete`;
        });
    });

    document.getElementById('deleteForm').addEventListener('submit', function(e) {
        const submitBtn = this.querySelector('button[type="submit"]');
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Deleting...';
        submitBtn.disabled = true;
    });
});
