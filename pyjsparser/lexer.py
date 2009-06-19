"""
    jsparser.parser
    ~~~~~~~~~~~~~~~
    
    yacc grammar for ECMAScript 5
    
    :copyright: Copyright 2009 Michael van Tellingen
    :license: BSD
    
"""
import itertools
import re
import warnings

import ply.lex


class Lexer(object):

    # Keywords    
    keywords = (
        'FUNCTION', 'VAR', 'CONTINUE', 'RETURN', 'IF', 'ELSE', 'BREAK',
        'TRUE', 'FALSE', 'THIS', 'NEW', 'INSTANCEOF', 'IN', 'DELETE', 'TYPEOF',
        'VOID', 'NULL', 'WHILE', 'DO', 'FOR', 'TRY', 'THROW', 'CATCH',
        'DEFAULT', 'FINALLY', 'CASE', 'WITH', 'DEBUGGER', 'SWITCH',
        # 'GET', 'SET', 
    )

    # Reserved keywords
    reserved_keywords = (
        'ABSTRACT', 'BOOLEAN', 'INTERFACE', 'STATIC', 'BOOLEAN', 'EXTENDS',
        'LONG', 'SUPER', 'BYTE', 'FINAL', 'NATIVE', 'SYNCHRONIZED', 'CHAR',
        'FLOAT', 'PACKAGE', 'THROWS', 'CLASS', 'GOTO', 'PRIVATE', 'TRANSIENT',
        'CONST', 'IMPLEMENTS', 'PROTECTED', 'VOLATILE', 'DOUBLE', 'IMPORT',
        'PUBLIC', 'ENUM', 'INT', 'SHORT'
    )
    
    # Separate state when parsing a RegularExpressionLiteral
    states = (
        ('regex', 'exclusive'),
    )
    
    # Other tokens
    tokens = (

        "ID",
        
        # Comments
        'LINE_COMMENT', 'BLOCK_COMMENT', 
        
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
        
        # These are also tokens which are used for Regular Expressions
        'DIVIDE', 'DIVIDE_EQUALS',      # /  /=
        
        # Separate tokens for postfix usage with [no line-terminator]
        'INCR_NO_LT', 'DECR_NO_LT',     # [no line-terminator] ++ --
        
        # Types
        "STRING_LITERAL",
        "NUMBER_LITERAL",
        
        # Regex state tokens, these are only used when the parser is in the
        # regex state
        'RE_BODY', 'RE_END',
    )

    # Regex for identifiers
    identifier      = r'[a-zA-Z_$][0-9a-zA-Z_$]*'

    
    # StringLiteral
    t_STRING_LITERAL = r"""
    (
        (?:"    # Double quoted strings
            (?:
                [^"\\\n\r] |            # No line terminators, escape chars or "
                \\[-a-zA-Z\\?\'"] |     # Escaped characters 
                \\x[a-fA-F0-9]{2} |     # Hex chars
                \\u[a-fA-F0-9]{4}       # Unicode chars
            )*?
        )"
        |
        (?:'    # Single quoted strings
            (?:
                [^'\\\n\r] |            # No line terminators, escape chars or '
                \\[-a-zA-Z\\?'\"] |     # Escaped characters
                \\x[a-fA-F0-9]{2} |     # Hex chars
                \\u[a-fA-F0-9]{4}       # Unicode chars
            )*?
        )'
    )
    """

    # NumberLiteral
    t_NUMBER_LITERAL   = r"""
        (?:
            0[xX][0-9a-fA-F]+ |             # Hex digits
            [0-9]+e[0-9]+ |                 # Exponent integer
            [0-9]*\.[0-9]+(?:e?[0-9]+)? |   # .2e20
            [0-9]+\.(?:e?[0-9]+) |          # 2.e20     
            [0-9]+                          # integer
        )
    """

    # RegexLiteral (only in 'regex' state)
    regex_first_char  = r'(?:[^\n\r\[\\\/\*]|(?:\\.)|(?:\[[^\]]+\]))'
    regex_char        = r'(?:[^\n\r\[\\\/]|(?:\\.)|(?:\[[^\]]+\]))'
    t_regex_RE_BODY      = regex_first_char + regex_char + '*'
    t_regex_RE_END    = r'/[aig]*'

    # Comments    
    t_LINE_COMMENT  = r'//[^\r\n]*'
    t_BLOCK_COMMENT = r'/\*[^*]*\*+([^/*][^*]*\*+)*/'
    
    # Punctuators
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
    t_CONDOP            = r'\?'
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

    def t_INCR_NO_LT(self, t):
        r'[\r\n]+\s*\+\+'
        t.value = '++'
        return t

    def t_DECR_NO_LT(self, t):
        r'[\r\n]+\s*--'
        t.value = '--'
        return t
    
    def t_LINE_TERMINATOR(self, t):
        r'[\n\r]+(?!\s*(?:\+\+)|(?:--))'
        # Hack for INCR_NO_LT / DECR_NO_LT
        t.lineno += len(t.value)
        return t

    @ply.lex.TOKEN(identifier)
    def t_ID(self, t):
        if t.value in self.reserved_keywords_map:
            warnings.warn("The identifier '%s' is a reserved keyword" % t.value)
        t.type = self.keywords_map.get(t.value, "ID")
        return t
   
    t_ignore = ' \t'

    def t_error(self, t):
        raise TypeError("Unknown text '%s', %d" % (t.value[:20], t.lineno))
    
    t_regex_ignore = ''    
    def t_regex_error(self, t):
        raise TypeError("Error parsing regular expression '%s', %d" % (
            t.value[:20], t.lineno))
    
    
    def __init__(self):
        self.lexer = None
        self.next_tokens = []
        self.prev_token = None
        self.curr_token = None
        self.keywords_map = {}
        self.reserved_keywords_map = {}

        self._prepare_tokens()
        self.lexer = ply.lex.lex(object=self, debug=0, reflags=re.UNICODE|re.VERBOSE)
        
    def _prepare_tokens(self):
        """Fill the keywords_map and reserved_keywords_map dictionaries
        and append them to the tokens list
        
        """
        # Map the keywords and reserved keywords to a dict lcase => ucase
        self.keywords_map = {}
        for value in self.keywords:
            self.keywords_map[value.lower()] = value
        
        self.reserved_keywords_map = {}
        for value in self.reserved_keywords:
            self.reserved_keywords_map[value.lower()] = value
        
        # Add other tokens
        self.tokens = self.keywords + self.tokens
    




    def input(self, input):
        self.lexer.input(input)
    
    def token(self):
        """Return a token from the stream.
        
        This method serves as a proxy to the real lexer and allows us to:
         - Reference the previous token
         - Ignore tokens
         - Automatically append semi colons after a few keywords which
           do not allow a new-line (continue, break, return throw)
        
        """
        if self.next_tokens:
            return self.next_tokens.pop()
        
        while True:
            self.prev_token = self.curr_token
            self.curr_token = self.lexer.token()
            
            if self.curr_token is None or self.curr_token.type not in (
                'LINE_TERMINATOR','LINE_COMMENT', 'BLOCK_COMMENT'):
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
        """Create a LexToken instance for a semicolon."""
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
        """Return True if the previous token was a line terminator"""
        return self.prev_token and self.prev_token.type == 'LINE_TERMINATOR'

    def scan_regexp(self, start_value):
        """Read a regular expression literal
        
        This method switches the lexer to the 'regex' state and parses
        the tokens RE_BODY and RE_END.
        
        """
        self.lexer.begin('regex')
        token = self.token()
        if token.type == 'RE_BODY':
            pattern = token.value
        
        token = self.token()
        if token.type != 'RE_END':
            raise SyntaxError("Invalid Regular Expression")
        flags = token.value[1:]
        
        self.lexer.begin('INITIAL')
        return pattern, flags

    
if __name__ == "__main__":
    lexer = Lexer()
    input = r"""
    "foo ";
    "foo\"zar";
    'xar';
    'foo\'b ar';
    'foo\' \'\' b"ar\'\'"\'"\'"';
    "<" + ("div");

    
            
    """
    #input = open('jquery-1.3.2.js').read()
    lexer.input(input)
    for token in lexer:
        print token
