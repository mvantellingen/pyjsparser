from pyjsparser.parser import Parser

def test_binop():
    input = """
        100 - 100;
        100 + 100;
        100 / 100;
        100 * 100;
        100 % 100;
        
        p -= 100;
        p += 100;
        p *= 100;
        p /= 100;
        p %= 100;
        p >>= 1;
        p >>>= 2;
        p <<= 3;
        
        p == 100;
        p === 100;
        p != 100;
        p !== 100;
        
        100 == 100 === 100
        100 != 100 !== 100
        
        100 & 1;
        100 | 1;
        100 ^ 1;
        100 &= 100;
        100 |= 100;
        100 ^= 100;
        
    """
    parser = Parser()
    program = parser.parse(input)

def test_condop():
    input = """
    var p =(true) ? false : true;
    """
    parser = Parser()
    program = parser.parse(input) 