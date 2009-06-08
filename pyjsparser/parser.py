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

    # Internal helpers
    def p_empty(self, p):
        """empty :"""
        
    def p_error(self, p):
        print p.lineno, p.lexpos
        raise SyntaxError("invalid syntax : %r " % p)


    #
    # 7. Lexical Conventions
    # Only some are implemented currently, see lexer for more

    # 7.4 Comments    
    def p_Comment(self, p):
        """Comment : SingleLineComment
                   | MultiLineComment """

    def p_SingleLineComment(self, p):
        """SingleLineComment : COMMENT"""

    def p_MultiLineComment(self, p):
        """MultiLineComment : BLOCK_COMMENT"""


    def p_IdentifierName(self, p):
        """IdentifierName : Identifier"""
                                    
    def p_Identifier(self, p):
        """Identifier : ID"""

    # TODO: Note that the RegularExpressionLiteral doesn't belong here
    # according to the ecmascript standard
    def p_Literal(self, p):
        """Literal : NullLiteral
                   | BooleanLiteral
                   | NumericLiteral
                   | StringLiteral
                   | RegularExpressionLiteral"""

    def p_NullLiteral(self, p):
        """NullLiteral : NULL """

    def p_BooleanLiteral(self, p):
        """BooleanLiteral : TRUE
                          | FALSE"""

    # TODO
    def p_NumericLiteral(self, p):
        """NumericLiteral : INTEGER"""
        
    def p_StringLiteral(self, p):
        """StringLiteral : STRING_LITERAL"""

    def p_RegularExpressionLiteral(self, p):
        """RegularExpressionLiteral : REGEX"""
    #
    # 11. Expressions

    # 11.1 Primary Expressions
    def p_PrimaryExpression(self, p):
        """PrimaryExpression : PrimaryExpressionNoObj
                             | ObjectLiteral"""

    def p_PrimaryExpressionNoObj(self, p):
        """PrimaryExpressionNoObj : THIS
                                  | Identifier
                                  | Literal
                                  | ArrayLiteral
                                  | LPAREN Expression RPAREN"""

    def p_ArrayLiteral(self, p):
        """ArrayLiteral : LBRACKET Elision_opt RBRACKET
                        | LBRACKET ElementList RBRACKET
                        | LBRACKET ElementList COMMA Elision_opt RBRACKET"""

    def p_ElementList(self, p):
        """ElementList : Elision_opt AssignmentExpression
                       | ElementList COMMA Elision_opt AssignmentExpression """ 

    def p_Elision(self, p):
        """Elision : COMMA
                   | Elision COMMA"""

    def p_ObjectLiteral(self, p):
        """ObjectLiteral : LBRACE RBRACE
                         | LBRACE PropertyNameAndValueList RBRACE
                         | LBRACE PropertyNameAndValueList COMMA RBRACE"""
                         
    def p_PropertyNameAndValueList(self, p):
        """PropertyNameAndValueList : PropertyAssignment 
                                    | PropertyNameAndValueList COMMA PropertyAssignment"""

    # Todo add get / set 
    def p_PropertyAssignment(self, p):
        """PropertyAssignment : PropertyName COLON AssignmentExpression
                              | GET PropertyName \
                                    LPAREN RPAREN \
                                    LBRACE FunctionBody RBRACE
                              | SET PropertyName \
                                    LPAREN PropertySetParameterList RPAREN \
                                    LBRACE FunctionBody RBRACE """

    def p_PropertyName(self, p):
        """PropertyName : IdentifierName
                        | StringLiteral 
                        | NumericLiteral"""

    def p_PropertySetParameterList(self, p):
        """PropertySetParameterList : Identifier """
        
    # 11.2 Left-Hand-Side Expressions
    def p_MemberExpression(self, p):
        """MemberExpression : PrimaryExpression
                            | FunctionExpression 
                            | MemberExpression LBRACKET Expression RBRACKET
                            | MemberExpression PERIOD IdentifierName 
                            | NEW MemberExpression Arguments """

    def p_MemberExpressionNoBF(self, p):
        """MemberExpressionNoBF : PrimaryExpressionNoObj 
                                | MemberExpressionNoBF LBRACKET Expression RBRACKET
                                | MemberExpressionNoBF PERIOD IdentifierName 
                                | NEW MemberExpression Arguments """

    def p_NewExpression(self, p):
        """NewExpression : MemberExpression
                         | NEW NewExpression"""

    def p_NewExpressionNoBF(self, p):
        """NewExpressionNoBF : MemberExpressionNoBF
                             | NEW NewExpression"""

    def p_CallExpression(self, p):
        """CallExpression : MemberExpression Arguments
                          | CallExpression Arguments
                          | CallExpression LBRACKET Expression RBRACKET
                          | CallExpression PERIOD IdentifierName"""

    def p_CallExpressionNoBF(self, p):
        """CallExpressionNoBF : MemberExpressionNoBF Arguments
                              | CallExpressionNoBF Arguments
                              | CallExpressionNoBF LBRACKET Expression RBRACKET
                              | CallExpressionNoBF PERIOD IdentifierName"""

    def p_Arguments(self, p):
        """Arguments : LPAREN RPAREN
                     | LPAREN ArgumentList RPAREN"""

    def p_ArgumentList(self, p):
        """ArgumentList : AssignmentExpression
                        | ArgumentList COMMA AssignmentExpression"""


                             
    def p_LeftHandSideExpression(self, p):
        """LeftHandSideExpression : NewExpression
                                  | CallExpression """

    def p_LeftHandSideExpressionNoBF(self, p):
        """LeftHandSideExpressionNoBF : NewExpressionNoBF
                                      | CallExpressionNoBF """
    
    # 11.3 Postfix Expressions
    def p_PostfixExpression(self, p): 
        """PostfixExpression : LeftHandSideExpression
                             | LeftHandSideExpression INCR_LBREAK 
                             | LeftHandSideExpression DECR_LBREAK """

    def p_PostfixExpressionNoBF(self, p): 
        """PostfixExpressionNoBF : LeftHandSideExpressionNoBF
                                 | LeftHandSideExpressionNoBF INCR_LBREAK 
                                 | LeftHandSideExpressionNoBF DECR_LBREAK """



    # 11.4 Unary Operators
    def p_UnaryExpressionCommon(self, p):
        """UnaryExpressionCommon : DELETE UnaryExpression 
                                 | VOID UnaryExpression 
                                 | TYPEOF UnaryExpression 
                                 | INCR UnaryExpression 
                                 | DECR UnaryExpression 
                                 | PLUS UnaryExpression 
                                 | MINUS UnaryExpression   
                                 | NOT UnaryExpression 
                                 | LNOT UnaryExpression """
                           
    def p_UnaryExpression(self, p):
        """UnaryExpression : PostfixExpression
                           | UnaryExpressionCommon"""
                           
    def p_UnaryExpressionNoBF(self, p):
        """UnaryExpressionNoBF : PostfixExpressionNoBF
                               | UnaryExpressionCommon"""

    # 11.5 Multiplicative Operators
    def p_MultiplicativeExpression(self, p):
        """MultiplicativeExpression : UnaryExpression 
                                    | MultiplicativeExpression TIMES UnaryExpression 
                                    | MultiplicativeExpression DIVIDE UnaryExpression 
                                    | MultiplicativeExpression MOD UnaryExpression """

    def p_MultiplicativeExpressionNoBF(self, p):
        """MultiplicativeExpressionNoBF : UnaryExpressionNoBF 
                                        | MultiplicativeExpressionNoBF TIMES UnaryExpression 
                                        | MultiplicativeExpressionNoBF DIVIDE UnaryExpression 
                                        | MultiplicativeExpressionNoBF MOD UnaryExpression """

    # 11.6 Additive Operators
    def p_AdditiveExpression(self, p):
        """AdditiveExpression : MultiplicativeExpression 
                              | AdditiveExpression PLUS MultiplicativeExpression 
                              | AdditiveExpression MINUS MultiplicativeExpression"""

    def p_AdditiveExpressionNoBF(self, p):
        """AdditiveExpressionNoBF : MultiplicativeExpressionNoBF
                                  | AdditiveExpressionNoBF PLUS MultiplicativeExpression 
                                  | AdditiveExpressionNoBF MINUS MultiplicativeExpression"""

    # 11.7 Bitwise Shift Operators
    def p_ShiftExpression(self, p):
        """ShiftExpression : AdditiveExpression 
                           | ShiftExpression LSHIFT AdditiveExpression 
                           | ShiftExpression RSHIFT AdditiveExpression 
                           | ShiftExpression URSHIFT AdditiveExpression"""

    def p_ShiftExpressionNoBF(self, p):
        """ShiftExpressionNoBF : AdditiveExpressionNoBF 
                               | ShiftExpressionNoBF LSHIFT AdditiveExpression 
                               | ShiftExpressionNoBF RSHIFT AdditiveExpression 
                               | ShiftExpressionNoBF URSHIFT AdditiveExpression"""

    # 11.8 Relational Operators
    def p_RelationalExpression(self, p):
        """RelationalExpression : ShiftExpression 
                                | RelationalExpression GT ShiftExpression 
                                | RelationalExpression LT ShiftExpression 
                                | RelationalExpression GE ShiftExpression 
                                | RelationalExpression LE ShiftExpression 
                                | RelationalExpression INSTANCEOF ShiftExpression 
                                | RelationalExpression IN ShiftExpression"""

    def p_RelationalExpressionNoIn(self, p):
        """RelationalExpressionNoIn : ShiftExpression 
                                    | RelationalExpressionNoIn GT ShiftExpression 
                                    | RelationalExpressionNoIn LT ShiftExpression 
                                    | RelationalExpressionNoIn GE ShiftExpression 
                                    | RelationalExpressionNoIn LE ShiftExpression 
                                    | RelationalExpressionNoIn INSTANCEOF ShiftExpression"""

    def p_RelationalExpressionNoBF(self, p):
        """RelationalExpressionNoBF : ShiftExpressionNoBF
                                    | RelationalExpressionNoBF GT ShiftExpression 
                                    | RelationalExpressionNoBF LT ShiftExpression 
                                    | RelationalExpressionNoBF GE ShiftExpression 
                                    | RelationalExpressionNoBF LE ShiftExpression 
                                    | RelationalExpressionNoBF INSTANCEOF ShiftExpression
                                    | RelationalExpressionNoBF IN ShiftExpression"""


    # 11.9 Equality Operators
    def p_EqualityExpression(self, p):
        """EqualityExpression : RelationalExpression 
                              | EqualityExpression EQ RelationalExpression 
                              | EqualityExpression NE RelationalExpression 
                              | EqualityExpression EQT RelationalExpression 
                              | EqualityExpression NET RelationalExpression"""

    def p_EqualityExpressionNoIn(self, p):
        """EqualityExpressionNoIn : RelationalExpressionNoIn 
                                  | EqualityExpressionNoIn EQ RelationalExpressionNoIn 
                                  | EqualityExpressionNoIn NE RelationalExpressionNoIn 
                                  | EqualityExpressionNoIn EQT RelationalExpressionNoIn 
                                  | EqualityExpressionNoIn NET RelationalExpressionNoIn"""

    def p_EqualityExpressionNoBF(self, p):
        """EqualityExpressionNoBF : RelationalExpressionNoBF 
                                  | EqualityExpressionNoBF EQ RelationalExpressionNoIn 
                                  | EqualityExpressionNoBF NE RelationalExpressionNoIn 
                                  | EqualityExpressionNoBF EQT RelationalExpressionNoIn 
                                  | EqualityExpressionNoBF NET RelationalExpressionNoIn"""


    # 11.10 Binary Bitwise Operators
    def p_BitwiseANDExpression(self, p):
        """BitwiseANDExpression : EqualityExpression 
                                | BitwiseANDExpression AND EqualityExpression"""

    def p_BitwiseANDExpressionNoIn(self, p):                            
        """BitwiseANDExpressionNoIn : EqualityExpressionNoIn 
                                    | BitwiseANDExpressionNoIn AND EqualityExpressionNoIn"""

    def p_BitwiseANDExpressionNoBF(self, p):                            
        """BitwiseANDExpressionNoBF : EqualityExpressionNoBF
                                    | BitwiseANDExpressionNoBF AND EqualityExpressionNoIn"""

    def p_BitwiseXORExpression(self, p):                                
        """BitwiseXORExpression : BitwiseANDExpression 
                                | BitwiseXORExpression XOR BitwiseANDExpression """

    def p_BitwiseXORExpressionNoIn(self, p):                            
        """BitwiseXORExpressionNoIn : BitwiseANDExpressionNoIn 
                                    | BitwiseXORExpressionNoIn XOR BitwiseANDExpressionNoIn """

    def p_BitwiseXORExpressionNoBF(self, p):                            
        """BitwiseXORExpressionNoBF : BitwiseANDExpressionNoBF
                                    | BitwiseXORExpressionNoBF XOR BitwiseANDExpressionNoIn """
                                    
    def p_BitwiseORExpression(self, p):
        """BitwiseORExpression : BitwiseXORExpression 
                               | BitwiseORExpression OR BitwiseXORExpression """

    def p_BitwiseORExpressionNoIn(self, p):                        
        """BitwiseORExpressionNoIn : BitwiseXORExpressionNoIn 
                                   | BitwiseORExpressionNoIn OR BitwiseXORExpressionNoIn"""

    def p_BitwiseORExpressionNoBF(self, p):                        
        """BitwiseORExpressionNoBF : BitwiseXORExpressionNoBF 
                                   | BitwiseORExpressionNoBF OR BitwiseXORExpressionNoIn"""

    # 11.11 Binary Logical Operators
    def p_LogicalANDExpression(self, p):
        """LogicalANDExpression : BitwiseORExpression 
                                | LogicalANDExpression LAND BitwiseORExpression"""

    def p_LogicalANDExpressionNoIn(self, p):
        """LogicalANDExpressionNoIn : BitwiseORExpressionNoIn
                                    | LogicalANDExpressionNoIn LAND BitwiseORExpressionNoIn """

    def p_LogicalANDExpressionNoBF(self, p):
        """LogicalANDExpressionNoBF : BitwiseORExpressionNoBF
                                    | LogicalANDExpressionNoBF LAND BitwiseORExpressionNoIn """

    def p_LogicalORExpression(self, p):
        """LogicalORExpression : LogicalANDExpression
                               | LogicalORExpression LOR LogicalANDExpression """

    def p_LogicalORExpressionNoIn(self, p):
        """LogicalORExpressionNoIn : LogicalANDExpressionNoIn 
                                   | LogicalORExpressionNoIn LOR LogicalANDExpressionNoIn """

    def p_LogicalORExpressionNoBF(self, p):
        """LogicalORExpressionNoBF : LogicalANDExpressionNoBF 
                                   | LogicalORExpressionNoBF LOR LogicalANDExpressionNoIn """

    # 11.12 Conditional Operator ( ?: )                                 
    def p_ConditionalExpression(self, p):
        """ConditionalExpression : LogicalORExpression 
                                 | LogicalORExpression CONDOP AssignmentExpression COLON AssignmentExpression """

    def p_ConditionalExpressionNoIn(self, p):                             
        """ConditionalExpressionNoIn : LogicalORExpressionNoIn 
                                     | LogicalORExpressionNoIn CONDOP AssignmentExpression COLON AssignmentExpressionNoIn"""

    def p_ConditionalExpressionNoBF(self, p):
        """ConditionalExpressionNoBF : LogicalORExpressionNoBF 
                                     | LogicalORExpressionNoBF CONDOP AssignmentExpression COLON AssignmentExpression """


    # 11.13 Assignment Operators
    def p_AssignmentExpression(self, p):
        """AssignmentExpression : ConditionalExpression
                                | LeftHandSideExpression AssignmentOperator \
                                    AssignmentExpression"""
                                
    def p_AssignmentExpressionNoIn(self, p):
        """AssignmentExpressionNoIn : ConditionalExpressionNoIn
                                    | LeftHandSideExpression \
                                        AssignmentOperator \
                                        AssignmentExpressionNoIn"""

    def p_AssignmentExpressionNoBF(self, p):
        """AssignmentExpressionNoBF : ConditionalExpressionNoBF
                                    | LeftHandSideExpressionNoBF AssignmentOperator \
                                        AssignmentExpression"""

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
                              | NOT_EQUALS
                              | OR_EQUALS"""

    # 11.14 Comma Operator ( , )
    def p_Expression(self, p):
        """Expression : AssignmentExpression
                      | Expression COMMA AssignmentExpression"""

    def p_ExpressionNoIn(self, p):
        """ExpressionNoIn : AssignmentExpressionNoIn
                          | ExpressionNoIn COMMA AssignmentExpressionNoIn"""

    def p_ExpressionNoBF(self, p):
        """ExpressionNoBF : AssignmentExpressionNoBF
                          | ExpressionNoBF COMMA AssignmentExpression"""


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

    # 12.1 Block
    def p_Block(self, p):
        """Block : LBRACE StatementList_opt RBRACE"""

    def p_StatementList(self, p):
        """StatementList : Statement
                         | StatementList Statement"""

    # 12.2 Variable Statement
    def p_VariableStatement(self, p):
        """VariableStatement : VAR VariableDeclarationList SEMI"""

    def p_VariableDeclarationList(self, p):
        """VariableDeclarationList : VariableDeclaration
                                   | VariableDeclarationList COMMA \
                                        VariableDeclaration"""

    def p_VariableDeclarationListNoIn(self, p):
        """VariableDeclarationListNoIn : VariableDeclarationNoIn 
                                       | VariableDeclarationListNoIn COMMA \
                                            VariableDeclarationNoIn """

    def p_VariableDeclaration(self, p):
        """VariableDeclaration : Identifier Initialiser_opt"""
        
    def p_VariableDeclarationNoIn(self, p):
        """VariableDeclarationNoIn : Identifier InitialiserNoIn_opt"""

    def p_Initialiser(self, p):
        """Initialiser : EQUALS AssignmentExpression"""

    def p_InitialiserNoIn(self, p):
        """InitialiserNoIn : EQUALS AssignmentExpressionNoIn"""

    # 12.3 Empty Statement
    def p_EmptyStatement(self, p):
        """EmptyStatement : SEMI"""

    # 12.4 Expression Statement
    def p_ExpressionStatement(self, p):
        """ExpressionStatement : ExpressionNoBF SEMI"""

    # 12.5 The if Statement
    def p_IfStatement(self, p):
        """IfStatement : IF LPAREN Expression RPAREN Statement ELSE Statement
                       | IF LPAREN Expression RPAREN Statement"""

    # 12.6 Iteration Statements   
    def p_IterationStatement(self, p):
        """IterationStatement : DO Statement WHILE LPAREN Expression RPAREN SEMI
                              | WHILE LPAREN Expression RPAREN Statement 
                              | FOR LPAREN ExpressionNoIn_opt SEMI \
                                    Expression_opt SEMI \
                                    Expression_opt RPAREN Statement
                              | FOR LPAREN VAR VariableDeclarationListNoIn SEMI \
                                    Expression_opt SEMI Expression_opt RPAREN \
                                    Statement
                              | FOR LPAREN LeftHandSideExpression IN \
                                    Expression RPAREN Statement
                              | FOR LPAREN VAR VariableDeclarationNoIn IN \
                                    Expression RPAREN Statement"""

    # 12.7 The continue Statement
    def p_ContinueStatement(self, p):
        """ContinueStatement : CONTINUE Identifier_opt SEMI"""
        # TODO No line terminator

    # 12.8 The break Statement
    def p_BreakStatement(self, p):
        """BreakStatement : BREAK Identifier_opt SEMI"""
        # TODO No line terminator

    # 12.9 The return Statement
    def p_ReturnStatement(self, p):
        """ReturnStatement : RETURN Expression_opt SEMI"""
        # TODO No line terminator

    # 12.10 The with Statement
    def p_WithStatement(self, p):
        """WithStatement : WITH LPAREN Expression RPAREN Statement"""

    # 12.11 The switch Statement
    def p_SwitchStatement(self, p):
        """SwitchStatement : SWITCH LPAREN Expression RPAREN CaseBlock"""

    def p_CaseBlock(self, p):
        """CaseBlock : LBRACE CaseClauses_opt RBRACE
                     | LBRACE CaseClauses_opt DefaultClause CaseClauses_opt RBRACE"""

    def p_CaseClauses(self, p):
        """CaseClauses : CaseClause
                       | CaseClauses CaseClause"""

    def p_CaseClause(self, p):
        """CaseClause : CASE Expression COLON StatementList_opt"""
        
    def p_DefaultClause(self, p):
        """DefaultClause : DEFAULT COLON StatementList_opt"""

    # 12.12 Labelled Statements
    def p_LabelledStatement(self, p): # 3 shift/reducs
        """LabelledStatement : Identifier COLON Statement"""

    # 12.13 The throw Statement
    def p_ThrowStatement(self, p):
        """ThrowStatement : THROW Expression SEMI"""
        # todo No lineterminator here

    # 12.14 The try Statement
    def p_TryStatement(self, p):
        """TryStatement : TRY Block Catch
                        | TRY Block Finally
                        | TRY Block Catch Finally"""

    def p_Catch(self, p):
        """Catch : CATCH LPAREN Identifier RPAREN Block"""

    def p_Finally(self, p):
        """Finally : FINALLY Block"""

    # 12.15 Debugger statement
    def p_DebuggerStatement(self, p):
        """DebuggerStatement : DEBUGGER SEMI"""

    #
    # 13. Function Definition

    def p_FunctionDeclaration(self, p):
        """FunctionDeclaration : FUNCTION Identifier \
                                    LPAREN FormalParameterList_opt RPAREN \
                                    LBRACE FunctionBody RBRACE"""

    def p_FunctionExpression(self, p):
        """FunctionExpression : FUNCTION Identifier_opt \
                                    LPAREN FormalParameterList_opt RPAREN \
                                    LBRACE FunctionBody RBRACE """

    def p_FormalParameterList(self, p):
        """FormalParameterList : Identifier
                               | FormalParameterList COMMA Identifier"""

    def p_FunctionBody(self, p):
        """FunctionBody : SourceElements_opt"""
    
    #
    # 14. Program
    
    def p_Program(self, p):
        """Program : SourceElements_opt"""

    def p_SourceElements(self, p):
        """SourceElements : SourceElement
                          | SourceElements SourceElement"""
    
    def p_SourceElement(self, p):
        """SourceElement : Statement
                         | FunctionDeclaration
                         | Comment """
        
    # TODO UseStrictDirective
    
    # TODO useExtension
    
    # TODO ArbitraryInputElements
    
    
if __name__ == "__main__":
    input = r"""
    """
    parser = Parser()
    output = parser.parse(input)
    print ">>>>>>>>>", output
