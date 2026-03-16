"""
Módulo de funções auxiliares.
Contém ferramentas para formatação de strings em LaTeX, construção de blocos HTML
dinâmicos e padronização de respostas de erro da API.
"""

def montar_step(titulo, conteudo):
    """
    Gera o código HTML estruturado para exibir uma etapa da resolução na interface.

    Args:
        titulo (str): O título do passo (ex: "Passo 1: Simplificação").
        conteudo (str): O conteúdo detalhado do passo em questão.

    Returns:
        str: Uma string contendo as tags HTML (`div`) com as classes apropriadas 
             para renderização no frontend.
    """
    return (
        f"<div class='step'>"
        f"<div class='step-title'>{titulo}</div>"
        f"<p>{conteudo}</p>"
        f"</div>"
    )

def unir(linhas):
    """
    Concatena uma lista de strings inserindo quebras de linha em formato HTML.

    Args:
        linhas (list): Uma lista de strings contendo as linhas de explicação ou equações.

    Returns:
        str: Uma única string com todos os elementos da lista separados pela tag `<br>`.
    """
    return "<br>".join(linhas)

def formatar_sinal(b):
    """
    Formata o termo independente de uma equação com o seu respectivo sinal matemático.
    
    Essencial para a montagem correta de strings LaTeX, evitando problemas de 
    exibição como "2x + -3" em vez do correto "2x - 3".

    Args:
        b (int): O valor numérico do termo independente.

    Returns:
        str: O número formatado com um espaço e o seu sinal (ex: "+ 5", "- 2"). 
             Retorna uma string vazia se o valor for 0.
    """
    if b > 0:
        return f"+ {b}"
    if b < 0:
        return f"- {abs(b)}"
    return ""

def erro_precoce(titulo, linhas):
    """
    Padroniza a resposta da API quando uma impossibilidade matemática é detectada.
    
    Retorna o status como "sucesso" para que o JavaScript não interprete como um erro 
    de servidor (Erro 500), mas envia a justificativa matemática empacotada em HTML 
    para ser exibida diretamente ao usuário.

    Args:
        titulo (str): O título da etapa em que o erro ocorreu.
        linhas (list): A lista de justificativas que explicam por que o sistema é inválido.

    Returns:
        dict: Um dicionário pronto para ser convertido em JSON pelo Flask, contendo as 
              chaves 'status' e 'mensagem'.
    """
    return {
        "status": "sucesso", 
        "mensagem": montar_step(titulo, unir(linhas))
    }