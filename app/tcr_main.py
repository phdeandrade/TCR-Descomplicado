"""
Módulo principal de orquestração do Teorema Chinês dos Restos (TCR).
Integra a formatação visual HTML com as etapas estritas de cálculo matemático.
"""

from app.utils import montar_step, unir
from app.tcr_solver import passo1_simplificacao, passo2_verificacao, passos3_4_5_tcr

def resolver_sistema_tcr(dados):
    """
    Organiza a resolução do sistema de congruências utilizando o TCR.
    
    Esta função processa os dados do frontend seguindo a ordem matemática estrita: simplificação das equações;
    verificação de coprimos; Caso o sistema seja válido,
    calcula os passos finais do TCR e compila os resultados em blocos HTML. Caso detecte
    uma impossibilidade matemática, interrompe a execução e retorna o erro.

    Args:
        dados (dict): Um dicionário contendo a chave 'equacoes', que armazena uma lista 
                      de dicionários com os parâmetros 'a', 'b', 'c' e 'n' de cada equação.

    Returns:
        dict: Um dicionário com a seguinte estrutura:
              - 'status' (str): "sucesso" se o processamento ocorreu sem falhas de rede/API, 
                                ou "erro" caso o dicionário esteja vazio.
              - 'mensagem' (str): O código HTML final contendo os blocos de passos da resolução 
                                  ou a justificativa matemática formatada para a interrupção.
    """

    equacoes = dados.get('equacoes', [])
    
    if not equacoes:
        return {"status": "erro", "mensagem": "Nenhuma equação recebida."}

    resultado_p1 = passo1_simplificacao(equacoes)
    
    if isinstance(resultado_p1, dict):
        return resultado_p1
        
    linhas_p1, restos, modulos = resultado_p1

    resultado_p2 = passo2_verificacao(modulos)
    
    if isinstance(resultado_p2, dict):
        html_passo1 = montar_step("Passo 1: Simplificação das equações", unir(linhas_p1))
        return {"status": "sucesso", "mensagem": html_passo1 + resultado_p2["mensagem"]}
        
    linhas_p2 = resultado_p2

    linhas_p3, linhas_p4, linhas_p5 = passos3_4_5_tcr(restos, modulos)

    explicacao = "".join([
        montar_step("Passo 1: Simplificação das equações", unir(linhas_p1)),
        montar_step("Passo 2: Verificação do sistema", unir(linhas_p2)),
        montar_step("Passo 3: Calcular M e n<sub>k</sub>", unir(linhas_p3)),
        montar_step("Passo 4: Calcular inversos", unir(linhas_p4)),
        montar_step("Passo 5: Aplicar na fórmula final", unir(linhas_p5)),
    ])

    return {"status": "sucesso", "mensagem": explicacao}