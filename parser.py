import parsley

class Number (object):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "Number({})".format(self.value)

    def excel(self):
        return self.value

class Cell (object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return "Cell({}, {})".format(repr(self.x), repr(self.y))

    def excel(self):
        return "{}{}".format(self.x, self.y)

class Arithmetic (object):
    def __init__(self, operand1, operator, operand2):
        self.operand1 = operand1
        self.operator = operator
        self.operand2 = operand2

    def __repr__(self):
        return "Arithmetic({}, {}, {})".format(
                repr(self.operand1),
                repr(self.operator),
                repr(self.operand2)
        )

    def excel(self, suppress_parens=False):
        # VisiCalc used left-to-right evaluation of arithmetic operators, unless
        # overriden by parentheses.
        # By only allowing explicitly parenthesised arithmetic operators on the
        # RHS, the grammar ensures that the AST's structure matches VisiCalc's
        # order of evaluation.
        # Here, we parenthesise every operation so that Excel will evaluate them
        # the way we want, rather than applying its natural order of operations.
        if suppress_parens:
            fs = "{}{}{}"
        else:
            fs = "({}{}{})"
        return fs.format(
            self.operand1.excel(),
            self.operator,
            self.operand2.excel()
        )

class Value (object):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "Value({})".format(self.value)

    def excel(self):
        if isinstance(self.value, Number):
            return self.value
        elif isinstance(self.value, Arithmetic):
            return "={}".format(self.value.excel(suppress_parens=True))
        else:
            return "={}".format(self.value.excel())

class Label (object):
    def __init__(self, first, rest):
        if first == '"':
            self.value = rest
        else:
            self.value = first + rest

    def __repr__(self):
        return "Label({})".format(self.value)

    def excel(self):
        return self.value


grammar = parsley.makeGrammar(r"""
digit = anything:x ?(x in '0123456789') -> x
letter = anything:x ?(x.upper() in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ') -> x
cell = '+'? letter:x digit:y -> Cell(x, y)
number = '+'? digit+:x -> Number(''.join(x))
arithmetic = (arithmetic | parenthesised_arithmetic | cell | number):o1 ('+' | '-' | '*' | '/'):oper (parenthesised_arithmetic | cell | number):o2 -> Arithmetic(o1, oper, o2)
parenthesised_arithmetic = '(' arithmetic:a ')' -> a
value = (arithmetic | cell | number):x -> Value(x)
label = ('"' | letter):first anything*:rest -> Label(first, ''.join(rest))
cell_content = label | value
""", globals())

while True:
    i = raw_input("> ")
    result = grammar(i).cell_content()
    print(repr(result))
    print(result.excel())