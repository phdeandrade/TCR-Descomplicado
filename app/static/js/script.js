document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    if (savedTheme === 'dark') {
        document.body.setAttribute('data-theme', 'dark');
    } else {
        document.body.removeAttribute('data-theme');
    }
});

function toggleTheme() {
    const body = document.body;
    if (body.getAttribute('data-theme') === 'dark') {
        body.removeAttribute('data-theme');
        localStorage.setItem('theme', 'light');
    } else {
        body.setAttribute('data-theme', 'dark');
        localStorage.setItem('theme', 'dark');
    }
}

function toggleOperation(selectEl) {
    const inputEl = selectEl.nextElementSibling;
    if (selectEl.value === 'none') {
        inputEl.style.display = 'none';
    } else {
        inputEl.style.display = 'inline-block';
    }
}

function addEquation() {
    const list = document.getElementById('equations-list');
    if (!list) return;
    
    const newRow = document.createElement('div');
    newRow.className = 'equation-row';
    newRow.innerHTML = `
        <input type="number"> x 
        <select onchange="toggleOperation(this)">
            <option value="none" selected></option>
            <option value="-">-</option>
            <option value="+">+</option>
        </select>
        <input type="number" class="op-val" style="display: none;">
        &equiv; <input type="number"> (mod <input type="number">)
        <button class="btn-remove" onclick="removeEquation(this)">✖</button>
    `;
    list.appendChild(newRow);
}

function removeEquation(btnElement) {
    const list = document.getElementById('equations-list');
    const rows = list.querySelectorAll('.equation-row');
    if (rows.length > 2) {
        btnElement.parentElement.remove();
    } else {
        alert("O sistema precisa ter no mínimo duas equações.");
    }
}

function generateSteps() {
    const solution = document.getElementById('solution-container');
    if (solution) {
        solution.style.display = 'block';
    }
}