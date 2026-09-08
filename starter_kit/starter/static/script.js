// Arogya Bhoomi — Global Scripts
// Vanilla JavaScript for enterprise UI controls

document.addEventListener('DOMContentLoaded', function () {
    // Close sidebar on mobile when a link is clicked
    const sidebarLinks = document.querySelectorAll('.sidebar-link');
    sidebarLinks.forEach(function (link) {
        link.addEventListener('click', function () {
            const sidebar = document.getElementById('sidebarNav');
            if (sidebar && window.innerWidth <= 992) {
                sidebar.classList.remove('open');
            }
        });
    });
});
