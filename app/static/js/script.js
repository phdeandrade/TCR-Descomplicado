/**
 * Índice do passo da resolução atualmente visível na tela (inicia em 0).
 * @type {number}
 */
let passoAtual = 0;

/**
 * Armazena as referências de todos os elementos HTML correspondentes aos passos da resolução.
 * @type {HTMLElement[]}
 */
let todosOsPassos = [];

/**
 * Define se a interface está atualmente exibindo o resumo final (todos os passos de uma vez).
 * @type {boolean}
 */
let modoResumo = false;

/**
 * Inicializa a aplicação configurando o tema visual baseado no cache do navegador
 * e configura os atalhos de teclado ('Enter' para calcular e setinhas para navegar).
 */
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

    document.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            generateSteps();
        }
    });

    document.addEventListener('keydown', function(e) {
        const solutionContainer = document.getElementById('solution-container');
        const containerVisivel = solutionContainer && solutionContainer.style.display === 'block';
        
        if (!containerVisivel || modoResumo) return;

        if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
            e.preventDefault();
            avancarOuResumir();
        } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
            e.preventDefault();
            if (passoAtual > 0) {
                irParaPasso(passoAtual - 1);
            }
        }
    });
});

/**
 * Alterna o tema da aplicação entre claro e escuro.
 */
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

/**
 * Adiciona uma nova linha de input de equação na interface gráfica.
 * Possui um limite máximo estrito de 5 equações para manter a performance e coerência visual.
 */
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

/**
 * Remove uma linha de equação específica da interface, impedindo que o sistema tenha menos de duas equações.
 * @param {HTMLElement} btnElement - A referência do botão de exclusão que foi clicado.
 */
function removeEquation(btnElement) {
    const list = document.getElementById('equations-list');
    const rows = list.querySelectorAll('.equation-row');
    if (rows.length > 2) {
        btnElement.parentElement.remove();
    } else {
        mostrarErro("O sistema precisa ter no mínimo duas equações.");
    }
}

/**
 * Processa a string de uma equação algébrica, validando sua estrutura e extraindo seus coeficientes.
 * @param {string} eqStr - A equação digitada pelo usuário (ex: "2x - 3" ou "-x").
 * @returns {Object|null} Retorna os coeficientes estruturados {a: numero, b: numero} ou null se o formato for inválido.
 */
function parseEquationString(eqStr) {
    const cleanStr = eqStr.replace(/\s+/g, '');
    
    const formatoValido = /^[+-]?\d*x([+-]\d+)?$/.test(cleanStr);
    if (!formatoValido) {
        return null; 
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

/**
 * Captura, valida e organiza todos os dados dos campos do formulário de equações.
 * @returns {Object|null} Retorna os dados estruturados contendo o array de equações ou null em caso de falha de validação.
 */
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

        if (!/^-?\d+$/.test(cInput)) {
            mostrarErro(`O valor após a igualdade ("${cInput}") não é um formato de número válido.`);
            return null;
        }
        const cValor = parseInt(cInput, 10);
        
        const parsedEq = parseEquationString(eqInput);
        if (!parsedEq) {
            mostrarErro(`A equação "${eqInput}" está num formato inválido. Use formatos como "2x + 1" ou "x - 3".`);
            return null;
        }

        if (parsedEq.a % nValor === 0) {
            mostrarErro(`O coeficiente de x não pode ser múltiplo do módulo (na equação "${eqInput}"). Isso anula a variável x!`);
            return null;
        }
        
        equacoesParaBackend.push({
            "a": parsedEq.a,             
            "b": parsedEq.b,             
            "c": cValor,                 
            "n": nValor                  
        });
    }
    
    return { "equacoes": equacoesParaBackend };
}

/**
 * Organiza a comunicação com a API do servidor, enviando os dados das equações e montando a interface de resolução.
 */
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

/**
 * Cria e exibe um alerta temporário de erro visual para o usuário.
 * @param {string} mensagem - O texto descritivo do erro a ser exibido.
 */
function mostrarErro(mensagem) {
    const container = document.getElementById('mensagem-erro');
    if (!container) return;

    container.innerHTML = '';

    container.innerHTML = `<div class="erro-inline">⚠️ ${mensagem}</div>`;
    const div = container.querySelector('.erro-inline');

    setTimeout(() => {
        div.classList.add('sumindo');
        
        setTimeout(() => { container.innerHTML = ''; }, 400);
    }, 4000);
}

