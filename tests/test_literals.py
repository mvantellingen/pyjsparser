from pyjsparser.parser import Parser

def test_number_simple():
    input = """
        1;
        1000;
        1000.0020;
        -100200.20;
        +1002010.2
    """
    parser = Parser()
    program = parser.parse(input)
    
def test_number_complex():
    input = """
        .100e1;
        .2e00;
        .2023e1;
        2.e10;
        1000.23e0;
        100e10;
    """
    parser = Parser()
    program = parser.parse(input)
    

def test_string():
    input = """
    "foo ";
    "foo\"bar";
    'bar';
    'foo\'b ar';
    'foo\' \'\' b"ar\'\'"\'"\'"';
    """
    parser = Parser()
    program = parser.parse(input)


def test_regex():
    input = """
    /foo/ai;
    foo = /bar/;
    /foo/
    {true?(pf(el.match(/op=([^)]*)/)[1])/100)+'':"";}np=np.repl(/-([a-z])/ig)
    """
    parser = Parser()
    program = parser.parse(input)
    

