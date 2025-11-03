async function fetchData(headersLength) {
    try {
        const response = await fetch('/get_info');
        const data = await response.json();

        const tbody = document.getElementById('table-body');
        tbody.innerHTML = '';

        data.forEach(row => {
            const tr = document.createElement('tr');
            tr.classList.add('hover:bg-gray-600', 'transition', 'duration-150');

            row.forEach((cell, index) => {
                const td = document.createElement('td');
                td.classList.add('px-6', 'py-4', 'whitespace-nowrap', 'text-sm', 'text-white');
                td.textContent = cell;

                tr.appendChild(td);
            });

            tbody.appendChild(tr);
        });

        // Update last updated time
        const now = new Date();
        document.getElementById('last-updated').textContent = now.toLocaleTimeString();

    } catch (error) {
        console.error('Error fetching data:', error);
        // Display error message to user
        const tbody = document.getElementById('table-body');
        const errorRow = document.createElement('tr');
        const errorCell = document.createElement('td');
        errorCell.setAttribute('colspan', headersLength);
        errorCell.classList.add('px-6', 'py-4', 'text-center', 'text-sm', 'text-red-500');
        errorCell.textContent = 'Error loading data. Please try again later.';
        errorRow.appendChild(errorCell);
        tbody.appendChild(errorRow);
    }
}

// Initial data load - this will be called from HTML with the headers length
// fetchData(document.querySelectorAll('#data-table thead th').length);

// Set up refresh button
document.addEventListener('DOMContentLoaded', function () {
    // Call fetchData after the DOM is loaded, passing the number of headers
    const headersCount = document.querySelectorAll('#data-table thead th').length;
    fetchData(headersCount);

    document.getElementById('refresh-btn').addEventListener('click', function () {
        fetchData(headersCount);
    });
});