/**
 * Configura o estado inicial da interface gráfica para iniciar a exibição fragmentada dos passos matemáticos.
 */
function iniciarNavegacao() {
    todosOsPassos = Array.from(document.querySelectorAll('#solution-container .step'));
    passoAtual = 0;
    modoResumo = false;

    todosOsPassos.forEach(passo => passo.style.display = 'none');

    irParaPasso(0);
}

/**
 * Oculta todos os passos em andamento e exibe o passo desejado.
 * @param {number} indice - O índice do passo que deve ser focado na interface.
 */
function irParaPasso(indice) {
    modoResumo = false;

    todosOsPassos.forEach(passo => passo.style.display = 'none');

    passoAtual = indice;

    const passoVisivel = todosOsPassos[passoAtual];
    passoVisivel.style.display = 'block';
    passoVisivel.style.animation = 'none';
    passoVisivel.offsetHeight; 
    passoVisivel.style.animation = 'fadeIn 0.4s ease';

    atualizarControles();

    if (window.MathJax) {
        MathJax.typesetPromise([passoVisivel]);
    }
}

/**
 * Sincroniza o estado (ativo, inativo, texto) dos botões da barra de navegação com base no fluxo atual da aplicação.
 */
function atualizarControles() {
    const barra = document.getElementById('barra-navegacao');
    if (!barra) return;
    
    barra.style.display = 'flex';

    const btnAnterior = document.getElementById('btn-anterior');
    const btnProximo  = document.getElementById('btn-proximo');
    const contador    = document.getElementById('contador-passos');
    const total       = todosOsPassos.length;

    if (modoResumo) {
        btnAnterior.disabled = false;
        btnAnterior.onclick = () => irParaPasso(total - 1);
        btnAnterior.innerHTML = '← Voltar aos passos';
        
        contador.textContent = `Resumo Completo`;
        
        btnProximo.style.display = 'none';
    } else {
        btnAnterior.disabled = passoAtual === 0;
        btnAnterior.onclick = () => irParaPasso(passoAtual - 1);
        btnAnterior.innerHTML = '← Anterior';
        
        contador.textContent = `Passo ${passoAtual + 1} de ${total}`;
        
        btnProximo.style.display = 'inline-block';
        
        if (passoAtual === total - 1) {
            btnProximo.innerHTML = 'Ver Resumo →';
        } else {
            btnProximo.innerHTML = 'Próximo →';
        }
    }
}

/**
 * Renderiza dinamicamente a barra com os botões controladores do fluxo de navegação do passo a passo.
 */
function criarBarraNavegacao() {
    const barraExistente = document.getElementById('barra-navegacao');
    if (barraExistente) barraExistente.remove();

    const barra = document.createElement('div');
    barra.id = 'barra-navegacao';
    barra.innerHTML = `
        <button id="btn-anterior" onclick="irParaPasso(passoAtual - 1)">← Anterior</button>
        <span id="contador-passos"></span>
        <button id="btn-proximo" onclick="avancarOuResumir()">Próximo →</button>
    `;

    const h2 = document.querySelector('#solution-container h2');
    h2.insertAdjacentElement('afterend', barra);
}

/**
 * Analisa a progressão atual do usuário, ou seja, avança um único passo ou engatilha a visão completa (modo resumo) do cálculo.
 */
function avancarOuResumir() {
    if (passoAtual < todosOsPassos.length - 1) {
        irParaPasso(passoAtual + 1);
        return;
    }

    modoResumo = true;

    todosOsPassos.forEach(passo => {
        passo.style.display = 'block';
        passo.style.animation = 'none';
        passo.offsetHeight; 
        passo.style.animation = 'fadeIn 0.4s ease';
    });

    if (window.MathJax) {
        MathJax.typesetPromise([document.getElementById('solution-container')]);
    }

    atualizarControles();
}

/**
 * Copia o resultado para a área de transferência do usuário.
 * @param {string} texto - A string com a resposta.
 */
function copiarResultado(texto) {
    navigator.clipboard.writeText(texto)
        .then(() => {
            const btn = document.getElementById('btn-copiar');
            if (btn) {
                const textoOriginal = btn.innerHTML;
                
                btn.innerHTML = '✅ Copiado!';
                btn.style.opacity = '0.8';
                
                setTimeout(() => {
                    btn.innerHTML = textoOriginal;
                    btn.style.opacity = '1';
                }, 2000);
            }
        })
        .catch(e => {
            console.log(e);
            mostrarErro("Erro ao copiar a resposta.");
        });
}