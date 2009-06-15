"""
    jsparser.parser
    ~~~~~~~~~~~~~~~
    
    yacc grammar for ECMAScript 5
    
    :copyright: Copyright 2009 Michael van Tellingen
    :license: BSD
    
"""
import ply.yacc
import ply.lex

from pyjsparser.lexer import Lexer
from pyjsparser import ast

class Parser(object):
    """
    Grammar for ECMAScript 5 (ECMA-262 Final Draft, 5th edition april 2009)
    
    The *NoIn Rules stand for No IN and is required for the IterationStatement
    
    The *NoBF Rules stand for No Brace or Function and is required for
    the ExpressionStatement rule.
    
    The grammer contains 1 shift/reduce conflict caused by the if/else clause,
    which is harmless.
    """
    def __init__(self):
        self.lexer = Lexer()
        self.tokens = self.lexer.tokens
        optionals = (
            'FormalParameterList',
            'SourceElements',
            'StatementList',
            'Elision',
            'Expression',
            'ExpressionNoIn',
            'Identifier',
            'Initialiser',
            'InitialiserNoIn',
            'CaseClauses',
            
        )
        for rulename in optionals:
            self._create_opt_rule(rulename)


        self.yacc = ply.yacc.yacc(module=self,  start='Program')

    
    # From plycparser:
    def _create_opt_rule(self, rulename):
        """ Given a rule name, creates an optional ply.yacc rule
            for it. The name of the optional rule is
            <rulename>_opt
        """
        optname = rulename + '_opt'
    
        def optrule(self, p):
            p[0] = p[1]
    
        optrule.__doc__ = '%s : empty\n| %s' % (optname, rulename)
        optrule.__name__ = 'p_%s' % optname
        setattr(self.__class__, optrule.__name__, optrule)    

    def parse(self, input):
        return self.yacc.parse(input, lexer=self.lexer)
    
    # Precedence rules
    precedence = (
        ('nonassoc', 'IF_WITHOUT_ELSE'),
        ('nonassoc', 'ELSE'),
        ('left', 'LOR'),
        ('left', 'LAND'),
        ('left', 'OR'),
        ('left', 'XOR'),
        ('left', 'AND'),
        ('left', 'EQ', 'NE'),
        ('left', 'GT', 'GE', 'LT', 'LE'),
        ('left', 'RSHIFT', 'LSHIFT'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE', 'MOD')
    )    

    def build_list(self, p, base, node, count=None):
        """Helper function to build a list"""
        if count is None:
            count = node
        if len(p) <= count:
            return [p[base]]
        else:
            p[base].append(p[node])
            return p[base]


    # Internal helpers
    def p_empty(self, p):
        """empty :"""
    
    def p_auto_semicolon(self, p):
        """auto_semicolon : error """

    def p_error(self, p):
        if (p and p.type != 'SEMI') or not p:
            next_token = self.lexer.auto_semicolon(p)
            if next_token:
                self.yacc.errok()
                return next_token

        raise SyntaxError("%r unexpected at %d:%d" % (
            p.value, p.lineno, p.lexpos))

    #
    # 7. Lexical Conventions
    # Only some are implemented currently, see lexer for more

    # 7.4 Comments    
    def p_Comment(self, p):
        """Comment : SingleLineComment
                   | MultiLineComment """
        p[0] = p[1]
        
    def p_SingleLineComment(self, p):
        """SingleLineComment : COMMENT"""
        p[0] = ast.LineComment(p[1])

    def p_MultiLineComment(self, p):
        """MultiLineComment : BLOCK_COMMENT"""
        p[0] = ast.BlockComment(p[1])

    def p_IdentifierName(self, p):
        """IdentifierName : Identifier"""
        print "IdentifierName: ", list(p)
        p[0] = p[1]      

    def p_Identifier(self, p):
        """Identifier : ID"""
        print "Identifier: ", list(p)
        p[0] = ast.Identifier(p[1])

    # TODO: Note that the RegularExpressionLiteral doesn't belong here
    # according to the ecmascript standard
    def p_Literal(self, p):
        """Literal : NullLiteral
                   | BooleanLiteral
                   | NumericLiteral
                   | StringLiteral
                   | RegularExpressionLiteral"""
        p[0] = p[1]

    def p_NullLiteral(self, p):
        """NullLiteral : NULL """
        print "NullLiteral: ", list(p)

    def p_BooleanLiteral(self, p):
        """BooleanLiteral : TRUE
                          | FALSE"""
        print "BooleanLiteral: ", list(p)
        p[0] = ast.Boolean(p[1])
        
    # TODO
    def p_NumericLiteral(self, p):
        """NumericLiteral : NUMBER_LITERAL"""
        print "NumericLiteral: ", list(p)
        p[0] = ast.Number(p[1])
        
    def p_StringLiteral(self, p):
        """StringLiteral : STRING_LITERAL"""
        print "StringLiteral: ", list(p)
        p[0] = ast.String(data=p[1])

    def p_RegularExpressionLiteral(self, p):
        """RegularExpressionLiteral : REGEX"""
        print "RegularExpressionLiteral: ", list(p)
    #
    # 11. Expressions

    # 11.1 Primary Expressions
    def p_PrimaryExpression(self, p):
        """PrimaryExpression : PrimaryExpressionNoObj
                             | ObjectLiteral"""
        p[0] = p[1]

    def p_PrimaryExpressionNoObj(self, p):
        """PrimaryExpressionNoObj : THIS
                                  | Identifier
                                  | Literal
                                  | ArrayLiteral
                                  | LPAREN Expression RPAREN"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = p[2]

    def p_ArrayLiteral(self, p):
        """ArrayLiteral : LBRACKET Elision_opt RBRACKET
                        | LBRACKET ElementList RBRACKET
                        | LBRACKET ElementList COMMA Elision_opt RBRACKET"""
        print "ArrayLiteral: ", list(p)

    def p_ElementList(self, p):
        """ElementList : Elision_opt AssignmentExpression
                       | ElementList COMMA Elision_opt AssignmentExpression """
        print "ElementList: ", list(p) 

    # TODO
    def p_Elision(self, p):
        """Elision : COMMA
                   | Elision COMMA"""
        print "Elision: ", list(p)
        

    def p_ObjectLiteral(self, p):
        """ObjectLiteral : LBRACE RBRACE
                         | LBRACE PropertyNameAndValueList RBRACE
                         | LBRACE PropertyNameAndValueList COMMA RBRACE"""
        p[0] = ast.Object(properties=p[2] if len(p) > 3 else [])
                         
    def p_PropertyNameAndValueList(self, p):
        """PropertyNameAndValueList : PropertyAssignment 
                                    | PropertyNameAndValueList COMMA PropertyAssignment"""
        p[0] = self.build_list(p, 1, 3)

    # TODO: add get / set 
    def p_PropertyAssignment(self, p):
        """PropertyAssignment : PropertyName COLON AssignmentExpression
                              | GET PropertyName \
                                    LPAREN RPAREN \
                                    LBRACE FunctionBody RBRACE
                              | SET PropertyName \
                                    LPAREN PropertySetParameterList RPAREN \
                                    LBRACE FunctionBody RBRACE """
        if len(p) == 4:
            p[0] = ast.Assign(node=p[1], operator=p[2], expression=p[3])
            
    def p_PropertyName(self, p):
        """PropertyName : IdentifierName
                        | StringLiteral 
                        | NumericLiteral"""
        p[0] = p[1]
            
    def p_PropertySetParameterList(self, p):
        """PropertySetParameterList : Identifier """
        p[0] = p[1]
        
    # 11.2 Left-Hand-Side Expressions
    # TODO
    def p_MemberExpression(self, p):
        """MemberExpression : PrimaryExpression
                            | FunctionExpression 
                            | MemberExpression LBRACKET Expression RBRACKET
                            | MemberExpression PERIOD IdentifierName 
                            | NEW MemberExpression Arguments """
        print "MemberExpression: ", list(p)
        if len(p) == 2:
            p[0] = p[1]
        elif p[1] != 'new':
            p[0] = ast.ElementGet(node=p[1], element=p[3])
        
    # TODO
    def p_MemberExpressionNoBF(self, p):
        """MemberExpressionNoBF : PrimaryExpressionNoObj 
                                | MemberExpressionNoBF LBRACKET Expression RBRACKET
                                | MemberExpressionNoBF PERIOD IdentifierName 
                                | NEW MemberExpression Arguments """
        print "MemberExpressionNoBF: ", list(p)
        if len(p) == 2:
            p[0] = p[1]
            
        elif p[1] != 'new':
            p[0] = ast.ElementGet(node=p[1], element=p[3])

        else:
            p[0] = ast.New(identifier=p[2], arguments=p[3])

    def p_NewExpression(self, p):
        """NewExpression : MemberExpression
                         | NEW NewExpression """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.New(identifier=p[2])

    def p_NewExpressionNoBF(self, p):
        """NewExpressionNoBF : MemberExpressionNoBF
                             | NEW NewExpression"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.New(identifier=p[2])

    def p_CallExpression(self, p):
        """CallExpression : MemberExpression Arguments
                          | CallExpression Arguments
                          | CallExpression LBRACKET Expression RBRACKET
                          | CallExpression PERIOD IdentifierName"""
        print "CallExpression: ", list(p)
        if len(p) == 3:
            p[0] = ast.FuncCall(node=p[1], arguments=p[2])
        

    def p_CallExpressionNoBF(self, p):
        """CallExpressionNoBF : MemberExpressionNoBF Arguments
                              | CallExpressionNoBF Arguments
                              | CallExpressionNoBF LBRACKET Expression RBRACKET
                              | CallExpressionNoBF PERIOD IdentifierName"""
        print "CallExpressionNoBF: ", list(p)
        if len(p) == 3:
            p[0] = ast.FuncCall(node=p[1], arguments=p[2])
            
    def p_Arguments(self, p):
        """Arguments : LPAREN RPAREN
                     | LPAREN ArgumentList RPAREN"""
        print "Arguments: ", list(p)
        if len(p) == 4:
            p[0] = p[2]

    def p_ArgumentList(self, p):
        """ArgumentList : AssignmentExpression
                        | ArgumentList COMMA AssignmentExpression"""
        print "ArgumentList: ", list(p)
        p[0] = self.build_list(p, 1, 3)

                             
    def p_LeftHandSideExpression(self, p):
        """LeftHandSideExpression : NewExpression
                                  | CallExpression """
        print "LeftHandSideExpression: ", list(p)
        p[0] = p[1]

    def p_LeftHandSideExpressionNoBF(self, p):
        """LeftHandSideExpressionNoBF : NewExpressionNoBF
                                      | CallExpressionNoBF """
        print "LeftHandSideExpressionNoBF: ", list(p)
        p[0] = p[1]
    
    # 11.3 Postfix Expressions
    def p_PostfixExpression(self, p): 
        """PostfixExpression : LeftHandSideExpression
                             | LeftHandSideExpression INCR_NO_LT 
                             | LeftHandSideExpression DECR_NO_LT"""
        print "PostfixExpression: ", list(p)

        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.UnaryOp(operator=p[3], value=p[1], postfix=True)
            
    def p_PostfixExpressionNoBF(self, p): 
        """PostfixExpressionNoBF : LeftHandSideExpressionNoBF
                                 | LeftHandSideExpressionNoBF INCR_NO_LT
                                 | LeftHandSideExpressionNoBF DECR_NO_LT"""
        print "PostfixExpressionNoBF: ", list(p)

        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.UnaryOp(operator=p[3], value=p[1], postfix=True)
        
    # 11.4 Unary Operators
    def p_UnaryExpressionCommon(self, p):
        """UnaryExpressionCommon : DELETE UnaryExpression 
                                 | VOID UnaryExpression 
                                 | TYPEOF UnaryExpression 
                                 | INCR UnaryExpression
                                 | INCR_NO_LT UnaryExpression 
                                 | DECR UnaryExpression
                                 | DECR_NO_LT UnaryExpression 
                                 | PLUS UnaryExpression 
                                 | MINUS UnaryExpression   
                                 | NOT UnaryExpression 
                                 | LNOT UnaryExpression """
        print "UnaryExpressionCommon: ", list(p)
        
        p[0] = ast.UnaryOp(operator=p[1], value=p[2], postfix=False)
    
    def p_UnaryExpression(self, p):
        """UnaryExpression : PostfixExpression
                           | UnaryExpressionCommon"""
        print "UnaryExpression: ", list(p)
        p[0] = p[1]
        print list(p)
                           
    def p_UnaryExpressionNoBF(self, p):
        """UnaryExpressionNoBF : PostfixExpressionNoBF
                               | UnaryExpressionCommon"""
        print "UnaryExpressionNoBF: ", list(p)
        p[0] = p[1]

    # 11.5 Multiplicative Operators
    def p_MultiplicativeExpression(self, p):
        """MultiplicativeExpression : UnaryExpression 
                                    | MultiplicativeExpression TIMES UnaryExpression 
                                    | MultiplicativeExpression DIVIDE UnaryExpression 
                                    | MultiplicativeExpression MOD UnaryExpression """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.BinOp(operator=p[2], left=p[1], right=p[3])

    def p_MultiplicativeExpressionNoBF(self, p):
        """MultiplicativeExpressionNoBF : UnaryExpressionNoBF 
                                        | MultiplicativeExpressionNoBF TIMES UnaryExpression 
                                        | MultiplicativeExpressionNoBF DIVIDE UnaryExpression 
                                        | MultiplicativeExpressionNoBF MOD UnaryExpression """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.BinOp(operator=p[2], left=p[1], right=p[3])

    # 11.6 Additive Operators
    def p_AdditiveExpression(self, p):
        """AdditiveExpression : MultiplicativeExpression 
                              | AdditiveExpression PLUS MultiplicativeExpression 
                              | AdditiveExpression MINUS MultiplicativeExpression"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.BinOp(operator=p[2], left=p[1], right=p[3])


    def p_AdditiveExpressionNoBF(self, p):
        """AdditiveExpressionNoBF : MultiplicativeExpressionNoBF
                                  | AdditiveExpressionNoBF PLUS MultiplicativeExpression 
                                  | AdditiveExpressionNoBF MINUS MultiplicativeExpression"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.BinOp(operator=p[2], left=p[1], right=p[3])

    # 11.7 Bitwise Shift Operators
    def p_ShiftExpression(self, p):
        """ShiftExpression : AdditiveExpression 
                           | ShiftExpression LSHIFT AdditiveExpression 
                           | ShiftExpression RSHIFT AdditiveExpression 
                           | ShiftExpression URSHIFT AdditiveExpression"""
        print "ShiftExpression: ", list(p)
        if len(p) == 2:
            p[0] = p[1]
            
    def p_ShiftExpressionNoBF(self, p):
        """ShiftExpressionNoBF : AdditiveExpressionNoBF 
                               | ShiftExpressionNoBF LSHIFT AdditiveExpression 
                               | ShiftExpressionNoBF RSHIFT AdditiveExpression 
                               | ShiftExpressionNoBF URSHIFT AdditiveExpression"""
        print "ShiftExpressionNoBF: ", list(p)
        if len(p) == 2:
            p[0] = p[1]
            

    # 11.8 Relational Operators
    def p_RelationalExpression(self, p):
        """RelationalExpression : ShiftExpression 
                                | RelationalExpression GT ShiftExpression 
                                | RelationalExpression LT ShiftExpression 
                                | RelationalExpression GE ShiftExpression 
                                | RelationalExpression LE ShiftExpression 
                                | RelationalExpression INSTANCEOF ShiftExpression 
                                | RelationalExpression IN ShiftExpression"""
        print "RelationalExpression: ", list(p)
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.BinOp(operator=p[2], left=p[1], right=p[3])

    def p_RelationalExpressionNoIn(self, p):
        """RelationalExpressionNoIn : ShiftExpression 
                                    | RelationalExpressionNoIn GT ShiftExpression 
                                    | RelationalExpressionNoIn LT ShiftExpression 
                                    | RelationalExpressionNoIn GE ShiftExpression 
                                    | RelationalExpressionNoIn LE ShiftExpression 
                                    | RelationalExpressionNoIn INSTANCEOF ShiftExpression"""
        print "RelationalExpressionNoIn: ", list(p)
        if len(p) == 2:
            p[0] = p[1]


    def p_RelationalExpressionNoBF(self, p):
        """RelationalExpressionNoBF : ShiftExpressionNoBF
                                    | RelationalExpressionNoBF GT ShiftExpression 
                                    | RelationalExpressionNoBF LT ShiftExpression 
                                    | RelationalExpressionNoBF GE ShiftExpression 
                                    | RelationalExpressionNoBF LE ShiftExpression 
                                    | RelationalExpressionNoBF INSTANCEOF ShiftExpression
                                    | RelationalExpressionNoBF IN ShiftExpression"""
        print "RelationalExpressionNoBF: ", list(p)
        if len(p) == 2:
            p[0] = p[1]


    # 11.9 Equality Operators
    def p_EqualityExpression(self, p):
        """EqualityExpression : RelationalExpression 
                              | EqualityExpression EQ RelationalExpression 
                              | EqualityExpression NE RelationalExpression 
                              | EqualityExpression EQT RelationalExpression 
                              | EqualityExpression NET RelationalExpression"""
        print "EqualityExpression: ", list(p)
        if len(p) == 2:
            p[0] = p[1]

    def p_EqualityExpressionNoIn(self, p):
        """EqualityExpressionNoIn : RelationalExpressionNoIn 
                                  | EqualityExpressionNoIn EQ RelationalExpressionNoIn 
                                  | EqualityExpressionNoIn NE RelationalExpressionNoIn 
                                  | EqualityExpressionNoIn EQT RelationalExpressionNoIn 
                                  | EqualityExpressionNoIn NET RelationalExpressionNoIn"""
        print "EqualityExpressionNoIn: ", list(p)
        if len(p) == 2:
            p[0] = p[1]

    def p_EqualityExpressionNoBF(self, p):
        """EqualityExpressionNoBF : RelationalExpressionNoBF 
                                  | EqualityExpressionNoBF EQ RelationalExpressionNoIn 
                                  | EqualityExpressionNoBF NE RelationalExpressionNoIn 
                                  | EqualityExpressionNoBF EQT RelationalExpressionNoIn 
                                  | EqualityExpressionNoBF NET RelationalExpressionNoIn"""
        print "EqualityExpressionNoBF: ", list(p)
        if len(p) == 2:
            p[0] = p[1]


    # 11.10 Binary Bitwise Operators
    def p_BitwiseANDExpression(self, p):
        """BitwiseANDExpression : EqualityExpression 
                                | BitwiseANDExpression AND EqualityExpression"""
        if len(p) == 4:
            p[0] = ast.BinOp(operator=p[2], left=p[1], right=p[3])
        else:
            p[0] = p[1]

    def p_BitwiseANDExpressionNoIn(self, p):                            
        """BitwiseANDExpressionNoIn : EqualityExpressionNoIn 
                                    | BitwiseANDExpressionNoIn AND EqualityExpressionNoIn"""
        if len(p) == 4:
            p[0] = ast.BinOp(operator=p[2], left=p[1], right=p[3])
        else:
            p[0] = p[1]

    def p_BitwiseANDExpressionNoBF(self, p):                            
        """BitwiseANDExpressionNoBF : EqualityExpressionNoBF
                                    | BitwiseANDExpressionNoBF AND EqualityExpressionNoIn"""
        if len(p) == 4:
            p[0] = ast.BinOp(operator=p[2], left=p[1], right=p[3])
        else:
            p[0] = p[1]

    def p_BitwiseXORExpression(self, p):                                
        """BitwiseXORExpression : BitwiseANDExpression 
                                | BitwiseXORExpression XOR BitwiseANDExpression """
        if len(p) == 4:
            p[0] = ast.BinOp(operator=p[2], left=p[1], right=p[3])
        else:
            p[0] = p[1]

    def p_BitwiseXORExpressionNoIn(self, p):                            
        """BitwiseXORExpressionNoIn : BitwiseANDExpressionNoIn 
                                    | BitwiseXORExpressionNoIn XOR BitwiseANDExpressionNoIn """
        if len(p) == 4:
            p[0] = ast.BinOp(operator=p[2], left=p[1], right=p[3])
        else:
            p[0] = p[1]

    def p_BitwiseXORExpressionNoBF(self, p):                            
        """BitwiseXORExpressionNoBF : BitwiseANDExpressionNoBF
                                    | BitwiseXORExpressionNoBF XOR BitwiseANDExpressionNoIn """
        if len(p) == 4:
            p[0] = ast.BinOp(operator=p[2], left=p[1], right=p[3])
        else:
            p[0] = p[1]
                                    
    def p_BitwiseORExpression(self, p):
        """BitwiseORExpression : BitwiseXORExpression 
                               | BitwiseORExpression OR BitwiseXORExpression """
        if len(p) == 4:
            p[0] = ast.BinOp(operator=p[2], left=p[1], right=p[3])
        else:
            p[0] = p[1]

    def p_BitwiseORExpressionNoIn(self, p):                        
        """BitwiseORExpressionNoIn : BitwiseXORExpressionNoIn 
                                   | BitwiseORExpressionNoIn OR BitwiseXORExpressionNoIn"""
        if len(p) == 4:
            p[0] = ast.BinOp(operator=p[2], left=p[1], right=p[3])
        else:
            p[0] = p[1]

    def p_BitwiseORExpressionNoBF(self, p):                        
        """BitwiseORExpressionNoBF : BitwiseXORExpressionNoBF 
                                   | BitwiseORExpressionNoBF OR BitwiseXORExpressionNoIn"""
        if len(p) == 4:
            p[0] = ast.BinOp(operator=p[2], left=p[1], right=p[3])
        else:
            p[0] = p[1]

    # 11.11 Binary Logical Operators
    def p_LogicalANDExpression(self, p):
        """LogicalANDExpression : BitwiseORExpression 
                                | LogicalANDExpression LAND BitwiseORExpression"""
        if len(p) == 4:
            p[0] = ast.BinOp(operator=p[2], left=p[1], right=p[3])
        else:
            p[0] = p[1]


    def p_LogicalANDExpressionNoIn(self, p):
        """LogicalANDExpressionNoIn : BitwiseORExpressionNoIn
                                    | LogicalANDExpressionNoIn LAND BitwiseORExpressionNoIn """
        if len(p) == 4:
            p[0] = ast.BinOp(operator=p[2], left=p[1], right=p[3])
        else:
            p[0] = p[1]


    def p_LogicalANDExpressionNoBF(self, p):
        """LogicalANDExpressionNoBF : BitwiseORExpressionNoBF
                                    | LogicalANDExpressionNoBF LAND BitwiseORExpressionNoIn """
        if len(p) == 4:
            p[0] = ast.BinOp(operator=p[2], left=p[1], right=p[3])
        else:
            p[0] = p[1]

    """ (true || false) || (true  && false)
        true && true
        """

    def p_LogicalORExpression(self, p):
        """LogicalORExpression : LogicalANDExpression
                               | LogicalORExpression LOR LogicalANDExpression """
        if len(p) == 4:
            p[0] = ast.BinOp(operator=p[2], left=p[1], right=p[3])
        else:
            p[0] = p[1]



    def p_LogicalORExpressionNoIn(self, p):
        """LogicalORExpressionNoIn : LogicalANDExpressionNoIn 
                                   | LogicalORExpressionNoIn LOR LogicalANDExpressionNoIn """
        if len(p) == 4:
            p[0] = ast.BinOp(operator=p[2], left=p[1], right=p[3])
        else:
            p[0] = p[1]


    def p_LogicalORExpressionNoBF(self, p):
        """LogicalORExpressionNoBF : LogicalANDExpressionNoBF 
                                   | LogicalORExpressionNoBF LOR LogicalANDExpressionNoIn """
        if len(p) == 4:
            p[0] = ast.BinOp(operator=p[2], left=p[1], right=p[3])
        else:
            p[0] = p[1]


    # 11.12 Conditional Operator ( ?: )                                 
    def p_ConditionalExpression(self, p):
        """ConditionalExpression : LogicalORExpression 
                                 | LogicalORExpression CONDOP \
                                    AssignmentExpression COLON \
                                    AssignmentExpression """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.If(expression=p[1], true=[p[3]], false=[p[5]])

    def p_ConditionalExpressionNoIn(self, p):                             
        """ConditionalExpressionNoIn : LogicalORExpressionNoIn 
                                     | LogicalORExpressionNoIn CONDOP \
                                        AssignmentExpression COLON \
                                        AssignmentExpressionNoIn"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.If(expression=p[1], true=[p[3]], false=[p[5]])


    def p_ConditionalExpressionNoBF(self, p):
        """ConditionalExpressionNoBF : LogicalORExpressionNoBF 
                                     | LogicalORExpressionNoBF CONDOP \
                                        AssignmentExpression COLON \
                                        AssignmentExpression """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.If(expression=p[1], true=[p[3]], false=[p[5]])



    # 11.13 Assignment Operators
    def p_AssignmentExpression(self, p):
        """AssignmentExpression : ConditionalExpression
                                | LeftHandSideExpression AssignmentOperator \
                                    AssignmentExpression"""
        print "AssignmentExpression: ", list(p)
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.Assign(node=p[1], operator=p[2], expression=p[3])
                                
    def p_AssignmentExpressionNoIn(self, p):
        """AssignmentExpressionNoIn : ConditionalExpressionNoIn
                                    | LeftHandSideExpression \
                                        AssignmentOperator \
                                        AssignmentExpressionNoIn"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.Assign(node=p[1], operator=p[2], expression=p[3])

    def p_AssignmentExpressionNoBF(self, p):
        """AssignmentExpressionNoBF : ConditionalExpressionNoBF
                                    | LeftHandSideExpressionNoBF AssignmentOperator \
                                        AssignmentExpression"""
        print "AssignmentExpressionNoBF: ", list(p)
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.Assign(node=p[1], operator=p[2], expression=p[3])
            

    def p_AssignmentOperator(self, p):
        """AssignmentOperator : EQUALS
                              | TIMES_EQUALS
                              | DIVIDE_EQUALS
                              | MOD_EQUALS
                              | PLUS_EQUALS
                              | MINUS_EQUALS
                              | LSHIFT_EQUALS
                              | RSHIFT_EQUALS
                              | URSHIFT_EQUALS
                              | AND_EQUALS
                              | XOR_EQUALS
                              | OR_EQUALS"""
        print "AssignmentOperator: ", list(p)
        p[0] = p[1]

    # 11.14 Comma Operator ( , )
    def p_Expression(self, p):
        """Expression : AssignmentExpression
                      | Expression COMMA AssignmentExpression"""
        print "Expression: ", list(p)
        if len(p) == 2:
            p[0] = p[1]

    def p_ExpressionNoIn(self, p):
        """ExpressionNoIn : AssignmentExpressionNoIn
                          | ExpressionNoIn COMMA AssignmentExpressionNoIn"""
        print "ExpressionNoIn: ", list(p)
        if len(p) == 2:
            p[0] = p[1]

    def p_ExpressionNoBF(self, p):
        """ExpressionNoBF : AssignmentExpressionNoBF
                          | ExpressionNoBF COMMA AssignmentExpression"""
        print "ExpressionNoBF: ", list(p)
        if len(p) == 2:
            p[0] = p[1]


    # 12 Statements
    #
    def p_Statement(self, p):
        """Statement : Block
                     | VariableStatement
                     | EmptyStatement
                     | ExpressionStatement
                     | IfStatement 
                     | IterationStatement 
                     | ContinueStatement
                     | BreakStatement 
                     | ReturnStatement 
                     | WithStatement 
                     | LabelledStatement 
                     | SwitchStatement 
                     | ThrowStatement 
                     | TryStatement 
                     | DebuggerStatement"""
        print "Statement: ", list(p)
        p[0] = p[1]
        
    # 12.1 Block
    def p_Block(self, p):
        """Block : LBRACE StatementList_opt RBRACE"""
        print "Block: ", list(p)
        p[0] = p[2]

    def p_StatementList(self, p):
        """StatementList : Statement
                         | StatementList Statement"""
        print "StatementList: ", list(p)
        p[0] = self.build_list(p, 1, 2)
            
    # 12.2 Variable Statement
    def p_VariableStatement(self, p):
        """VariableStatement : VAR VariableDeclarationList SEMI
                             | VAR VariableDeclarationList auto_semicolon"""
        print "VariableStatement: ", list(p)
        p[0] = []
        for node, expression in p[2]:
            p[0].append(ast.VariableDeclaration(node, expression))
        
    def p_VariableDeclarationList(self, p):
        """VariableDeclarationList : VariableDeclaration
                                   | VariableDeclarationList COMMA \
                                        VariableDeclaration"""
        p[0] = self.build_list(p, 1, 3)
            
    def p_VariableDeclarationListNoIn(self, p):
        """VariableDeclarationListNoIn : VariableDeclarationNoIn 
                                       | VariableDeclarationListNoIn COMMA \
                                            VariableDeclarationNoIn """
        p[0] = self.build_list(p, 1, 3)

    def p_VariableDeclaration(self, p):
        """VariableDeclaration : Identifier Initialiser_opt"""
        p[0] = (p[1], p[2])
        
    def p_VariableDeclarationNoIn(self, p):
        """VariableDeclarationNoIn : Identifier InitialiserNoIn_opt"""
        p[0] = (p[1], p[2])

    def p_Initialiser(self, p):
        """Initialiser : EQUALS AssignmentExpression"""
        p[0] = p[2]
        
    def p_InitialiserNoIn(self, p):
        """InitialiserNoIn : EQUALS AssignmentExpressionNoIn"""
        p[0] = p[2]

    # 12.3 Empty Statement
    def p_EmptyStatement(self, p):
        """EmptyStatement : SEMI"""

    # 12.4 Expression Statement
    def p_ExpressionStatement(self, p):
        """ExpressionStatement : ExpressionNoBF SEMI
                               | ExpressionNoBF auto_semicolon"""
        p[0] = p[1]

    # 12.5 The if Statement
    def p_IfStatement(self, p):
        """IfStatement : IF LPAREN Expression RPAREN Statement %prec IF_WITHOUT_ELSE 
                       | IF LPAREN Expression RPAREN Statement ELSE Statement"""
        p[0] = ast.If(expression=p[3], true=p[5],
                      false=p[7] if len(p) > 6 else None)

    # 12.6 Iteration Statements   
    def p_IterationStatement_1(self, p):
        """IterationStatement : DO Statement WHILE LPAREN Expression RPAREN \
                                SEMI"""
        p[0] = ast.DoWhile(condition=p[5], statement=p[2])
        
    def p_IterationStatement_2(self, p):
        """IterationStatement : WHILE LPAREN Expression RPAREN Statement"""
        p[0] = ast.While(condition=p[3], statement=p[5])
        
    def p_IterationStatement_3(self, p):
        """IterationStatement : FOR LPAREN ExpressionNoIn_opt SEMI \
                                    Expression_opt SEMI \
                                    Expression_opt RPAREN Statement
                              | FOR LPAREN VAR VariableDeclarationListNoIn SEMI \
                                    Expression_opt SEMI Expression_opt RPAREN \
                                    Statement"""
        if len(p) == 10:
            p[0] = ast.For(initialisers=p[3], conditions=p[5], increments=p[7],
                           statement=p[9])
        else:
            initialisers = [ast.VariableDeclaration(node, expression)
                            for (node, expression) in p[4]]
            p[0] = ast.For(initialisers=initialisers, conditions=p[6],
                           increments=p[8], statement=p[10])
        
    def p_IterationStatement_4(self, p):
        """IterationStatement : FOR LPAREN LeftHandSideExpression IN \
                                    Expression RPAREN Statement
                              | FOR LPAREN VAR VariableDeclarationNoIn IN \
                                    Expression RPAREN Statement"""
        if len(p) == 7:
            p[0] = ast.ForIn(item=p[3], iterator=p[5], statement=p[7])
        else:
            item = ast.VariableDeclaration(p[4], None)
            p[0] = ast.ForIn(item=item, iterator=p[6], statement=p[8])
        

    # 12.7 The continue Statement
    def p_ContinueStatement(self, p):
        """ContinueStatement : CONTINUE Identifier_opt SEMI"""
        p[0] = ast.Continue(identifier=p[2])

    # 12.8 The break Statement
    def p_BreakStatement(self, p):
        """BreakStatement : BREAK Identifier_opt SEMI"""
        p[0] = ast.Break(identifier=p[2])

    # 12.9 The return Statement
    def p_ReturnStatement(self, p):
        """ReturnStatement : RETURN Expression_opt SEMI
                           | RETURN Expression_opt auto_semicolon"""
        p[0] = ast.Return(expression=p[2])

    # 12.10 The with Statement
    def p_WithStatement(self, p):
        """WithStatement : WITH LPAREN Expression RPAREN Statement"""
        p[0] = ast.With(expression=p[3], statement=p[5])

    # 12.11 The switch Statement
    def p_SwitchStatement(self, p):
        """SwitchStatement : SWITCH LPAREN Expression RPAREN CaseBlock"""
        cases = []
        default = None
        for item in p[5]:
            if isinstance(item, list):
                cases.extend(item)
            else:
                default = item
        p[0] = ast.Switch(p[3], cases=cases, default=default)
                
     
    def p_CaseBlock(self, p):
        """CaseBlock : LBRACE CaseClauses_opt RBRACE
                     | LBRACE CaseClauses_opt DefaultClause CaseClauses_opt RBRACE"""
                     
        p[0] = p[2:-1]

    def p_CaseClauses(self, p):
        """CaseClauses : CaseClause
                       | CaseClauses CaseClause"""
        p[0] = self.build_list(p, 1, 2)

    def p_CaseClause(self, p):
        """CaseClause : CASE Expression COLON StatementList_opt"""
        p[0] = ast.Case(identifier=p[2], statements=p[4])
        
    def p_DefaultClause(self, p):
        """DefaultClause : DEFAULT COLON StatementList_opt"""
        p[0] = ast.DefaultCase(identifier=p[1], statements=p[3])
        
    # 12.12 Labelled Statements
    def p_LabelledStatement(self, p):
        """LabelledStatement : Identifier COLON Statement"""
        p[0] = ast.LabelledStatement(identifier=p[1], statement=p[2])

    # 12.13 The throw Statement
    def p_ThrowStatement(self, p):
        """ThrowStatement : THROW Expression SEMI"""
        p[0] = ast.Throw(expression=p[2])

    # 12.14 The try Statement
    def p_TryStatement_1(self, p):
        """TryStatement : TRY Block Catch"""
        p[0] = ast.Try(statements=p[2], catch=p[3], finally_=None)

    def p_TryStatement_2(self, p):
        """TryStatement : TRY Block Finally
                        | TRY Block Catch Finally"""
        if len(p) == 4:
            p[0] = ast.Try(statements=p[2], catch=None, finally_=p[3])
        else:
            p[0] = ast.Try(statements=p[2], catch=p[3], finally_=p[4])

        
    def p_Catch(self, p):
        """Catch : CATCH LPAREN Identifier RPAREN Block"""
        p[0] = ast.Catch(identifier=p[3], statements=p[5])
            
    def p_Finally(self, p):
        """Finally : FINALLY Block"""
        p[0] = ast.Finally(statements=p[2])
        
    # 12.15 Debugger statement
    def p_DebuggerStatement(self, p):
        """DebuggerStatement : DEBUGGER SEMI"""
        print "DebuggerStatement: ", list(p)

    #
    # 13. Function Definition

    def p_FunctionDeclaration(self, p):
        """FunctionDeclaration : FUNCTION Identifier \
                                    LPAREN FormalParameterList_opt RPAREN \
                                    LBRACE FunctionBody RBRACE"""
        p[0] = ast.FuncDecl(p[1], p[4], p[7])
        
    def p_FunctionExpression(self, p):
        """FunctionExpression : FUNCTION Identifier_opt \
                                    LPAREN FormalParameterList_opt RPAREN \
                                    LBRACE FunctionBody RBRACE """
        if len(p) == 9:
            p[0] = ast.FuncDecl(name=p[2], parameters=p[4], statements=p[7])
        elif len(p) == 8 and p[3] == '(':
            p[0] = ast.FuncDecl(name=None, parameters=p[2], statements=p[6])
        else:
            p[0] = ast.FuncDecl(name=None, parameters=p[3], statements=p[6])
        
    def p_FormalParameterList(self, p):
        """FormalParameterList : Identifier
                               | FormalParameterList COMMA Identifier"""
        p[0] = self.build_list(p, 1, 3)
            
    def p_FunctionBody(self, p):
        """FunctionBody : SourceElements_opt"""
        p[0] = p[1]
    
    #
    # 14. Program
    
    def p_Program(self, p):
        """Program : SourceElements_opt"""
        p[0] = ast.Program(p[1])

    def p_SourceElements(self, p):
        """SourceElements : SourceElement
                          | SourceElements SourceElement"""
        p[0] = self.build_list(p, 1, 2)
        
        
    def p_SourceElement(self, p):
        """SourceElement : Statement
                         | FunctionDeclaration
                         | Comment """
        p[0] = p[1]

    # TODO UseStrictDirective
    
    # TODO useExtension
    
    # TODO ArbitraryInputElements



class NodeVisitor(object):
    
    def __init__(self):
        self.level = 0
        
    def get_visitor(self, node):
        method = 'visit_' + node.__class__.__name__
        return getattr(self, method, None)
        
    def visit(self, node):
        self.level +=  1
        
        print "%s %r" % (self.level * '    ', node)
        visitor = self.get_visitor(node)
        if visitor is not None:
            result = visitor(Node)
        else:
            result = self.generic_visit(node)
        self.level -= 1
        return result
    
    def generic_visit(self, node):
            
        try:
            for child in node:
                if isinstance(child, list):
                    for subchild in child:
                        if isinstance(subchild, ast.Node):
                            self.visit(subchild)
                        else:
                            self.generic_visit(subchild)
                elif isinstance(child, ast.Node):
                    self.visit(child)
        except TypeError:
            print "Unable to visit: ", node
        
                
     
    
if __name__ == "__main__":
    input = r"""
    var quicktest = {
        test: function() {
            return 1;
            funccall();
        }
    }
    """
    
    parser = Parser()
    output = parser.parse(input)
    print ">>>>>", output
    walker = NodeVisitor()
    walker.visit(output)
