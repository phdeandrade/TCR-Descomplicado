from app.utils import montar_step, unir
from app.tcr_solver import passo1_simplificacao, passo2_verificacao, passos3_4_5_tcr

def resolver_sistema_tcr(dados):
    """Recebe o JSON do frontend e processa as equações na nova ordem: Simplificação -> Verificação."""
    equacoes = dados.get('equacoes', [])
    if not equacoes:
        return {"status": "erro", "mensagem": "Nenhuma equação recebida."}

    # ==============================
    # PASSO 1: SIMPLIFICAÇÃO DAS EQUAÇÕES
    # ==============================
    resultado_p1 = passo1_simplificacao(equacoes)
    
    # Se retornou um dict, houve erro (equação sem solução) e já encerra cedo
    if isinstance(resultado_p1, dict):
        return resultado_p1
        
    linhas_p1, restos, modulos = resultado_p1

    # ==============================
    # PASSO 2: VERIFICAÇÃO DA SOLUÇÃO (COPRIMOS)
    # ==============================
    resultado_p2 = passo2_verificacao(modulos)
    
    if isinstance(resultado_p2, dict):
        html_passo1 = montar_step("Passo 1: Simplificação das equações", unir(linhas_p1))
        return {"status": "sucesso", "mensagem": html_passo1 + resultado_p2["mensagem"]}
        
    linhas_p2 = resultado_p2

    # ==============================
    # PASSOS 3, 4 e 5: CALCULAR M, INVERSOS E FÓRMULA FINAL
    # ==============================
    linhas_p3, linhas_p4, linhas_p5 = passos3_4_5_tcr(restos, modulos)

    # ==============================
    # CONSTRUÇÃO DAS 5 DIVS EM HTML (SUCESSO TOTAL)
    # ==============================
    explicacao = "".join([
        montar_step("Passo 1: Simplificação das equações", unir(linhas_p1)),
        montar_step("Passo 2: Verificação do sistema", unir(linhas_p2)),
        montar_step("Passo 3: Calcular M e n<sub>k</sub>", unir(linhas_p3)),
        montar_step("Passo 4: Calcular inversos", unir(linhas_p4)),
        montar_step("Passo 5: Aplicar na fórmula final", unir(linhas_p5)),
    ])

    return {"status": "sucesso", "mensagem": explicacao}