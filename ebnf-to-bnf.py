"""
*** converter gramática EBNF para BNF; ***
"""

import os
import sys
import re

# \/ detectar não-terminal;
def get_nonTerm(txt):
    reg = r"(::=|:|=)"
    x = re.search(reg, txt)
    if x != None:
        return txt[0:x.start()].strip()
    return None

# \/ obter lista de substrings que compõem caracteres de blocos;
def pegar_grupos(txt, tup_blocos):
    bloco = tup_blocos
    listg = []
    # \/ bloco final;
    fech = txt.rfind(bloco[1])
    while fech != -1:
        # \/ do final, volta ao bloco abertura;
        abre = txt[0:fech].rfind(bloco[0])
        if abre != -1:
            meio = txt[abre:-1]
            # \/ da abertura, vai ao próximo bloco final;
            fech2 = meio.find(bloco[1])
            grupo = meio[0:fech2+1]
            listg.append( grupo )

            txt = txt[0:abre]
            fech = txt.rfind(bloco[1])
    return listg

def find_nth(haystack: str, needle: str, n: int) -> int:
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+1)
        n -= 1
    return start

def rfind_nth(haystack: str, needle: str, n: int) -> int:
    start = haystack.rfind(needle)
    while start >= 0 and n > 1:
        start = haystack.rfind(needle, 0, start-1)
        n -= 1
    return start

def pegar_grupos_profund(txt, tup_blocos, niveis):
    bloco = tup_blocos
    listg = []
    # \/ bloco final;
    fech = find_nth(txt, bloco[1], niveis)
    while fech != -1:
        # \/ do final, volta ao bloco abertura;
        abre = rfind_nth(txt[0:fech+1], bloco[0], niveis)
        if abre != -1:
            meio = txt[abre:fech+1]
            listg.append( meio )

            txt = txt[0:abre]
            fech = find_nth(txt, bloco[1], niveis)
    return listg

# \/ obter lista de substrings que compõem blocos de strings("...", "...");
def pegar_grupos_string(txt):
    tipos_string = ('"', '\'')
    token_string = tipos_string[0]
    listg = []
    # \/ bloco final;
    fech = txt.rfind(token_string)
    while fech != -1:
        # \/ do final, volta ao bloco abertura;
        abre = txt[0:fech].rfind(token_string)
        if abre != -1:
            meio = txt[abre:-1]
            # \/ da abertura, vai ao próximo bloco final;
            fech2 = meio.find(token_string, 1)
            grupo = meio[0:fech2+1]
            listg.append( grupo )

            txt = txt[0:abre]
            fech = txt.rfind(token_string)
    return listg

""" \/ se o indice do inicio algum bloco encontrado,
estiver no mesmo local que um bloco de string encontrado (ex: "(");
elimina grupos obtidos com bordas que pertencam a grupos strings;
"""
def eliminar_grupos_bordas_strings(txt, tup_blocos, nivel):
    grupos_blocos = pegar_grupos_profund(txt, tup_blocos, nivel)
    grupos_str = pegar_grupos_string(txt)
    for i in grupos_str:
        ind = txt.find(i)+1
        for idx, bloco in enumerate(grupos_blocos):
            indb = txt.find(bloco)
            if ind == indb:
                grupos_blocos.pop(idx)
    return grupos_blocos

def retirar_ultimos_blocos(line, tup_blocos):
    bloco = tup_blocos
    new_line = None

    if bloco[0] == '(':
        reg1 = '\|[ \t]*\('
        reg2 = '(::=|:|=)[ \t]*\('
    if bloco[0] == '[':
        reg1 = '\|[ \t]*\['
        reg2 = '(::=|:|=)[ \t]*\['

    reg = reg1
    x = re.search(reg, line)
    if x != None and line[-1] == bloco[1]:
        lugar = x.span()
        new_line = line[0:lugar[1]-1] + line[lugar[1]+1:-1]

    reg = reg2
    x = re.search(reg, line)
    if x != None and line[-1] == bloco[1]:
        lugar = x.span()
        new_line = line[0:lugar[1]-1] + line[lugar[1]+1:-1]

    return new_line

