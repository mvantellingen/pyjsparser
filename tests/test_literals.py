from pyjsparser.parser import Parser

def test_comments():
    input = r"""
    // line comment
    /* foo /* foo
     *
     */
    """
    parser = Parser()
    program = parser.parse(input)

def test_null():
    input = """
        var p = null;
        null;
    """
    parser = Parser()
    program = parser.parse(input)
        
def test_number_simple():
    input = r"""
        1;
        1000;
        1000.0020;
        -100200.20;
        +1002010.2
    """
    parser = Parser()
    program = parser.parse(input)

def test_number_hex():
    input = r"""
        0xabcdef
        0XAbEfC
    """
    parser = Parser()
    program = parser.parse(input)


def test_number_complex():
    input = r"""
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
    input = r"""
    "foo ";
    "foo\"zar";
    'xar';
    'foo\'b ar';
    'foo\' \'\' b"ar\'\'"\'"\'"';
    "<" + ("div");
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
    

def test_object():
    input = r"""
    var obj = {
        foo: 10,
        bar: 20
    };
    obj.foo;
    """
    parser = Parser()
    program = parser.parse(input)
    
def test_array():
    input = r"""
    var p = [1, 2, 3, 4]
    p[1]
    
    // elision
    var p = [,]
    """
    parser = Parser()
    program = parser.parse(input)
    