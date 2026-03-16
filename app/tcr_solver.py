"""
Módulo de motor matemático para o Teorema Chinês dos Restos (TCR).
Contém a lógica isolada de cada passo da resolução.
"""

from app.utils import montar_step, unir, formatar_sinal, erro_precoce
import math
from functools import reduce

def passo1_simplificacao(equacoes):
    """
    Simplifica as equações lineares e reduz cada uma ao formato canônico x ≡ r (mod m).
    
    Verifica se existem erros matemáticos ou equações triviais (módulo <= 1 ou x anulado).
    Caso a equação seja válida, isola a variável, checa a viabilidade da solução 
    através do MDC e calcula o inverso modular, se necessário.

    Args:
        equacoes (list): Lista de dicionários, onde cada dicionário representa uma equação
                         com as chaves 'a' (coeficiente de x), 'b' (termo linear), 
                         'c' (resultado da congruência) e 'n' (módulo).

    Returns:
        tuple ou dict: Retorna uma tupla (linhas, restos, modulos) contendo o passo a passo
                       HTML formatado e as listas de restos e módulos simplificados se houver sucesso.
                       Retorna um dicionário (erro_precoce) se o sistema for matematicamente impossível.
    """
    linhas = []
    restos = []
    modulos = []

    for i, eq in enumerate(equacoes, start=1):
        a, b, c, n = eq.get('a', 1), eq.get('b', 0), eq.get('c', 0), eq.get('n', 1)

        if n <= 1:
            texto = f"<strong>Equação {i}:</strong> O módulo da equação deve ser estritamente maior que 1 (recebido mod {n}). <strong style='color: var(--danger-color);'>Sistema Inválido!</strong><br>"
            linhas.append(texto)
            return erro_precoce("Passo 1: Simplificação das equações", linhas)

        a_mod = a % n
        if a_mod == 0:
            eq_original = f"{a}x {formatar_sinal(b)} \\equiv {c} \\pmod{{{n}}}"
            texto = f"<strong>Equação {i}:</strong> ${eq_original}$<br>"
            texto += f"O coeficiente de $x$ é múltiplo do módulo ($\\equiv 0 \\pmod{{{n}}}$). Isso anula a variável $x$, tornando o sistema impossível de ser calculado pelo TCR.<br>"
            linhas.append(texto)
            return erro_precoce("Passo 1: Simplificação das equações", linhas)
        
        C = (c - b) % n
        d = math.gcd(a_mod, n)
        
        eq_original = f"{a}x {formatar_sinal(b)} \\equiv {c} \\pmod{{{n}}}"
        texto = f"<strong>Equação {i}:</strong> ${eq_original}$<br>"

        if b != 0:
            texto += f"Isolando $x$: ${a_mod}x \\equiv {C} \\pmod{{{n}}}$<br>"

        if C % d != 0:
            texto += f"$\\text{{mdc}}({a_mod}, {n}) = {d}$. Como {d} não divide {C}, <strong style='color: var(--danger-color);'>não tem solução!</strong><br>"
            linhas.append(texto)
            linhas.append("<br><strong style='color: var(--danger-color);'>Conclusão:</strong> Como uma das equações do sistema é impossível de ser resolvida, <strong>o sistema inteiro não possui solução.</strong>")
            return erro_precoce("Passo 1: Simplificação das equações", linhas)
        else:
            texto += f"$\\text{{mdc}}({a_mod}, {n}) = {d}$, que divide {C}. <strong style='color: var(--success-color);'>OK!</strong><br>"

        a_simp = a_mod // d
        C_simp = C // d
        n_simp = n // d

        if a_simp == 1:
            novo_resto = C_simp % n_simp
            texto += f"Formato canônico: <strong>$x \\equiv {novo_resto} \\pmod{{{n_simp}}}$</strong><br>"
        else:
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

    linhas.append("<br><strong style='color: var(--success-color);'>Conclusão:</strong> Todas as equações foram simplificadas e possuem solução individual!")
    return linhas, restos, modulos


def passo2_verificacao(modulos):
    """
    Verifica se a condição fundamental do TCR é atendida.
    
    Testa todos os pares possíveis de módulos simplificados para garantir 
    que são estritamente coprimos entre si (MDC igual a 1).

    Args:
        modulos (list): Lista de inteiros representando os módulos das equações já simplificadas.

    Returns:
        list ou dict: Retorna uma lista de strings (HTML) descrevendo o processo se todos 
                      forem coprimos. Retorna um dicionário (erro_precoce) caso falhe.
    """
    linhas = [
        "Para o Teorema Chinês dos Restos (TCR) ser aplicado, os <strong>novos módulos</strong> do sistema "
        "devem ser coprimos aos pares ($\\text{mdc} = 1$).<br>"
    ]

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
        return erro_precoce("Passo 2: Verificação do sistema", linhas)

    linhas.append("<br><strong style='color: var(--success-color);'>Conclusão:</strong> Todos os módulos são coprimos. O sistema é válido e o TCR pode ser aplicado!")
    return linhas


def passos3_4_5_tcr(restos, modulos):
    """
    Executa os cálculos finais e aplica a fórmula final do TCR.
    
    Calcula o Módulo Global (M), os módulos parciais (nk), os seus respectivos
    inversos modulares (dk) e unifica tudo na congruência final para encontrar o valor de 'x'.

    Args:
        restos (list): Lista de inteiros contendo as constantes resultantes das equações canônicas.
        modulos (list): Lista de inteiros contendo os módulos coprimos.

    Returns:
        tuple: Três listas de strings (linhas_p3, linhas_p4, linhas_p5) contendo 
               o código HTML documentando o passo a passo matemático das três últimas etapas.
    """
    M = reduce(lambda x, y: x * y, modulos)

    modulos_latex = " \\cdot ".join(map(str, modulos))
    linhas_p3 = [
        f"<strong>Módulo Global ($M$):</strong>",
        f"$M = {modulos_latex} = {M}$<br>",
        f"<strong>Módulos Parciais ($n_k = M / m_k$):</strong>",
    ]

    linhas_p4 = []
    termos_soma = []
    termos_formula = []
    x_acumulado = 0

    for k, (ak, mk) in enumerate(zip(restos, modulos), start=1):
        nk = M // mk
        dk = pow(nk, -1, mk)
        x_acumulado += ak * nk * dk

        linhas_p3.append(f"&bull; <strong>Equação {k}:</strong> $n_{{{k}}} = \\frac{{{M}}}{{{mk}}} = {nk}$")

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