#
# calc.py
#
# mawabot - Maware's selfbot
# Copyright (c) 2017 Ma-wa-re, Ammon Smith
#
# mawabot is available free of charge under the terms of the MIT
# License. You are free to redistribute and/or modify it under those
# terms. It is distributed in the hopes that it will be useful, but
# WITHOUT ANY WARRANTY. See the LICENSE file for more details.
#

import ply.lex as lex
import ply.yacc as yacc

# Token list
tokens = (
    'INT',
    'FLOAT',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'FDIVIDE',
    'POWER',
    'LPAREN',
    'RPAREN',
    'LBRACE',
    'RBRACE',
    'LCBRACE',
    'RCBRACE',
)

t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_FDIVIDE = r'//'
t_POWER   = r'\*\*|^'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_LBRACE  = r'\['
t_RBRACE  = r'\]'
t_LCBRACE = r'\{'
t_RCBRACE = r'\}'

t_ignore  = '` \f\t\n'

def t_INT(t):
    r'[+-]?[0-9]+'

    t.value = int(t.value)
    return t

def t_FLOAT(t):
    r'[+-]?(?:(?:[0-9]*\.[0-9]+|[0-9]+\.[0-9]*)(?:[eE][+-][0-9]+)?|inf|nan)'

    t.value = float(t.value)
    return t

def t_error(t):
    # try and ignore errors
    t.lexer

# Grammar definition
precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'FDIVIDE'),
    ('left', 'POWER'),
    ('nonassoc', 'LPAREN', 'LBRACE', 'LCBRACE'),
)

def p_expr_plus(p):
    'expr : expr PLUS expr'

    p[0] = p[1] + p[3]

def p_expr_minus(p):
    'expr : expr MINUS expr'

    p[0] = p[1] - p[3]

def p_expr_mult(p):
    'expr : expr TIMES expr'

    p[0] = p[1] * p[3]

def p_expr_div(p):
    'expr : expr DIVIDE expr'

    p[0] = p[1] / p[3]

def p_expr_fdiv(p):
    'expr : expr FDIVIDE expr'

    p[0] = p[1] // p[3]

def p_expr_pow(p):
    'expr : expr POWER expr'

    p[0] = p[1] ** p[3]

def p_expr_paren(p):
    'expr : LPAREN expr RPAREN'

    p[0] = p[2]

def p_expr_brace(p):
    'expr : LBRACE expr RBRACE'

    p[0] = p[2]

def p_expr_cbrance(p):
    'expr : LCBRACE expr RCBRACE'

    p[0] = p[2]

def p_expr_int(p):
    'expr : INT'

    p[0] = p[1]

def p_expr_float(p):
    'expr : FLOAT'

    p[0] = p[1]

# Build them
lexer = lex.lex(optimize=1, reflags=re.IGNORECASE)
parser = yacc.yacc(optimize=1)