def detectar_divisor_production(line):
    reg = r"(::=|:|=)"
    x = re.search(reg, line)
    if x != None:
        lugar = x.span()
        return line[lugar[0]:lugar[1]]

def remove_duplicates(lista):
    return list(dict.fromkeys(lista))

# \/ detectar dupla abertura ou fechadura de bloco;
def se_linha_dupla_bloco(linha):
    reg_dupla_bloc = r"(([\(\[][ ]*[\"\']?[\(\[][\"\']?)+)"

    dupla = re.search(reg_dupla_bloc, linha)
    return (dupla != None)

def replace_cont_with_regex(linha):
    reg_rep = "([^\"\'][\?\*\+][^\"\'])"
    sinais_rep = re.search(reg_rep, linha)
    while sinais_rep != None:
        lugar = sinais_rep.span()
        linha = linha[0:lugar[0]+1] + linha[lugar[1]-1:]
        sinais_rep = re.search(reg_rep, linha)
    # \/ retirar o ultimo;
    if linha[-1] == '?' or linha[-1] == '*' or linha[-1] == '+': linha = linha[0:-1]
    return linha

def criar_auxiliares_por_grupos_obtidos(linha, con, nonterm, tup_blocos, divisor_production, dic_grupo_nonTerm_aux, nivel, rep):
    novas_linhas = []
    paren = eliminar_grupos_bordas_strings(linha, tup_blocos, nivel)
    paren = remove_duplicates(paren)
    if len(paren) > 0:
        for idx, grupo in enumerate(paren):
            grupo = grupo.strip()
            if grupo != "":
                if grupo in dic_grupo_nonTerm_aux:
                    nonTerm_aux = dic_grupo_nonTerm_aux[grupo]
                else:
                    marca_nivel = '_n' + str(nivel) if nivel > 1 else ''
                    marca_rep = '_rep' + str(rep) if rep > 0 else ''
                    nonTerm_aux = nonterm + '_AUX_' + str(con) + '_' + str(idx) + marca_nivel + marca_rep
                    dic_grupo_nonTerm_aux[grupo] = nonTerm_aux

                linha = linha.replace(grupo, nonTerm_aux)

                # \/ detectar dupla abertura ou fechadura de bloco;
                if se_linha_dupla_bloco(linha):
                    rep+=1
                    tup_linha_novas_linhas = criar_auxiliares_por_grupos_obtidos(linha, con, nonterm, tup_blocos, divisor_production, dic_grupo_nonTerm_aux, nivel, rep)
                    novas_linhas += tup_linha_novas_linhas[1]
                    dic_grupo_nonTerm_aux.update(tup_linha_novas_linhas[2])
                    linha = tup_linha_novas_linhas[0]

                if se_linha_dupla_bloco(linha) and rep > 2:
                    nivel += 1
                    rep+=1
                    tup_linha_novas_linhas = criar_auxiliares_por_grupos_obtidos(linha, con, nonterm, tup_blocos, divisor_production, dic_grupo_nonTerm_aux, nivel, rep)
                    novas_linhas += tup_linha_novas_linhas[1]
                    dic_grupo_nonTerm_aux.update(tup_linha_novas_linhas[2])
                    linha = tup_linha_novas_linhas[0]


                div = divisor_production if divisor_production != None else '::='

                # \/ retirar ultimos blocos( "(" ... ")" | "[" ... "]" );
                grupo = grupo.strip()[1:-1]

                new_non_term = nonTerm_aux + ' ' + div + ' ' + grupo
                novas_linhas.append(new_non_term)
    return (linha, novas_linhas, dic_grupo_nonTerm_aux)

