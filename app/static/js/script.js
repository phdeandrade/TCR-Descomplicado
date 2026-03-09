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

function addEquation() {
    const equationsList = document.getElementById('equations-list');
    const newRow = document.createElement('div');
    newRow.className = 'equation-row';
    
    newRow.innerHTML = `
        <input type="text" class="eq-input" placeholder="Ex: 2x + 1">
        ≡ <input type="text" class="num-input" inputmode="numeric" oninput="this.value = this.value.replace(/[^0-9]/g, '')"> 
        (mod <input type="text" class="num-input" inputmode="numeric" oninput="this.value = this.value.replace(/[^0-9]/g, '')">)
        <button class="btn-remove" onclick="removeEquation(this)">✖</button>
    `;
    
    equationsList.appendChild(newRow);
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