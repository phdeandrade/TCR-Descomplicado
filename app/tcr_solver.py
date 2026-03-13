import math
from functools import reduce


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def montar_step(titulo, conteudo):
    """Gera o HTML de um bloco 'step' com título e conteúdo."""
    return (
        f"<div class='step'>"
        f"<div class='step-title'>{titulo}</div>"
        f"<p>{conteudo}</p>"
        f"</div>"
    )


def unir(linhas):
    """Junta uma lista de strings com <br> para exibição HTML."""
    return "<br>".join(linhas)


def formatar_sinal(b):
    """Formata o termo independente b com seu sinal para uso em strings LaTeX."""
    if b > 0:
        return f"+ {b}"
    if b < 0:
        return f"- {abs(b)}"
    return ""


def erro_precoce(titulo, linhas):
    """Retorna um resultado de sucesso parcial (erro matemático detectado)."""
    return {"status": "sucesso", "mensagem": montar_step(titulo, unir(linhas))}


# ============================================================
# FUNÇÕES DE CADA PASSO
# ============================================================

def passo1_verificacao(equacoes):
    """
    PASSO 1: VERIFICAÇÃO DA SOLUÇÃO
    Checa se os módulos são coprimos e se cada equação tem solução inteira.
    Retorna (linhas_html, equacoes_ok) ou interrompe cedo com erro_precoce.
    """
    modulos = [eq.get('n', 1) for eq in equacoes]
    linhas = [
        "Para o Teorema Chinês dos Restos (TCR) ser aplicado, os módulos do sistema "
        "devem ser coprimos aos pares ($\\text{mdc} = 1$).<br>"
    ]

    # 1.1 Verificando se os módulos originais são coprimos
    coprimos_validos = True
    for i in range(len(modulos)):
        for j in range(i + 1, len(modulos)):
            mdc_par = math.gcd(modulos[i], modulos[j])
            if mdc_par != 1:
                linhas.append(
                    f"&bull; $\\text{{mdc}}({modulos[i]}, {modulos[j]}) = {mdc_par}$"
                    f" &larr; <strong style='color: var(--danger-color);'>Falhou!</strong>"
                )
                coprimos_validos = False
            else:
                linhas.append(f"&bull; $\\text{{mdc}}({modulos[i]}, {modulos[j]}) = 1$")

    if not coprimos_validos:
        linhas.append(
            "<br><strong style='color: var(--danger-color);'>Conclusão:</strong> "
            "Como há módulos que não são coprimos entre si, "
            "<strong>o Teorema Chinês dos Restos não pode ser aplicado.</strong>"
        )
        return erro_precoce("Passo 1: Verificação da solução", linhas)

    # 1.2 Verificando se cada equação individual possui solução inteira
    linhas.append("<br><strong>Verificação de existência de solução nas equações:</strong>")
    equacoes_validas = True

    for i, eq in enumerate(equacoes, start=1):
        a, b, c, n = eq.get('a', 1), eq.get('b', 0), eq.get('c', 0), eq.get('n', 1)
        C = (c - b) % n
        a_mod = a % n
        d = math.gcd(a_mod, n)

        if C % d != 0:
            linhas.append(
                f"&bull; Equação {i}: $\\text{{mdc}}({a_mod}, {n}) = {d}$. "
                f"Como {d} não divide {C}, "
                f"<strong style='color: var(--danger-color);'>não tem solução!</strong>"
            )
            equacoes_validas = False
        else:
            linhas.append(
                f"&bull; Equação {i}: $\\text{{mdc}}({a_mod}, {n}) = {d}$, "
                f"que divide {C}. OK!"
            )

    if not equacoes_validas:
        linhas.append(
            "<br><strong style='color: var(--danger-color);'>Conclusão:</strong> "
            "Pelo menos uma equação não possui solução. O sistema não pode ser resolvido."
        )
        return erro_precoce("Passo 1: Verificação da solução", linhas)

    linhas.append("<br><strong>Conclusão:</strong> O sistema é válido e pode ser resolvido!")
    return linhas


def passo2_simplificacao(equacoes):
    """
    PASSO 2: SIMPLIFICAÇÃO DAS EQUAÇÕES
    Reduz cada equação ao formato canônico x ≡ r (mod m).
    Retorna (linhas_html, restos[], modulos[]).
    """
    linhas = []
    restos = []
    modulos = []

    for i, eq in enumerate(equacoes, start=1):
        a, b, c, n = eq.get('a', 1), eq.get('b', 0), eq.get('c', 0), eq.get('n', 1)

        C = (c - b) % n
        a_mod = a % n
        d = math.gcd(a_mod, n)
        a_simp = a_mod // d
        C_simp = C // d
        n_simp = n // d

        eq_original = f"{a}x {formatar_sinal(b)} \\equiv {c} \\pmod{{{n}}}"
        texto = f"<strong>Equação {i}:</strong> ${eq_original}$<br>"

        if b != 0:
            texto += f"Isolando $x$: ${a_mod}x \\equiv {C} \\pmod{{{n}}}$<br>"

        if a_simp == 1:
            # Coeficiente de x já é 1 — sem necessidade de inverso
            novo_resto = C_simp % n_simp
            texto += f"Formato canônico: <strong>$x \\equiv {novo_resto} \\pmod{{{n_simp}}}$</strong><br>"
        else:
            # Calcula o inverso modular de a_simp
            inverso_a  = pow(a_simp, -1, n_simp)
            novo_resto = (C_simp * inverso_a) % n_simp

            if d != 1:
                texto += (
                    f"Dividindo todos os termos pelo mdc ({d}):<br>"
                    f"${a_simp}x \\equiv {C_simp} \\pmod{{{n_simp}}}$<br>"
                )

            texto += (
                f"Multiplicando pelo inverso de {a_simp} (que é {inverso_a}):<br>"
                f"<strong>$x \\equiv {novo_resto} \\pmod{{{n_simp}}}$</strong><br>"
            )

        linhas.append(texto)
        restos.append(novo_resto)
        modulos.append(n_simp)

    return linhas, restos, modulos