def detectar_grupos_criar_non_terms(linhas_arq, tup_blocos):
    divisor_production = ''
    nonterm_ant = ''
    novas_linhas = []
    dic_grupo_nonTerm_aux = {}

    rep = 1
    nivel = 1
    for con, l in enumerate(linhas_arq):
        linha = l.strip()
        # \/ eliminar caracteres opcionais, ou de repetição;
        linha = replace_cont_with_regex(linha)
        nonterm = get_nonTerm(linha)

        if nonterm != None:
            divisor_production = detectar_divisor_production(linha)
            nonterm_ant = nonterm

            tup_linha_novas_linhas = criar_auxiliares_por_grupos_obtidos(linha, con, nonterm, tup_blocos, divisor_production, dic_grupo_nonTerm_aux, nivel, rep)
            novas_linhas += tup_linha_novas_linhas[1]
            dic_grupo_nonTerm_aux.update(tup_linha_novas_linhas[2])
            linha = tup_linha_novas_linhas[0]
        elif linha[0] == '|':

            tup_linha_novas_linhas = criar_auxiliares_por_grupos_obtidos(linha, con, nonterm_ant, tup_blocos, divisor_production, dic_grupo_nonTerm_aux, nivel, rep)
            novas_linhas += tup_linha_novas_linhas[1]
            dic_grupo_nonTerm_aux.update(tup_linha_novas_linhas[2])
            linha = tup_linha_novas_linhas[0]

        novas_linhas = remove_duplicates(novas_linhas)
        linhas_arq[con] = linha
    return novas_linhas

def detectar_grupos_por_tipo_blocos(linhas_arq):
    tup_blocos1 = ('(', ')')
    tup_blocos2 = ('[', ']')
    novas_linhas = detectar_grupos_criar_non_terms(linhas_arq, tup_blocos1)
    novas_linhas += detectar_grupos_criar_non_terms(linhas_arq, tup_blocos2)
    return novas_linhas

def criar_arq_bnf(linhas_arq, nome_arq_bnf):
    file = open(nome_arq_bnf, "w")
    for l in linhas_arq: file.write(l + "\n")
    file.close()

def add_novas_linhas(linhas_arq):
    tup_bloco1 = ('(', ')')
    tup_bloco2 = ('[', ']')

    novas_linhas = detectar_grupos_por_tipo_blocos(linhas_arq)
    for l in novas_linhas:
        linhas_arq.append(l)
    return linhas_arq

def apply(linhas_arq, nome_arq_bnf):
    linhas_arq = add_novas_linhas(linhas_arq)
    criar_arq_bnf(linhas_arq, nome_arq_bnf)

def apply_in_file(arquivo):
    f = open(arquivo, "r")

    nome_bnf = ''
    idx_ex = f.name.find('.')
    if idx_ex != -1:
        nome_bnf = f.name[0:idx_ex] + '-bnf.txt'
    else:
        nome_bnf = f.name + '-bnf.txt'
    
    lines = f.readlines()
    apply(lines, nome_bnf)

    # Close opened file
    f.close()

def apply_in_folder(pasta):
    if os.path.exists(pasta):
        dir_list = os.listdir(pasta)
        for file in dir_list:
            if file.find('.txt') != -1:
                path = os.path.join(pasta, file)
                apply_in_file(path)
    else: print('Este diretório não existe;')

def get_args():
    pasta = None
    arquivo = None

    cmd1 = '-fold='
    cmd2 = '-file='
    for arg in sys.argv:
        if arg.find(cmd1) != -1: pasta = arg[len(cmd1):]
        if arg.find(cmd2) != -1: arquivo = arg[len(cmd2):]
    return {'pasta': pasta, 'arquivo': arquivo}

def apply_from_args():
    dic_args = get_args()
    if 'arquivo' in dic_args and dic_args['arquivo'] != None: apply_in_file(dic_args['arquivo'])
    if 'pasta' in dic_args and dic_args['pasta'] != None: apply_in_folder(dic_args['pasta'])


apply_from_args()
# apply(arq, "teste-bnf.txt")
# apply_in_file('js-grammar.txt')