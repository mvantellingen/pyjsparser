"""
    jsparser.parser
    ~~~~~~~~~~~~~~~
    
    yacc grammar for ECMAScript 5
    
    :copyright: Copyright 2009 Michael van Tellingen
    :license: BSD
    
"""
import itertools
import warnings

import ply.lex
from ply.lex import TOKEN, LexToken


class Lexer(object):
    
    # Reserved keywords
    keywords = (
        'FUNCTION', 'VAR', 'CONTINUE', 'RETURN', 'IF', 'ELSE', 'BREAK',
        'TRUE', 'FALSE', 'THIS', 'NEW', 'INSTANCEOF', 'IN', 'DELETE', 'TYPEOF',
        'VOID', 'NULL', 'WHILE', 'DO', 'FOR', 'GET', 'SET', 'TRY', 'THROW', 'CATCH',
        'DEFAULT', 'FINALLY', 'CASE', 'WITH', 'DEBUGGER', 'SWITCH',
    )
    
    reserved_keywords = (
        'ABSTRACT', 'BOOLEAN'
        
    )
    
    tokens = (
        "ID",
        
        'LINE_TERM',
        
        'COMMENT', 'BLOCK_COMMENT', 'REGEX',
        
        "LPAREN", "RPAREN",
        "LBRACE", "RBRACE",
        "LBRACKET", "RBRACKET",
        "COMMA", "PERIOD",
        "SEMI", "COLON",
    
        'CONDOP',
        
        'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD', 'OR', 'AND', 'NOT', 'XOR',
        'LSHIFT', 'RSHIFT', 'URSHIFT', 'LOR', 'LAND', 'LNOT', 'LT', 'GT', 'LE',
        'GE', 'EQ', 'NE', 'EQT', 'NET', 
        'INCR_LBREAK', 'DECR_LBREAK','INCR', 'DECR', 
        'TIMES_EQUALS', 'DIVIDE_EQUALS', 'MOD_EQUALS', 'PLUS_EQUALS', 'MINUS_EQUALS',
        'LSHIFT_EQUALS', 'RSHIFT_EQUALS', 'URSHIFT_EQUALS', 'AND_EQUALS', 'NOT_EQUALS',
        'OR_EQUALS', "EQUALS", "MULTIPLY",
    
        "STRING_LITERAL",
        "INTEGER",
        "FLOAT",        
    )


    # Create regex tokens
    identifier = r'[a-zA-Z_$][0-9a-zA-Z_$]*'
    
    line_break      = r'(?:\r|\n)+'
    white_space     = r'(?:\s|\t)+'
    simple_escape   = r'\\([-a-zA-Z\\?\'"])'
    hex_char        = r'\\(x[a-fA-F0-9]{2})'
    unicode_char    = r'\\(u[a-fA-F0-9]{4})'
    escape_sequence = r'('+ simple_escape + '|'+ hex_char +'|'+ unicode_char +')'
    
    string_char     = r'[^\\\n]|'+ escape_sequence
    string_literal  = (r'((?:"(?:[^"\\\n]|'+ escape_sequence +')*")|'
                        r"(?:'(?:[^'\\\n]|"+ escape_sequence +")*'))")

    digit   = r'([0-9]+)'
    float   = r'(?:[0-9]*\.[0-9]+(?:e?[0-9]+)?)|(?:[0-9]+\.(?:e?[0-9]+)?)'
    
    block_comment = r'/\*[^*]*\*+([^/*][^*]*\*+)*/'


    def __init__(self,):
        self._prepare_tokens()
        self.lexer = None
        self.lexer = ply.lex.lex(object=self, debug=0)
        
    def _prepare_tokens(self):
                
        # Map the keywords and reserved keywords to a dict lcase => ucase
        self.keywords_map = {}
        for value in self.keywords:
            self.keywords_map[value.lower()] = value
        
        self.reserved_keywords_map = {}
        for value in self.reserved_keywords:
            self.reserved_keywords_map[value.lower()] = value
        
        
        # Add other tokens
        self.tokens = self.keywords + self.tokens
    

    t_COMMENT   = r'//[^\n]*'
    t_BLOCK_COMMENT = block_comment
    t_REGEX     = r'(/(?=[^/*])(\\\\|\\/|[^/\n])*/)[a-zA-Z]*'
    
    # Delimeters
    t_LPAREN    = r'\('
    t_RPAREN    = r'\)'
    t_LBRACKET  = r'\['
    t_RBRACKET  = r'\]'
    t_LBRACE    = r'{'
    t_RBRACE    = r'}'
    t_COMMA     = r','
    t_PERIOD    = r'\.'
    t_SEMI      = r';'
    t_COLON     = r':'
    
    t_CONDOP    = r'\?'
    
    # Operators
    t_TIMES_EQUALS      = r'\*='
    t_DIVIDE_EQUALS     = r'/='
    t_MOD_EQUALS        = r'%='
    t_PLUS_EQUALS       = r'\+='
    t_MINUS_EQUALS      = r'-='
    t_LSHIFT_EQUALS     = r'<<='
    t_RSHIFT_EQUALS     = r'>>='
    t_URSHIFT_EQUALS    = r'>>>='
    t_AND_EQUALS        = r'&='
    t_NOT_EQUALS        = r'\^='
    t_OR_EQUALS         = r'\|='
    t_PLUS              = r'\+'
    t_MINUS             = r'-'
    t_TIMES             = r'\*'
    t_DIVIDE            = r'/'
    t_MOD               = r'%'
    t_OR                = r'\|'
    t_AND               = r'&'
    t_NOT               = r'~'
    t_XOR               = r'\^'
    t_LSHIFT            = r'<<'
    t_RSHIFT            = r'>>' # Signed right shift
    t_URSHIFT           = r'>>' # Unsigned right shift
    t_LOR               = r'\|\|'
    t_LAND              = r'&&'
    t_LNOT              = r'!'
    t_LT                = r'<'
    t_GT                = r'>'
    t_LE                = r'<='
    t_GE                = r'>='
    t_EQ                = r'=='
    t_NE                = r'!='
    t_EQT               = r'==='
    t_NET               = r'!=='
    t_INCR              = r'\+\+'
    t_DECR              = r'--'
    
    def t_INCR_LBREAK(self, t):
        r'\n\s*\+\+'
        t.value = '++'
        return t
    
    def t_DECR_LBREAK(self, t):
        r'\n\s*--'
        t.value = '--'
        return t
    
    
    # Assignment operators
    t_EQUALS    = r'='
    
    
    def t_newline(self, t):
        r'\n+(?!\s*(?:\+\+)|(?:--))'
        # Hack for INCR_LBREAK / DECR_LBREAK
        t.lineno += len(t.value)
        t.type = 'LINE_TERM'
        
        #return t
    
    t_ignore = ' \t'
    
    t_STRING_LITERAL = string_literal
        
    t_INTEGER = digit;
    t_FLOAT = float;
    
    @TOKEN(identifier)
    def t_ID(self, t):
        if t.value in self.reserved_keywords_map:
            warnings.warn("The identifier '%s' is a reserved keyword" % t.value)
        t.type = self.keywords_map.get(t.value, "ID")
        return t
        
        
    def t_error(self, t):
        raise TypeError("Unknown text '%s', %d" % (t.value[:20], t.lineno))

    def input(self, input):
        self.lexer.input(input)
    
    @property
    def token(self):
        
        
        if not self.lexer:
            return None
        
        return self.lexer.token 
        return Tokenizer(self.lexer)
        
class Tokenizer(object):
    def __init__(self, lexer):
        self.lexer = lexer
        self.generator = self._build_generator()
        
    def _build_generator(self):
        node = self.lexer.next()
        
        for next_node in self.lexer:
            if node.type != 'LINE_TERM':
                yield node
            
            # 7.9 Automatic Semicolon insertion
            if next_node.type in ('RBRACE', 'LINE_TERM'):
                token = LexToken()
                token.type = 'SEMI'
                token.value = ';'
                token.lineno = node.lineno
                token.lexpos = node.lexpos + 1
                yield token
            
            node = next_node
        
        if node.type != 'LINE_TERM':
            yield node
            
    def __call__(self):
        try:
            token = self.generator.next()
            print token
            return token
        except StopIteration:
            return None
   
   
    
if __name__ == "__main__":
    input = """
    var test = 1;
    """
    lexer.input(input)
    for token in lexer:
        print token
