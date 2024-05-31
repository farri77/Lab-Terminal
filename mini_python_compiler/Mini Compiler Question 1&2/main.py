import re
from collections import namedtuple

# Token definition
Token = namedtuple('Token', ['type', 'value'])

# Lexer
def lexer(text):
    token_specification = [
        ('NUMBER',   r'\d+'),     # Integer
        ('ADD',      r'\+'),      # Addition
        ('MUL',      r'\*'),      # Multiplication
        ('LPAREN',   r'\('),      # Left Parenthesis
        ('RPAREN',   r'\)'),      # Right Parenthesis
        ('SKIP',     r'[ \t]+'),  # Skip over spaces and tabs
        ('MISMATCH', r'.'),       # Any other character
    ]
    tokens = []
    for mo in re.finditer('|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in token_specification), text):
        kind = mo.lastgroup
        value = mo.group()
        if kind == 'NUMBER':
            value = int(value)
        elif kind == 'SKIP':
            continue
        elif kind == 'MISMATCH':
            raise RuntimeError(f'{value} unexpected')
        tokens.append(Token(kind, value))
    return tokens

# Parser
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def parse(self):
        result = self.expr()
        if self.pos != len(self.tokens):
            raise SyntaxError('Unexpected token at the end')
        return result

    def expr(self):
        node = self.term()
        while self.pos < len(self.tokens) and self.tokens[self.pos].type == 'ADD':
            self.pos += 1
            node = ('ADD', node, self.term())
        return node

    def term(self):
        node = self.factor()
        while self.pos < len(self.tokens) and self.tokens[self.pos].type == 'MUL':
            self.pos += 1
            node = ('MUL', node, self.factor())
        return node

    def factor(self):
        token = self.tokens[self.pos]
        if token.type == 'NUMBER':
            self.pos += 1
            return ('NUMBER', token.value)
        elif token.type == 'LPAREN':
            self.pos += 1
            node = self.expr()
            if self.tokens[self.pos].type != 'RPAREN':
                raise SyntaxError('Expected closing parenthesis')
            self.pos += 1
            return node
        else:
            raise SyntaxError(f'Unexpected token: {token.type}')

# Semantic Analyzer
def analyze(node):
    if node[0] == 'NUMBER':
        return 'int'
    elif node[0] in ('ADD', 'MUL'):
        left_type = analyze(node[1])
        right_type = analyze(node[2])
        if left_type != 'int' or right_type != 'int':
            raise TypeError('Type error: Only integer operations are supported')
        return 'int'
    else:
        raise TypeError(f'Unknown node type: {node[0]}')

# Code Generator
def generate_code(node):
    if node[0] == 'NUMBER':
        return [f'PUSH {node[1]}']
    elif node[0] in ('ADD', 'MUL'):
        left_code = generate_code(node[1])
        right_code = generate_code(node[2])
        op_code = 'ADD' if node[0] == 'ADD' else 'MUL'
        return left_code + right_code + [op_code]

# Main function to compile and generate bytecode from input
def compile_expression(expression):
    tokens = lexer(expression)
    parser = Parser(tokens)
    ast = parser.parse()
    analyze(ast)  # Perform semantic analysis
    bytecode = generate_code(ast)
    return tokens, ast, bytecode

# Get user input
expression = input("Enter an arithmetic expression: ")
tokens, ast, bytecode = compile_expression(expression)

print("Tokens:", tokens)
print("AST:", ast)
print("Bytecode:", bytecode)
