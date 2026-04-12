window.toggleFiltros = function() {
    const sidebar = document.getElementById('sidebar-filtros');
    const btnShow = document.getElementById('btn-show-filtros');
    
    if (!sidebar || !btnShow) return;

    if (sidebar.style.width === '0px') {
        // Si está cerrado, lo abrimos
        sidebar.style.width = '300px';
        sidebar.style.padding = '20px';
        btnShow.style.display = 'none';
    } else {
        // Si está abierto, lo cerramos
        sidebar.style.width = '0px';
        sidebar.style.padding = '20px 0px'; // Mantener padding vertical, quitar horizontal
        btnShow.style.display = 'block';
    }
}