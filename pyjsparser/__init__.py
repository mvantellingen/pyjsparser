from pyjsparser import ast, parser

def parse(file):
    p = parser.Parser()
    fh = open(file)
    return p.parse(fh.read())
    
def dump(node):
    walker = ast.NodeVisitor()
    walker.visit(node)
 