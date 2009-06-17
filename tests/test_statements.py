from pyjsparser.parser import Parser

def test_if():
    input = """
        if (true)
            var p = 100;
        
        if (true) {
            var p = 100;
            var z = 200;
        }
        
        if (true)
            if (true)
                var p = 100;
            else
                var p = 200;
        
        if (true) {
            var p = 1000;
        }
        else {
            var z = 200;
        }

    """
    parser = Parser()
    program = parser.parse(input)
   
def test_iteration():
    input = """
    for(var i=0; i < 20; i++) {
        p = 100 * i;
    }
    
    for(i = 100; i > 0; i++) {
        p = 1000-i;
    }
    
    for (var i=0, p=0; i < 10 || p < 9; i++, p++) {
        a = i*p;
    }
    
    for (var p in object) {
        p = 100;
    }
    
    for (p in object) {
        p = 200;
    }
    
    do {
        p = 100;
    } while(false);
    
    while(false) {
        p = 200;
    }

    """
    parser = Parser()
    program = parser.parse(input)
    

def test_switch():
    input = """
    switch(100) {
        case 99:
        case 98: {
            false;
            break;
        }
        default: {
            break;
        }
        case 100: {
            var found=true;
            break;
        }
        case 101: {
            found=true;
            /* fall-through */
        }
        case 102: {
            found=false;
            break;
        }
    }
    """
    parser = Parser()
    program = parser.parse(input)
    
def test_continue():
    input = """
    while(true) {
        continue;
        notreached = true;
    }
    """
    parser = Parser()
    program = parser.parse(input)
    
def test_break():
    input = """
    while(true) {
        break;
        notreached = true;
    }
    """
    parser = Parser()
    program = parser.parse(input)


def test_return():
    input = """
    function foo(bar) {
        return 100;
    }
    function foo(bar) {
        return
        100 * 2 // separate statement..
    }

    """
    parser = Parser()
    program = parser.parse(input)        


def test_labelled_statement():
    input = """
    label: {
        foo;
    }
    """
    parser = Parser()
    program = parser.parse(input)        


def test_try():
    input = """
    try {
        foo;
    }
    catch (clause) {
        bar;
    }

    try {
        foo;
    }
    catch (clause) {
        bar;
    }
    finally {
        foobar;
    }

    try {
        foo;
    }
    finally {
        foobar;
    }    
    """
    parser = Parser()
    program = parser.parse(input)        


def test_throw():
    input = """
    throw "foo";
    """
    parser = Parser()
    program = parser.parse(input)        
 
 
def test_debugger():
    input = """
    debugger;
    """
    parser = Parser()
    program = parser.parse(input)        

def test_with():
    input = """
    with(verylong.longlong.foobar) {
        var foo = bar;
    }
    """
    parser = Parser()
    program = parser.parse(input)
    
    
def test_empty():
    input = """
    ;
    ;
    """
    parser = Parser()
    program = parser.parse(input)

def test_block() :
    input = """
    {
        foo;
    }
    """
    parser = Parser()
    program = parser.parse(input)
    
def test_expression_statement():
    input = """
    100/100;
    foo++;
    --foo;
    
    """
    parser = Parser()
    program = parser.parse(input)
    
def test_var_declaration():
    input = """
    var foo, bar = 100;
    var foo=100, bar;
    var foo, bar;
    var bar
    var foo
    
    """
    parser = Parser()
    program = parser.parse(input)   
 
 
def test_function_call():
    input = """
    foo();
    """
    parser = Parser()
    program = parser.parse(input)
    
def test_new():
    input = """
    var p = new Foo.Bar();
    new Foo.Bar();
    Foo.Bar()[100];
    new Foo.Bar().bar;
    """
    parser = Parser()
    program = parser.parse(input)    
    