def passos3_4_5_tcr(restos, modulos):
    """
    PASSOS 3, 4 e 5: CÁLCULO DO TCR
    Calcula M, os módulos parciais, os inversos e aplica a fórmula final.
    Retorna (linhas_p3, linhas_p4, linhas_p5).
    """
    M = reduce(lambda x, y: x * y, modulos)

    # Passo 3: Módulo global e módulos parciais
    modulos_latex = " \\cdot ".join(map(str, modulos))
    linhas_p3 = [
        f"<strong>Módulo Global ($M$):</strong>",
        f"$M = {modulos_latex} = {M}$<br>",
        f"<strong>Módulos Parciais ($n_k = M / m_k$):</strong>",
    ]

    # Passos 4 e 5: Inversos modulares e montagem da fórmula
    linhas_p4 = []
    termos_soma = []
    termos_formula = []
    x_acumulado = 0

    for k, (ak, mk) in enumerate(zip(restos, modulos), start=1):
        nk = M // mk
        dk = pow(nk, -1, mk)
        x_acumulado += ak * nk * dk

        linhas_p3.append(f"&bull; <strong>Equação {k}:</strong> $n_{{{k}}} = \\frac{{{M}}}{{{mk}}} = {nk}$")

        # A tag HTML de negrito foi removida de dentro do $ para evitar que o MathJax quebre
        linhas_p4.append(
            f"&bull; <strong>Equação {k}:</strong> "
            f"$n_{{{k}}} \\cdot d_{{{k}}} \\equiv 1 \\pmod{{{mk}}} "
            f"\\implies {nk} \\cdot d_{{{k}}} \\equiv 1 \\pmod{{{mk}}} "
            f"\\implies d_{{{k}}} = {dk}$"
        )

        termos_soma.append(f"({ak} \\cdot {nk} \\cdot {dk})")
        termos_formula.append(f"(a_{{{k}}} \\cdot n_{{{k}}} \\cdot d_{{{k}}})")

    linhas_p5 = [
        f"$x \\equiv {' + '.join(termos_formula)} \\pmod{{M}}$",
        f"$x \\equiv {' + '.join(termos_soma)} \\pmod{{{M}}}$",
        f"<strong>$x \\equiv {x_acumulado % M} \\pmod{{{M}}}$</strong>",
    ]

    return linhas_p3, linhas_p4, linhas_p5


# ============================================================
# FUNÇÃO PRINCIPAL
# ============================================================

def resolver_sistema_tcr(dados):
    """Recebe o JSON do frontend e processa as equações separando rigidamente Verificação e Simplificação."""
    equacoes = dados.get('equacoes', [])
    if not equacoes:
        return {"status": "erro", "mensagem": "Nenhuma equação recebida."}

    # ==============================
    # PASSO 1: VERIFICAÇÃO DA SOLUÇÃO
    # ==============================
    resultado_verificacao = passo1_verificacao(equacoes)

    # Se retornou um dict, houve erro e a função já encerrou cedo
    if isinstance(resultado_verificacao, dict):
        return resultado_verificacao

    linhas_p1 = resultado_verificacao

    # ==============================
    # PASSO 2: SIMPLIFICAÇÃO DAS EQUAÇÕES
    # ==============================
    linhas_p2, restos, modulos = passo2_simplificacao(equacoes)

    # ==============================
    # PASSOS 3, 4 e 5: CALCULAR M, INVERSOS E FÓRMULA FINAL
    # ==============================
    linhas_p3, linhas_p4, linhas_p5 = passos3_4_5_tcr(restos, modulos)

    # ==============================
    # CONSTRUÇÃO DAS 5 DIVS EM HTML (SUCESSO TOTAL)
    # ==============================
    explicacao = "".join([
        montar_step("Passo 1: Verificação da solução", unir(linhas_p1)),
        montar_step("Passo 2: Simplificação das equações", unir(linhas_p2)),
        montar_step("Passo 3: Calcular M e n<sub>k</sub>", unir(linhas_p3)),
        montar_step("Passo 4: Calcular inversos", unir(linhas_p4)),
        montar_step("Passo 5: Aplicar na fórmula final", unir(linhas_p5)),
    ])

    return {"status": "sucesso", "mensagem": explicacao}