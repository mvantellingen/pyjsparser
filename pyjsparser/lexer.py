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
        'ABSTRACT', 'BOOLEAN', 'INTERFACE', 'STATIC', 'BOOLEAN', 'EXTENDS',
        'LONG', 'SUPER', 'BYTE', 'FINAL', 'NATIVE', 'SYNCHRONIZED', 'CHAR',
        'FLOAT', 'PACKAGE', 'THROWS', 'CLASS', 'GOTO', 'PRIVATE', 'TRANSIENT',
        'CONST', 'IMPLEMENTS', 'PROTECTED', 'VOLATILE', 'DOUBLE', 'IMPORT',
        'PUBLIC', 'ENUM', 'INT', 'SHORT'
    )
    
    tokens = (

        "ID",
        
        'COMMENT', 'BLOCK_COMMENT', 'REGEX',
        
        # Delimeters
        "LINE_TERMINATOR",              # One of LF, CR, LS, PS, see 7.3 
    
        # Punctuators
        'LBRACE', 'RBRACE',             # {  }
        'LPAREN', 'RPAREN',             # (  )
        'LBRACKET', 'RBRACKET',         # [  ]
        'PERIOD', 'SEMI', 'COMMA',      # .  ;  ,
        'LT', 'GT',                     # <  >
        'LE', 'GE',                     # <=  >=
        'EQ', 'NE',                     # ==  !=
        'EQT',  'NET',                  # ===  !==
        'PLUS', 'MINUS',                # +  -
        'TIMES', 'MOD',                 # *  %
        'INCR', 'DECR',                 # ++  --
        'LSHIFT', 'RSHIFT', 'URSHIFT',  # <<  >>  >>>
        'AND', 'OR', 'XOR', 'LNOT',     # &  |  ^  !
        'NOT', 'LAND', 'LOR',           # ~  &&  ||
        'CONDOP', 'COLON',              # ?  :
        'EQUALS', 'PLUS_EQUALS',        # =  +=
        'MINUS_EQUALS', 'TIMES_EQUALS', # -=  *=
        'MOD_EQUALS', 'LSHIFT_EQUALS',  # %=  <<=
        'RSHIFT_EQUALS',                # >>=
        'URSHIFT_EQUALS',               # >>>=
        'AND_EQUALS', 'OR_EQUALS',      # &=  |=
        'XOR_EQUALS',                   # ^=
        
        'DIVIDE', 'DIVIDE_EQUALS',      # /  /=
        
        # Separate tokens for postfix usage with [no line-terminator]
        'INCR_NO_LT', 'DECR_NO_LT',     # [no line-terminator] ++ --
        
        # Types
        "STRING_LITERAL",
        "NUMBER_LITERAL",
        
        
    )


    # Create regex tokens
    identifier = r'[a-zA-Z_$][0-9a-zA-Z_$]*'
    
    line_break      = r'(?:\r|\n)+'
    white_space     = r'(?:\s|\t)+'
    simple_escape   = r'\\([-a-zA-Z\\?\'"])'
    hex_char        = r'\\(x[a-fA-F0-9]{2})'
    unicode_char    = r'\\(u[a-fA-F0-9]{4})'
    escape_sequence = r'('+ simple_escape + '|'+ hex_char +'|'+ unicode_char +')'

    # Literals
    t_STRING_LITERAL    = (r'((?:"(?:[^"\\\n]|'+ escape_sequence +')*")|'
                            r"(?:'(?:[^'\\\n]|"+ escape_sequence +")*'))")

    t_NUMBER_LITERAL   = (r'(?:'                          
                            '(?:[0-9]*\.[0-9]+(?:e?[0-9]+)?)|'  # .2e20
                            '(?:[0-9]+\.(?:e?[0-9]+)?)|'        # 2.e20     
                            '[0-9]+'                            # integer
                           ')')

    # Regex
    t_REGEX         = r'(/(?=[^/*])(\\\\|\\/|[^/\n])*/)[a-zA-Z]*'

    # Comments    
    t_COMMENT       = r'//[^\n]*'
    t_BLOCK_COMMENT = r'/\*[^*]*\*+([^/*][^*]*\*+)*/'
    
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
    t_XOR_EQUALS        = r'\^='
    t_OR_EQUALS         = r'\|='
    t_EQUALS            = r'='
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
    t_RSHIFT            = r'>>'  # Signed right shift
    t_URSHIFT           = r'>>>' # Unsigned right shift
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


    def __init__(self,):
        self._prepare_tokens()
        self.lexer = None
        self.lexer = ply.lex.lex(object=self, debug=0)
        self.next_tokens = []
        self.prev_token = None
        self.curr_token = None
        
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
    
    def t_INCR_NO_LT(self, t):
        r'\n\s*\+\+'
        t.value = '++'
        return t

    def t_DECR_NO_LT(self, t):
        r'\n\s*--'
        t.value = '--'
        return t
    
    
    def t_LINE_TERMINATOR(self, t):
        r'\n+(?!\s*(?:\+\+)|(?:--))'
        # Hack for INCR_NO_LT / DECR_NO_LT
        t.lineno += len(t.value)
        return t
    
    t_ignore = ' \t'
    
    
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
    
    def token(self):
        if self.next_tokens:
            return self.next_tokens.pop()
        
        while True:
            self.prev_token = self.curr_token
            self.curr_token = self.lexer.token()
            
            if self.curr_token is None:
                break
            
            if self.curr_token.type != 'LINE_TERMINATOR':
                break
            
            # When a token should not be followed by a lineTerminator token
            # then we automatically replace the lineTerminator with a
            # semi-colon
            if self.prev_token and self.prev_token.type in [
                'CONTINUE', 'BREAK', 'RETURN', 'THROW']:
                return self.create_semicolon_token(self.curr_token)
                
        return self.curr_token
    
    
    def __iter__(self):
        while True:
            token = self.token()
            if token:
                yield token
            else:
                break
        
    def create_semicolon_token(self, token):
        asi_token = ply.lex.LexToken()
        asi_token.type = 'SEMI'
        asi_token.value = ';'
        if token:
            asi_token.lineno = token.lineno
            asi_token.lexpos = token.lexpos
        else:
            asi_token.lineno = 0
            asi_token.lexpos = 0
        return asi_token
        
    def auto_semicolon(self, token):
        if not token or (token and token.type == 'RBRACE') or \
           self.prev_line_terminator():
            if token:
                self.next_tokens.append(token)
            return self.create_semicolon_token(token)
        
    def prev_line_terminator(self):
        return self.prev_token and self.prev_token.type == 'LINE_TERMINATOR'
            
    
if __name__ == "__main__":
    lexer = Lexer()
    input = """
    [1,2]
            
    """
    lexer.input(input)
    for token in lexer:
        print token
