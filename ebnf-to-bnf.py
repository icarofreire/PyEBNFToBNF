"""
*** converter gramática EBNF para BNF; ***
"""
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
def eliminar_grupos_bordas_strings(txt, tup_blocos):
    grupos_blocos = pegar_grupos(txt, tup_blocos)
    grupos_str = pegar_grupos_string(txt)
    for i in grupos_str:
        ind = txt.find(i)+1
        for idx, bloco in enumerate(grupos_blocos):
            indb = txt.find(bloco)
            if ind == indb:
                grupos_blocos.pop(idx)
    return grupos_blocos

def retirar_ultimos_blocos(line):
    bloco = ('(', ')')
    new_line = None

    reg = r"(| \{bloco[0]})"
    x = re.search(reg, line)
    if x != None and line[-1] == bloco[1]: new_line = '|' + line[3:-1]

    reg = r"(::=|:|=)"
    x = re.search(reg, line)
    if x != None and line[-1] == bloco[1]:
        lugar = x.span()
        new_line = line[0:lugar[1]] + line[lugar[1]+2:-1]

    return new_line

def detectar_divisor_production(line):
    reg = r"(::=|:|=)"
    x = re.search(reg, line)
    if x != None:
        lugar = x.span()
        return line[lugar[0]:lugar[1]]

def remove_duplicates(lista):
    return list(dict.fromkeys(lista))

def criar_auxiliares_por_grupos_obtidos(linha, con, nonterm, tup_blocos):
    novas_linhas = []
    paren = eliminar_grupos_bordas_strings(linha, tup_blocos)
    paren = remove_duplicates(paren)
    if len(paren) > 0:
        for idx, grupo in enumerate(paren):
            nonTerm_aux = nonterm + '_AUX_' + str(con) + '_' + str(idx)
            linha = linha.replace(grupo, nonTerm_aux)

            new_non_term = nonTerm_aux + ' ::= ' + grupo
            novas_linhas.append(new_non_term)
    return novas_linhas

def detectar_grupos_criar_non_terms(linhas_arq):
    divisor_production = ''
    nonterm_ant = ''
    novas_linhas = []
    for con, l in enumerate(arq):
        linha = l.strip()
        # \/ eliminar caracteres opcionais, ou de repetição;
        linha  = re.sub('[\?\+\*]+', ' ', linha)
        nonterm = get_nonTerm(linha)

        tup_blocos1 = ('(', ')')
        tup_blocos2 = ('[', ']')

        if nonterm != None:
            divisor_production = detectar_divisor_production(linha)
            nonterm_ant = nonterm

            novas_linhas += criar_auxiliares_por_grupos_obtidos(linha, con, nonterm, tup_blocos1)
            novas_linhas += criar_auxiliares_por_grupos_obtidos(linha, con, nonterm, tup_blocos2)
        elif linha[0] == '|' and nonterm != None:

            novas_linhas += criar_auxiliares_por_grupos_obtidos(linha, con, nonterm, tup_blocos1)
            novas_linhas += criar_auxiliares_por_grupos_obtidos(linha, con, nonterm, tup_blocos2)

        arq[con] = linha
    return novas_linhas


def criar_arq_bnf(linhas_arq, nome_arq_bnf):
    file = open(nome_arq_bnf, "w")
    for l in linhas_arq: file.write(l + "\n")
    file.close()

def add_novas_linhas(linhas_arq):
    novas_linhas = detectar_grupos_criar_non_terms(linhas_arq)
    for l in novas_linhas:
        l = retirar_ultimos_blocos(l)
        linhas_arq.append(l)
    return linhas_arq

def apply(linhas_arq, nome_arq_bnf):
    linhas_arq = add_novas_linhas(linhas_arq)
    criar_arq_bnf(linhas_arq, nome_arq_bnf)


arq = [
'IfStatement	::=	"if" "(" Expression ")" Statement ( "else" Statement )?',
'IterationStatement	::=	( "do" Statement "while" "(" Expression ")" ( ";" )? )',
'|	( "while" "(" Expression ")" Statement )',
'|	( "for" "(" ( ExpressionNoIn )? ";" ( Expression )? ";" ( Expression )? ")" Statement )',
'|	( "for" "(" "var" VariableDeclarationList ";" ( Expression )? ";" ( Expression )? ")" Statement )',
'|	( "for" "(" "var" VariableDeclarationNoIn "in" Expression ")" Statement )',
'|	( "for" "(" LeftHandSideExpressionForIn "in" Expression ")" Statement )',
'ContinueStatement	::=	"continue" ( Identifier )? ( ";" )?',
'BreakStatement	::=	"break" ( Identifier )? ( ";" )?',
'ReturnStatement	::=	"return" ( Expression )? ( ";" )?',
'WithStatement	::=	"with" "(" Expression ")" Statement',
'SwitchStatement	::=	"switch" "(" Expression ")" CaseBlock',
'CaseBlock	::=	"{" ( CaseClauses )? ( "}" | DefaultClause ( CaseClauses )? "}" )',
'CaseClauses	::=	( CaseClause )+',
'CaseClause	::=	( ( "case" Expression ":" ) ) ( StatementList )?',
'DefaultClause	::=	( ( "default" ":" ) ) ( StatementList )?',
]

apply(arq, "teste-bnf.txt")
# line = 'IfStatement_AUX_0_1 ::= ( " else " Statement )'
# line = inserir_espaco_aspas(line)
# print(line)
# # print( detectar_divisor_production(line) )
# print( retirar_aspas_ultimas(line) )