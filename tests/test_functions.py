from pyjsparser.parser import Parser

def test_function():
    input = """

    function foo() {
        
    }

    function foo(bar) {
        
    }

    function foo(bar, foo) {
        
    }
    
    var p = function() {
        
    }
    
    var p = function(bar) {
        
    }
    
    var p = function(foo, bar) {
        
    }
    
    (function(foo){
        
    }())
    
    """
    parser = Parser()
    program = parser.parse(input)
    
def test_function_in_function():
    
    input = """
    // Officialy not allowed, but browsers do support it.
    // jQuery uses it also once.
    
    function foo() {
       function bar() {
       }
    }
    """
    parser = Parser()
    program = parser.parse(input) 