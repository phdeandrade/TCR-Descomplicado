import math
from functools import reduce

def resolver_sistema_tcr(dados):
    """Recebe o JSON do frontend e processa as equações separando rigidamente Verificação e Simplificação."""
    equacoes = dados.get('equacoes', [])
    if not equacoes:
        return {"status": "erro", "mensagem": "Nenhuma equação recebida."}

    # ==============================
    # PASSO 1: VERIFICAÇÃO DA SOLUÇÃO
    # ==============================
    passos_verificacao = []
    modulos_originais = []
    
    for eq in equacoes:
        modulos_originais.append(eq.get('n', 1))
        
    passos_verificacao.append("Para o Teorema Chinês dos Restos (TCR) ser aplicado, os módulos do sistema devem ser coprimos aos pares ($\\text{mdc} = 1$).<br>")
    
    # 1.1 Verificando se os módulos originais são coprimos
    coprimos_ok = True
    for i in range(len(modulos_originais)):
        for j in range(i + 1, len(modulos_originais)):
            mdc_par = math.gcd(modulos_originais[i], modulos_originais[j])
            if mdc_par != 1:
                passos_verificacao.append(f"&bull; $\\text{{mdc}}({modulos_originais[i]}, {modulos_originais[j]}) = {mdc_par}$ &larr; <strong style='color: var(--danger-color);'>Falhou!</strong>")
                coprimos_ok = False
            else:
                passos_verificacao.append(f"&bull; $\\text{{mdc}}({modulos_originais[i]}, {modulos_originais[j]}) = 1$")
                
    if not coprimos_ok:
        passos_verificacao.append("<br><strong style='color: var(--danger-color);'>Conclusão:</strong> Como há módulos que não são coprimos entre si, <strong>o Teorema Chinês dos Restos não pode ser aplicado.</strong>")
        str_verificacao = "<br>".join(passos_verificacao)
        explicacao = f"<div class='step'><div class='step-title'>Passo 1: Verificação da solução</div><p>{str_verificacao}</p></div>"
        return {"status": "sucesso", "mensagem": explicacao}

    # 1.2 Verificando se cada equação individual possui solução inteira
    passos_verificacao.append("<br><strong>Verificação de existência de solução nas equações:</strong>")
    equacoes_ok = True
    
    for i, eq in enumerate(equacoes, start=1):
        a = eq.get('a', 1)
        b = eq.get('b', 0)
        c = eq.get('c', 0)
        n = eq.get('n', 1)
        
        C = (c - b) % n
        a_mod = a % n
        d = math.gcd(a_mod, n)
        
        if C % d != 0:
            passos_verificacao.append(f"&bull; Equação {i}: $\\text{{mdc}}({a_mod}, {n}) = {d}$. Como {d} não divide {(c - b) % n}, <strong style='color: var(--danger-color);'>não tem solução!</strong>")
            equacoes_ok = False
        else:
            passos_verificacao.append(f"&bull; Equação {i}: $\\text{{mdc}}({a_mod}, {n}) = {d}$, que divide {(c - b) % n}. OK!")

    if not equacoes_ok:
        passos_verificacao.append("<br><strong style='color: var(--danger-color);'>Conclusão:</strong> Pelo menos uma equação não possui solução. O sistema não pode ser resolvido.")
        str_verificacao = "<br>".join(passos_verificacao)
        explicacao = f"<div class='step'><div class='step-title'>Passo 1: Verificação da solução</div><p>{str_verificacao}</p></div>"
        return {"status": "sucesso", "mensagem": explicacao}

    passos_verificacao.append("<br><strong>Conclusão:</strong> O sistema é válido e pode ser resolvido!")

    # ==============================
    # PASSO 2: SIMPLIFICAÇÃO DAS EQUAÇÕES
    # ==============================
    passos_simplificacao = []
    restos = []
    modulos = []
    
    for i, eq in enumerate(equacoes, start=1):
        a = eq.get('a', 1)
        b = eq.get('b', 0)
        c = eq.get('c', 0)
        n = eq.get('n', 1)
        
        C = (c - b) % n
        a_mod = a % n
        d = math.gcd(a_mod, n)
        
        a_simp = a_mod // d
        C_simp = C // d
        n_simp = n // d
        
        sinal_b = f"+ {b}" if b > 0 else (f"- {abs(b)}" if b < 0 else "")
        eq_original = f"{a}x {sinal_b} \\equiv {c} \\pmod{{{n}}}"
        
        texto_simp = f"<strong>Equação {i}:</strong> ${eq_original}$<br>"
        if b != 0:
            texto_simp += f"Isolando $x$: ${a_mod}x \\equiv {C} \\pmod{{{n}}}$<br>"

        if a_simp == 1:
            novo_resto = C_simp % n_simp
            texto_simp += f"Formato canônico: <strong>$x \\equiv {novo_resto} \\pmod{{{n_simp}}}$</strong><br>"
        else:
            inverso_a = pow(a_simp, -1, n_simp)
            novo_resto = (C_simp * inverso_a) % n_simp
            
            if d != 1:
                texto_simp += f"Dividindo todos os termos pelo mdc ({d}):<br>${a_simp}x \\equiv {C_simp} \\pmod{{{n_simp}}}$<br>"
                
            texto_simp += f"Multiplicando pelo inverso de {a_simp} (que é {inverso_a}):<br>"
            texto_simp += f"<strong>$x \\equiv {novo_resto} \\pmod{{{n_simp}}}$</strong><br>"
            
        passos_simplificacao.append(texto_simp)
        restos.append(novo_resto)
        modulos.append(n_simp)

    # ==============================
    # PASSO 3: CALCULAR M E n_k
    # ==============================
    M = reduce(lambda x, y: x * y, modulos)
    str_modulos = " \\cdot ".join(map(str, modulos))
    
    passos_M = []
    passos_M.append(f"<strong>Módulo Global ($M$):</strong>")
    passos_M.append(f"$M = {str_modulos} = {M}$<br>")
    passos_M.append(f"<strong>Módulos Parciais ($n_k = M / m_k$):</strong>")

    # ==============================
    # PASSO 4 e 5: INVERSOS E FÓRMULA FINAL
    # ==============================
    passos_inversos = []
    x_final = 0
    soma_str = []
    formula_generica_str = []
    
    for k, (ak, mk) in enumerate(zip(restos, modulos), start=1):
        nk = M // mk
        dk = pow(nk, -1, mk)
        parcela = ak * nk * dk
        x_final += parcela
        
        soma_str.append(f"({ak} \\cdot {nk} \\cdot {dk})")
        formula_generica_str.append(f"(a_{{{k}}} \\cdot n_{{{k}}} \\cdot d_{{{k}}})")
        
        passos_M.append(f"&bull; <strong>Equação {k}:</strong> $n_{{{k}}} = \\frac{{{M}}}{{{mk}}} = {nk}$")
        
        # A tag HTML de negrito foi removida de dentro do $ para evitar que o MathJax quebre
        passos_inversos.append(
            f"&bull; <strong>Equação {k}:</strong> $n_{{{k}}} \\cdot d_{{{k}}} \\equiv 1 \\pmod{{{mk}}} "
            f"\\implies {nk} \\cdot d_{{{k}}} \\equiv 1 \\pmod{{{mk}}} \\implies d_{{{k}}} = {dk}$"
        )

    passos_final = []
    str_formula_generica = " + ".join(formula_generica_str)
    passos_final.append(f"$x \\equiv {str_formula_generica} \\pmod{{M}}$")
    passos_final.append(f"$x \\equiv {str(' + '.join(soma_str))} \\pmod{{{M}}}$")
    passos_final.append(f"<strong>$x \\equiv {x_final % M} \\pmod{{{M}}}$</strong>")

    # ==============================
    # CONSTRUÇÃO DAS 5 DIVS EM HTML (SUCESSO TOTAL)
    # ==============================
    str_verificacao = "<br>".join(passos_verificacao)
    str_simplificacao = "<br>".join(passos_simplificacao)
    str_M = "<br>".join(passos_M)
    str_inversos = "<br>".join(passos_inversos)
    str_final = "<br>".join(passos_final)

    explicacao = (
        "<div class='step'>"
        "<div class='step-title'>Passo 1: Verificação da solução</div>"
        f"<p>{str_verificacao}</p>"
        "</div>"
        
        "<div class='step'>"
        "<div class='step-title'>Passo 2: Simplificação das equações</div>"
        f"<p>{str_simplificacao}</p>"
        "</div>"
        
        "<div class='step'>"
        "<div class='step-title'>Passo 3: Calcular M e n<sub>k</sub></div>"
        f"<p>{str_M}</p>"
        "</div>"
        
        "<div class='step'>"
        "<div class='step-title'>Passo 4: Calcular inversos</div>"
        f"<p>{str_inversos}</p>"
        "</div>"

        "<div class='step'>"
        "<div class='step-title'>Passo 5: Aplicar na fórmula final</div>"
        f"<p>{str_final}</p>"
        "</div>"
    )

    return {"status": "sucesso", "mensagem": explicacao}