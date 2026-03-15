// Índice do passo atualmente visível (começa no primeiro)
let passoAtual = 0;

// Lista de todos os elementos .step encontrados no DOM
let todosOsPassos = [];

document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    const themeBtn = document.querySelector('.theme-toggle');

    if (savedTheme === 'dark') {
        document.body.setAttribute('data-theme', 'dark');
        if (themeBtn) themeBtn.textContent = '☀️';
    } else {
        document.body.removeAttribute('data-theme');
        if (themeBtn) themeBtn.textContent = '🌙';
    }
});

function toggleTheme() {
    const body = document.body;
    const themeBtn = document.querySelector('.theme-toggle');

    if (body.getAttribute('data-theme') === 'dark') {
        body.removeAttribute('data-theme');
        localStorage.setItem('theme', 'light');
        if (themeBtn) themeBtn.textContent = '🌙';
    } else {
        body.setAttribute('data-theme', 'dark');
        localStorage.setItem('theme', 'dark');
        if (themeBtn) themeBtn.textContent = '☀️';
    }
}

function addEquation() {
    const equationsList = document.getElementById('equations-list');
    
    const currentEquations = equationsList.querySelectorAll('.equation-row').length;
    
    if (currentEquations >= 5) {
        mostrarErro("O sistema permite adicionar no máximo 5 equações.");
        return;
    }

    const newRow = document.createElement('div');
    newRow.className = 'equation-row';
    
    newRow.innerHTML = `
        <input type="text" class="eq-input" placeholder="Ex: 2x + 1">
        ≡ <input type="text" class="num-input" inputmode="numeric" oninput="this.value = this.value.replace(/[^0-9-]/g, '')"> 
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
        mostrarErro("O sistema precisa ter no mínimo duas equações.");
    }
}

function parseEquationString(eqStr) {
    const cleanStr = eqStr.replace(/\s+/g, '');
    
    // Valida o formato completo antes de qualquer coisa.
    // Aceita apenas: [sinal] [dígitos] x [sinal dígitos]
    // Exemplos válidos: x, 2x, -x, x+3, 2x-1, -3x+5
    const formatoValido = /^[+-]?\d*x([+-]\d+)?$/.test(cleanStr);
    if (!formatoValido) {
        return null; // Rejeita "x-23NK", "xabc", "2x+3y", etc.
    }

    const xMatch = cleanStr.match(/(^|[+-])(\d*)x/);
    
    if (!xMatch) {
        return null; 
    }
    
    const sign = xMatch[1] === '-' ? -1 : 1;
    const coef = xMatch[2] === '' ? 1 : parseInt(xMatch[2], 10);
    const a = sign * coef;
    
    const noXStr = cleanStr.replace(/(^|[+-])\d*x/, '');
    
    let b = 0;
    if (noXStr !== '') {
        b = parseInt(noXStr, 10);
        if (isNaN(b)) return null;
    }
    
    return { a: a, b: b };
}

function collectEquationsData() {
    const rows = document.querySelectorAll('.equation-row'); 
    const equacoesParaBackend = [];
    
    for (let row of rows) {
        const eqInput = row.querySelector('.eq-input').value; 
        const numInputs = row.querySelectorAll('.num-input'); 
        const cInput = numInputs[0].value; 
        const nInput = numInputs[1].value; 
        
        if (!eqInput || !cInput || !nInput) {
            mostrarErro("Por favor, preencha todos os campos antes de gerar o passo a passo.");
            return null; 
        }

        const nValor = parseInt(nInput, 10);
        if (nValor <= 1) {
            mostrarErro(`O módulo deve ser um número maior que 1 (você digitou mod ${nValor}).`);
            return null;
        }
        
        const parsedEq = parseEquationString(eqInput);
        if (!parsedEq) {
            mostrarErro(`A equação "${eqInput}" está num formato inválido. Use formatos como "2x + 1" ou "x - 3".`);
            return null;
        }
        
        equacoesParaBackend.push({
            "a": parsedEq.a,             // termo dependente de x
            "b": parsedEq.b,             // termo independente com sinal (0 se não houver)
            "c": parseInt(cInput, 10),   // resultado da congruência
            "n": parseInt(nInput, 10)    // módulo
        });
    }
    
    return { "equacoes": equacoesParaBackend };
}

async function generateSteps() {
    const dados = collectEquationsData();
    if (!dados) return; 

    const solutionContainer = document.getElementById('solution-container');
    
    solutionContainer.style.display = 'block';
    solutionContainer.innerHTML = '<h2>Resolução Passo a Passo</h2><p>Calculando a magia do TCR...</p>';

    try {
        const resposta = await fetch('/resolver', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dados)
        });

        const resultado = await resposta.json();

        if (resultado.status === "sucesso") {
            solutionContainer.innerHTML = '<h2>Resolução Passo a Passo</h2>' + resultado.mensagem;
            criarBarraNavegacao();
            iniciarNavegacao();
            
            if (window.MathJax) {
                MathJax.typesetPromise([solutionContainer]);
            }
        } else {
            solutionContainer.innerHTML = `<h2>Resolução Interrompida</h2>
                                           <p style="color: var(--danger-color); font-weight: bold;">${resultado.mensagem}</p>`;
        }

    } catch (erro) {
        console.error("Erro de conexão:", erro);
        solutionContainer.innerHTML = '<h2>Erro de Servidor</h2><p>Não foi possível conectar ao backend. Verifique se o Flask está rodando!</p>';
    }
}

function mostrarErro(mensagem) {
    const container = document.getElementById('mensagem-erro');
    if (!container) return;

    // Garante que qualquer erro anterior seja cancelado antes de mostrar o novo
    container.innerHTML = '';

    container.innerHTML = `<div class="erro-inline">⚠️ ${mensagem}</div>`;
    const div = container.querySelector('.erro-inline');

    setTimeout(() => {
        // Dispara a animação de saída
        div.classList.add('sumindo');
        
        // Remove do DOM só depois que a animação de saída terminar (400ms)
        setTimeout(() => { container.innerHTML = ''; }, 400);
    }, 4000);
}

function iniciarNavegacao() {
    // Captura todos os .step que o backend acabou de inserir no DOM
    todosOsPassos = Array.from(document.querySelectorAll('#solution-container .step'));
    passoAtual = 0;

    // Esconde todos os passos inicialmente
    todosOsPassos.forEach(passo => passo.style.display = 'none');

    // Mostra o primeiro
    irParaPasso(0);
}

function irParaPasso(indice) {
    // Esconde o passo anterior (se existir)
    if (todosOsPassos[passoAtual]) {
        todosOsPassos[passoAtual].style.display = 'none';
    }

    passoAtual = indice;

    // Mostra o passo atual com animação (a classe fadeIn já existe no seu CSS)
    const passoVisivel = todosOsPassos[passoAtual];
    passoVisivel.style.display = 'block';
    passoVisivel.style.animation = 'none';
    // Força o reflow para reiniciar a animação — truque necessário para o CSS reanimar
    passoVisivel.offsetHeight;
    passoVisivel.style.animation = 'fadeIn 0.4s ease';

    // Atualiza os botões e o contador depois de mudar o passo
    atualizarControles();

    // Re-renderiza o MathJax apenas no passo atual (muito mais rápido que re-renderizar tudo)
    if (window.MathJax) {
        MathJax.typesetPromise([passoVisivel]);
    }
}

function atualizarControles() {
    const btnAnterior = document.getElementById('btn-anterior');
    const btnProximo  = document.getElementById('btn-proximo');
    const contador    = document.getElementById('contador-passos');
    const total       = todosOsPassos.length;

    // O botão "Anterior" só faz sentido a partir do segundo passo
    btnAnterior.disabled = passoAtual === 0;

    // Atualiza o contador "Passo 2 de 5"
    contador.textContent = `Passo ${passoAtual + 1} de ${total}`;
}

function criarBarraNavegacao() {
    // Evita duplicar a barra se o usuário gerar uma segunda resolução
    const barraExistente = document.getElementById('barra-navegacao');
    if (barraExistente) barraExistente.remove();

    const barra = document.createElement('div');
    barra.id = 'barra-navegacao';
    barra.innerHTML = `
        <button id="btn-anterior" onclick="irParaPasso(passoAtual - 1)">← Anterior</button>
        <span id="contador-passos"></span>
        <button id="btn-proximo" onclick="avancarOuResumir()">Próximo →</button>
    `;

    // Insere a barra logo após o h2 "Resolução Passo a Passo"
    const h2 = document.querySelector('#solution-container h2');
    h2.insertAdjacentElement('afterend', barra);
}

function avancarOuResumir() {
    // Se não é o último passo, navega normalmente
    if (passoAtual < todosOsPassos.length - 1) {
        irParaPasso(passoAtual + 1);
        return;
    }

    // Se é o último passo, entra no modo resumo: mostra todos os passos de uma vez
    todosOsPassos.forEach(passo => {
        passo.style.display = 'block';
        // Reinicia a animação em cada passo para um efeito cascata suave
        passo.style.animation = 'none';
        passo.offsetHeight; // força reflow
        passo.style.animation = 'fadeIn 0.4s ease';
    });

    // Re-renderiza o MathJax em todo o container, já que agora tudo está visível
    if (window.MathJax) {
        MathJax.typesetPromise([document.getElementById('solution-container')]);
    }

    // Esconde a barra de navegação — ela não faz mais sentido no modo resumo
    document.getElementById('barra-navegacao').style.display = 'none';
}