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

# \/ detectar: '( ... )'
def detectar_paren(txt):
    lp = []
    reg = r"([\(\[]+)[^\"\']([^\(\)\[\]]+)[^\"\']([\)\]]+)"
    x = re.findall(reg, txt)
    for r in x:
        conteudo = ' '.join(list(r))
        lp.append(conteudo)
    return lp

# \/ inserir espaço em branco entre aspas e remover espaços duplicados;
def inserir_espaco_aspas(txt):
    txt = txt.replace("'", " ' ").replace('"', ' " ')
    txt = re.sub('[ \t]+', ' ', txt)
    return txt

def retirar_aspas_ultimas(line):
    new_line = None

    reg = r"(| \()"
    x = re.search(reg, line)
    if x != None and line[-1] == ')': new_line = '|' + line[3:-1]

    reg = r"(::=|:|=)"
    x = re.search(reg, line)
    if x != None and line[-1] == ')':
        lugar = x.span()
        new_line = line[0:lugar[1]] + line[lugar[1]+2:-1]

    return new_line

def detectar_divisor_production(line):
    reg = r"(::=|:|=)"
    x = re.search(reg, line)
    if x != None:
        lugar = x.span()
        return line[lugar[0]:lugar[1]]

def detectar_grupos_criar_non_terms(linhas_arq):
    nonterm_ant = ''
    novas_linhas = []
    for con, l in enumerate(arq):
        linha = l.strip()
        linha = inserir_espaco_aspas(linha)
        nonterm = get_nonTerm(linha)

        if nonterm != None:
            nonterm_ant = nonterm
            paren = detectar_paren(linha)
            for idx, p in enumerate(paren):
                nonTerm_aux = nonterm + '_AUX_' + str(con) + '_' + str(idx)
                linha = linha.replace(p, nonTerm_aux)

                new_non_term = nonTerm_aux + ' ::= ' + p
                novas_linhas.append(new_non_term)
        elif linha[0] == '|':
            paren = detectar_paren(linha)
            for idx, p in enumerate(paren):
                nonTerm_aux = nonterm_ant + '_AUX_' + str(con) + '_' + str(idx)
                linha = linha.replace(p, nonTerm_aux)

                new_non_term = nonTerm_aux + ' ::= ' + p
                novas_linhas.append(new_non_term)
        # print(linha)
        arq[con] = linha
    return novas_linhas


def criar_arq_bnf(linhas_arq, nome_arq_bnf):
    file = open(nome_arq_bnf, "w")
    for l in linhas_arq: file.write(l + "\n")
    file.close()

def add_novas_linhas(linhas_arq):
    novas_linhas = detectar_grupos_criar_non_terms(linhas_arq)
    for l in novas_linhas:
        # l = retirar_aspas_ultimas(l)
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