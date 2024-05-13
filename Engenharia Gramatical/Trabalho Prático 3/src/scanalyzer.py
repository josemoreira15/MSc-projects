from lark import Lark, Token, Tree
from lark.visitors import Interpreter
import json, sys

grammar = '''
// Regras Sintáticas
start: (def_function | content)+

def_function: def_type "function" ID "(" args? ")" "{" content* return_clause? "}"

def_type: VOID | type

type: INT | FLOAT | STRING | TUPLE | BOOLEAN | DICT | SET | LIST

hashable_value: BOOLEAN_VALUE | STRING_VALUE | INT_VALUE | FLOAT_VALUE | tuple

unhashable_value: list | dict | set

list: "[" ( ( hashable_value | unhashable_value ) ( "," ( hashable_value | unhashable_value ) )* )* "]"

tuple: "(" ( hashable_value | unhashable_value ) "," ( hashable_value | unhashable_value ) ("," ( hashable_value | unhashable_value ) )* ")"

dict: "{" ( hashable_value ":" ( hashable_value | unhashable_value ) ( "," hashable_value ":" ( hashable_value | unhashable_value ) ) * )? "}"

set: "{" ( hashable_value ( "," hashable_value )* )* "}"

arithmetic_operators: SUM | SUB | MUL | DIV | MOD | EXP | IDIV | PEQ | MEQ | DEQ | SEQ

comparison_operators: EQS | DIFS | LSS | GRT | LEQ | GEQ | IN

args: arg ("," arg)*

arg: type ID

params: param ("," param)*

param: (ID | hashable_value | unhashable_value)

unary_operators: INC | DEQ

unary_operation: ( (ID | hashable_value | call_function) unary_operators ) | ( unary_operators (ID | hashable_value | call_function) )

binary_operation: (ID | hashable_value | call_function) arithmetic_operators (ID | hashable_value | call_function)

condition: (hashable_value | unhashable_value | ID) comparison_operators (hashable_value | unhashable_value | ID)

content: declaration | assignment | unary_operation ";" | binary_operation ";" | while_loop | do_while_loop | for_loop | call_function ";" | if_clause

return_clause: "return" (call_function | hashable_value | unhashable_value | binary_operation | ID | condition) ";"

declaration: type ID ( "=" ( hashable_value | unhashable_value | ID | call_function | binary_operation | condition ) )? ";"

assignment: ID "=" (hashable_value | unhashable_value | ID | call_function | binary_operation | condition ) ";"

call_function: ID "(" params? ")"

while_loop: "while" "(" "!"? condition ")" "{" content* "}"

for_loop: "for" "(" (declaration | assignment) condition ";" (unary_operation ";" | binary_operation ";" | assignment) ")" "{" content* "}"

do_while_loop: "do" "{" content* "}" "while" "(" "!"? condition ")"

if_clause: "if" "(" "!"? condition ")" "{" content* "}" else_clause?

else_clause: "else" if_clause? "{" content* "}"


// Regras Lexicográficas
VOID: /void/
INT: /int/
FLOAT: /float/
STRING: /string/
TUPLE: /tuple/
BOOLEAN: /boolean/
DICT: /dict/
SET: /set/
LIST: /list/

BOOLEAN_VALUE: /true|false/
ID: /[a-zA-Z_]\w*/
FLOAT_VALUE: /\-?[0-9]+\.[0-9]+/
INT_VALUE: /\-?[0-9]+/
STRING_VALUE: /("[^"]*"|'[^']*')/

SUM: /\+/
SUB: /\-/
MUL: /\*/
DIV: /\//
MOD: /%/
EXP: /\*\*/
IDIV: /\/\//
PEQ: /\+=/
MEQ: /\*=/
DEQ: /\/=/
SEQ: /\-=/

EQS: /==/
DIFS: /!=/
LSS: /</
GRT: />/
LEQ: /<=/
GEQ: />=/
IN: /in/

INC: /\+\+/
DEC: /\-\-/


// Tratamento dos espaços em branco
%import common.WS
%ignore WS
'''



class MyInterpreter(Interpreter):

    def __init__(self):
        self.global_stats = {
            'vars_per_type': {
                'int': 0,
                'float': 0,
                'string': 0,
                'tuple': 0,
                'boolean': 0,
                'dict': 0,
                'set': 0,
                'list': 0
            },
            'functions': {},
            'instructions': {
                'declaration': 0,
                'assignment': 0,
                'unary_operation': 0,
                'binary_operation': 0,
                'while_loop': 0,
                'do_while_loop': 0,
                'for_loop': 0,
                'call_function': 0,
                'if_clause': 0
            },
            'nested_structures': 0,
            'nested_replace_ifs': 0
        }

        self.infos = {
            'global': {
                'instructions': {},
                'vars_logs': [],
                'errors': []
            }
        }

        self.variables = [{}]
        self.state = 'global'
        self.cycle = []

        self.graph = ""
        self.graph_acc = ""
        self.in_content = 0


    def start(self, tree):
        'start: (def_function | content)+'
        self.graph += f'digraph G {{\n  start -> '
        self.visit_children(tree)

        for var in self.variables[0]:
            if self.variables[0][var][2] == False:
                self.infos[self.state]['vars_logs'].append(f'the variable "{var}" was never used')

        for key in self.infos:
            self.infos[key]['vars_logs'] = list(set(self.infos[key]['vars_logs']))
            self.infos[key]['errors'] = list(set(self.infos[key]['errors']))

        self.graph += 'end\n}'
        self.graph = self.graph.replace('__if__replace__', 'end')

        return { 'gstats': self.global_stats, 'infos': self.infos, 'variables': self.variables }


    def def_function(self, tree):
        'def_function: def_type "function" ID "(" args? ")" "{" content* return_clause? "}"'
        self.variables.insert(0, {})
        self.state = tree.children[1].value
        self.infos[self.state] = {'instructions': {}, 'vars_logs': [], 'errors': []}

        args = self.visit(tree.children[2]) if (len(tree.children) > 2 and tree.children[2].data == 'args') else []
        for arg in args:
            self.variables[0][arg[0]] = (arg[1], True, False)

        def_type = self.visit(tree.children[0])
        self.global_stats['functions'][tree.children[1].value] = (def_type, [arg[1] for arg in args])

        for child in tree.children[2:]:
            if child.data == 'content':
                self.visit(child)

        self.in_content += 1
        return_type = self.visit(tree.children[-1]) if (isinstance(tree.children[-1], Tree) and tree.children[-1].data == 'return_clause') else 'void'
        self.graph_acc = ""
        self.in_content -= 1
        
        if def_type != return_type and return_type != None:
            self.infos[self.state]['errors'].append(f"the return type differs from the definition type")

        for var in self.variables[0]:
            if self.variables[0][var][2] == False:
                self.infos[self.state]['vars_logs'].append(f'the variable "{var}" was never used')
        
        self.variables.pop(0)
        self.state = 'global'


    def def_type(self, tree):
        'def_type: VOID | type'
        return tree.children[0].value if isinstance(tree.children[0], Token) else self.visit(tree.children[0])
        
    
    def type(self, tree):
        'type: INT | FLOAT | STRING | TUPLE | BOOLEAN | DICT | SET | LIST'
        return tree.children[0].value
    

    def hashable_value(self, tree):
        'hashable_value: BOOLEAN_VALUE | STRING_VALUE | INT_VALUE | FLOAT_VALUE | tuple'
        if isinstance(tree.children[0], Token):
            self.graph_acc += f'{tree.children[0].value}'
            return tree.children[0].type.split('_')[0].lower()
        
        else:
            self.visit(tree.children[0])
            return tree.children[0].data


    def unhashable_value(self, tree):
        'unhashable_value: list | dict | set'
        self.visit(tree.children[0])
        return tree.children[0].data
    

    def list(self, tree):
        'list: "[" ( ( hashable_value | unhashable_value ) ( "," ( hashable_value | unhashable_value ) )* )? "]"'
        self.graph_acc += '['

        if len(tree.children) > 0:
            for child in tree.children:
                self.visit(child)
                self.graph_acc += ', '
            self.graph_acc = self.graph_acc[:-2]

        self.graph_acc += ']'


    def tuple(self, tree):
        'tuple: "(" ( hashable_value | unhashable_value ) "," ( hashable_value | unhashable_value ) ("," ( hashable_value | unhashable_value ) )* ")"'
        self.graph_acc += '('
        self.visit(tree.children[0])

        if len(tree.children) > 1:
            for child in tree.children[1:]:
                self.graph_acc += ', '
                self.visit(child)
        self.graph_acc += ')'


    def dict(self, tree):
        'dict: "{" ( hashable_value ":" ( hashable_value | unhashable_value ) )* "}"'
        self.graph_acc += '{'
        # print(tree)

        if len(tree.children) > 0:
            for index in range(len(tree.children)):
                self.visit(tree.children[index])
                if index % 2 == 0:
                    self.graph_acc += ': '
                else:
                    self.graph_acc += ', '
            self.graph_acc = self.graph_acc[:-2]
            
        # print(self.graph_acc)
        self.graph_acc += '}'
        

    def set(self, tree):
        'set: "{" ( hashable_value ( "," hashable_value )* )? "}"'
        self.graph_acc += '{'

        if len(tree.children) > 0:
            for child in tree.children:
                self.visit(child)
                self.graph_acc += ', '
            self.graph_acc = self.graph_acc[:-2]

        self.graph_acc += '}'
    
    
    def arithmetic_operators(self, tree):
        'arithmetic_operators: SUM | SUB | MUL | DIV | MOD | EXP | IDIV | PEQ | MEQ | DEQ | SEQ'
        self.graph_acc += f' {tree.children[0].value} '
        return tree.children[0].value


    def comparison_operators(self, tree):
        'comparison_operators: EQS | DIFS | LSS | GRT | LEQ | GEQ | IN'
        self.graph_acc += f' {tree.children[0].value} '
        return tree.children[0].value
    

    def args(self, tree):
        'args: arg ("," arg)*'
        return [self.visit(child) for child in tree.children]


    def arg(self, tree):
        'arg: type ID'
        return (tree.children[1].value, self.visit(tree.children[0]))
    

    def params(self, tree):
        'params: param ("," param)*'
        params_result = []

        params_result.append(self.visit(tree.children[0]))
        for child in tree.children[1:]:
            self.graph_acc += ", "
            params_result.append(self.visit(child))

        return params_result


    def param(self, tree):
        'param: (ID | hashable_value | unhashable_value)'
        if isinstance(tree.children[0], Token):
            self.graph_acc += tree.children[0].value
            for var_dict in self.variables:
                if tree.children[0].value in var_dict:
                    var_dict[tree.children[0].value] = var_dict[tree.children[0].value][:-1] + (True,)
                    if var_dict[tree.children[0].value][1] == False:
                        self.infos[self.state]['vars_logs'].append(f'the variable "{tree.children[0].value}" was declared but not initialized')
                    return var_dict[tree.children[0].value][0]  
            return None
        
        return self.visit(tree.children[0])


    def unary_operators(self, tree):
        'unary_operators: INC | DEQ'
        self.graph_acc += tree.children[0].value
        pass
    

    def unary_operation(self, tree):
        'unary_operation: ( (ID | hashable_value | call_function) unary_operators ) | ( unary_operators (ID | hashable_value | call_function) )'
        check_type = None
        index = 0
        self.in_content += 1
        unary_visit = False

        if isinstance(tree.children[0], Tree) and tree.children[0].data == 'unary_operators':
            self.visit(tree.children[0])
            index = 1
            unary_visit = True

        if isinstance(tree.children[index], Token):
            self.graph_acc += tree.children[index].value
            for var_dict in self.variables:
                if tree.children[index].value in var_dict:
                    var_dict[tree.children[index].value] = var_dict[tree.children[index].value][:-1] + (True,)
                    check_type = var_dict[tree.children[index].value]
                    if check_type[1] == False:
                        self.infos[self.state]['vars_logs'].append(f'the variable "{tree.children[index].value}" was declared but not initialized')
                    check_type = check_type[0]
                    break

            if check_type == None:
                self.infos[self.state]['vars_logs'].append(f'the variable "{tree.children[index].value}" was not declared')

        else:
            check_type = self.visit(tree.children[index])

        if check_type not in ['int', 'float']:
            self.infos[self.state]['errors'].append(f'can not increment/decrement a variable of type {check_type}')

        if unary_visit == False:
            self.visit(tree.children[1])

        self.in_content -= 1

        if self.in_content == 0:
            graph_content = self.graph_acc
            self.graph += f'"{graph_content}"\n  "{graph_content}" -> '
            self.graph_acc = ""


    def binary_operation(self, tree):
        'binary_operation: (ID | hashable_value | call_function) arithmetic_operators (ID | hashable_value | call_function)'
        types = [None, None]
        make_op = True
        operation = None
        self.in_content += 1
        
        for index in [0, 1]:
            if isinstance(tree.children[2 * index], Token):
                self.graph_acc += tree.children[index * 2].value
                for var_dict in self.variables:
                    if tree.children[2 * index].value in var_dict:
                        var_info = var_dict[tree.children[2 * index].value]
                        var_dict[tree.children[2 * index].value] = var_dict[tree.children[2 * index].value][:-1] + (True,)
                        if var_info[1] == False:
                            self.infos[self.state]['vars_logs'].append(f'the variable "{tree.children[2 * index].value}" was declared but not initialized')
                        types[index] = var_info[0]
                        break

                if types[index] == None:
                    self.infos[self.state]['vars_logs'].append(f'the variable "{tree.children[2 * index].value}" was not declared')
                    make_op = False
            
            else:
                types[index] = self.visit(tree.children[2 * index])

            if operation == None:
                operation = self.visit(tree.children[1])

        self.in_content -= 1

        if self.in_content == 0:
            graph_content = self.graph_acc
            self.graph += f'"{graph_content}"\n  "{graph_content}" -> '
            self.graph_acc = ""

        if make_op == False:
            return None
        
        else:
            if types[0] != types[1]:
                self.infos[self.state]['errors'].append(f'can not make the operation "{operation}" between variables of different types ({types[0]} and {types[1]})')
                return None

            else:
                if types[0] not in ['int', 'float']:
                    if operation in ['+', '+='] and types[0] in ['tuple', 'string', 'list']:
                        return types[0]
                    else:
                        self.infos[self.state]['errors'].append(f'can not make the operation "{operation}" with variables of type {types[1]}')
                        return None
                else:
                    return types[0]


    def condition(self, tree):
        'condition: (hashable_value | unhashable_value | ID) comparison_operators (hashable_value | unhashable_value | ID)'
        types = [None, None]
        make_cond = True
        condition = None

        for index in [0, 1]:
            if isinstance(tree.children[2 * index], Token):
                self.graph_acc += tree.children[index * 2].value
                for var_dict in self.variables:
                    if tree.children[2 * index].value in var_dict:
                        var_info = var_dict[tree.children[2 * index].value]
                        var_dict[tree.children[2 * index].value] = var_dict[tree.children[2 * index].value][:-1] + (True,)
                        if var_info[1] == False:
                            self.infos[self.state]['vars_logs'].append(f'the variable "{tree.children[2 * index].value}" was declared but not initialized')
                        types[index] = var_info[0]
                        break

                if types[index] == None:
                    make_cond = False
                    self.infos[self.state]['vars_logs'].append(f'the variable "{tree.children[2 * index].value}" was not declared')

            else:
                types[index] = self.visit(tree.children[2 * index])

            if condition == None:
                condition = self.visit(tree.children[1])

        if make_cond == True:
            if condition not in ['==', '!=']:
                if condition in ['<', '>', '<=', '>=']:
                    if types[0] != types[1]:
                        self.infos[self.state]['errors'].append(f'can not make the operation "{condition}" between variables of different types ({types[0]} and {types[1]})')
                    if types[0] not in ['int', 'float', 'string']:
                        self.infos[self.state]['errors'].append(f'can not make the operation "{condition}" with variables of type {types[0]}')

                if condition == 'in':
                    if (types[0] == 'string' and types[1] == 'string') or (types[0] in ['int', 'float', 'string', 'tuple', 'boolean'] and types[1] in ['tuple', 'dict', 'set', 'list']):
                        pass
                    else:
                        self.infos[self.state]['errors'].append(f'can not make the operation "{condition}" with variables of type {types[0]} and {types[1]}')
        
        return 'boolean'

    
    def content(self, tree):
        'content: declaration | assignment | unary_operation ";" | binary_operation ";" | while_loop | do_while_loop | for_loop | call_function ";" | if_clause'
        self.global_stats['instructions'][tree.children[0].data.value] += 1
        if tree.children[0].data.value not in self.infos[self.state]['instructions']:
            self.infos[self.state]['instructions'][tree.children[0].data.value] = 0
        self.infos[self.state]['instructions'][tree.children[0].data.value] += 1

        self.visit(tree.children[0])


    def return_clause(self, tree):
        'return_clause: "return" (call_function | hashable_value | unhashable_value | binary_operation | ID | condition) ";"'
        if isinstance(tree.children[0], Token):
            for var_dict in self.variables:
                if tree.children[0].value in var_dict:
                    var_dict[tree.children[0]] = var_dict[tree.children[0]][:-1] + (True,)
                    var_info = var_dict[tree.children[0]]
                    if var_info[1] == False:
                        self.infos[self.state]['vars_logs'].append(f'the variable "{tree.children[0].value}" was declared but not initialized')
                    return var_info[0]
            
        else:
            return self.visit(tree.children[0])


    def declaration(self, tree):
        'declaration: type ID ( "=" ( hashable_value | unhashable_value | ID | call_function | binary_operation | condition ) )? ";"'
        type = self.visit(tree.children[0])
        self.graph_acc += f'{type} {tree.children[1].value}'
        self.in_content += 1

        if tree.children[1].value in self.variables[0]:
            self.infos[self.state]['vars_logs'].append(f'the variable "{tree.children[1].value}" already exists')

            if len(tree.children) > 2:
                self.graph_acc += ' = '
                if isinstance(tree.children[2], Tree):
                    self.visit(tree.children[2])
                else:
                    self.graph_acc += tree.children[2].value

        else:
            self.global_stats['vars_per_type'][type] += 1
            if len(tree.children) > 2:
                self.graph_acc += ' = '
                if isinstance(tree.children[2], Tree):
                    check_type = self.visit(tree.children[2])
                else:
                    self.graph_acc += tree.children[2].value
                    assign = False
                    check_type = None
                    for var_dict in self.variables:
                        if tree.children[2].value in var_dict:
                            assign = True
                            var_info = var_dict[tree.children[2].value]
                            var_dict[tree.children[2].value] = var_dict[tree.children[2].value][:-1] + (True,)
                            check_type = var_info[0]
                            break
                    
                    if assign == False:
                        self.infos[self.state]['vars_logs'].append(f'the variable "{tree.children[2].value}" was not declared')
                    
                
                if type != check_type and check_type != None:
                    self.infos[self.state]['vars_logs'].append(f'the variable "{tree.children[1].value}" ({type}) can not be declared with a {check_type} value"')
                    
                self.variables[0][tree.children[1].value] = (type, True, False)
                self.infos[self.state]['vars_logs'].append(f'the variable "{tree.children[1].value}" ({type}) was declared')

            else:
                self.variables[0][tree.children[1].value] = (type, False, False)
                self.infos[self.state]['vars_logs'].append(f'the variable "{tree.children[1].value}" ({type}) was declared')

        self.in_content -= 1
        
        
        if self.in_content == 0:
            graph_content = self.graph_acc
            self.graph = self.graph.replace('__if__replace__', graph_content)
            self.graph += f'"{graph_content}"\n  "{graph_content}" -> '
            self.graph_acc = ""


    def assignment(self, tree):
        'assignment: ID "=" (hashable_value | unhashable_value | ID | call_function | binary_operation | condition ) ";"'
        assign = False
        self.in_content += 1
        self.graph_acc += f'{tree.children[0].value} = '

        for var_dict in self.variables:
            if tree.children[0].value in var_dict:
                assign = True
                var_info = var_dict[tree.children[0].value]
                break

        if assign == True:
            assign_info = None

            if isinstance(tree.children[1], Token):
                self.graph += tree.children[1].value
                for var_dict in self.variables:
                    if tree.children[1].value in var_dict:
                        var_dict[tree.children[1].value] = var_dict[tree.children[1].value][:-1] + (True,)
                        assign_info = var_dict[tree.children[1].value]
                        break

                if assign_info == None:
                    self.infos[self.state]['vars_logs'].append(f'the variable "{tree.children[1].value}" was not declared')
                else:
                    assign_info = assign_info[0]

            else:
                assign_info = self.visit(tree.children[1])

            if var_info[0] != assign_info and assign_info != None:
                self.infos[self.state]['vars_logs'].append(f'the variable "{tree.children[0].value} ({var_info[0]}) can not be assigned with a {assign_info} value"')

        else:
            if isinstance(tree.children[1], Token):
                self.graph_acc += tree.children[1].value

            else:
                self.visit(tree.children[1])

            self.infos[self.state]['vars_logs'].append(f'the variable "{tree.children[0].value}" was not declared')

        self.in_content -= 1

        if self.in_content == 0:
            graph_content = self.graph_acc
            self.graph = self.graph.replace('__if__replace__', graph_content)
            self.graph += f'"{graph_content}"\n  "{graph_content}" -> '
            self.graph_acc = ""

        

    def call_function(self, tree):
        'call_function: ID "(" params? ")"'
        return_type = 0
        self.in_content += 1
        self.graph_acc += tree.children[0].value + "("

        if tree.children[0] not in self.global_stats['functions']:
            self.infos[self.state]['errors'].append(f'the function "{tree.children[0].value}" does not exist')
            if len(tree.children) > 1:
                self.visit(tree.children[1])

            return_type = None
        
        else:
            function = self.global_stats['functions'][tree.children[0].value]
            check_call_args = function[1]
            call_args = self.visit(tree.children[1]) if len(tree.children) > 1 else []

            if len(check_call_args) != len(call_args):
                self.infos[self.state]['errors'].append(f'the function "{tree.children[0].value}" takes {len(check_call_args)} argument(s) but {len(call_args)} was/were given')
                return_type = None
            
            else:
                for index in range(0, len(check_call_args)):
                    if check_call_args[index] != call_args[index] and call_args[index] != None:
                        self.infos[self.state]['errors'].append(f'the function "{tree.children[0].value}" was called with wrong type of arguments')
                        return_type = None
                        break
                    

        self.graph_acc += ")"
        self.in_content -= 1
        if self.in_content == 0:
            graph_content = self.graph_acc
            self.graph += f'"{graph_content}"\n  "{graph_content}" -> '
            self.graph_acc = ""

            
        return function[0] if return_type == 0 else return_type


    def while_loop(self, tree):
        'while_loop: "while" "(" "!"? condition ")" "{" content* "}"'
        self.variables.insert(0, {})
        self.graph_acc += 'while ('

        if len(self.cycle) > 0:
            self.global_stats['nested_structures'] += 1
        self.cycle.append('while')

        self.visit(tree.children[0])
        while_statement = self.graph_acc + ')'
        self.graph_acc = ""
        self.graph += f'"{while_statement}"\n  "{while_statement}" [shape=diamond];\n  "{while_statement}" -> '

        if len(tree.children) > 1:
            for child in tree.children[1:]:
                self.visit(child)

        self.graph += f'"{while_statement}"\n  "{while_statement}" -> '
        
        for var in self.variables[0]:
            if self.variables[0][var][2] == False:
                self.infos[self.state]['vars_logs'].append(f'the variable "{var}" was never used')

        self.cycle.pop()
        self.variables.pop(0)


    def for_loop(self, tree):
        'for_loop: "for" "(" (declaration | assignment) condition ";" (unary_operation ";" | binary_operation ";" | assignment) ")" "{" content* "}"'
        self.variables.insert(0, {})
        self.graph_acc += 'for ('

        if len(self.cycle) > 0:
            self.global_stats['nested_structures'] += 1
        self.cycle.append('for')

        self.in_content += 1

        for index in range(3):
            self.visit(tree.children[index])
            self.graph_acc += '; '

        self.graph_acc = self.graph_acc[:-2] + ")"
        for_statement = self.graph_acc
        self.graph_acc = ""
        self.in_content -= 1

        self.graph += f'"{for_statement}"\n  "{for_statement}" [shape=diamond];\n  "{for_statement}" -> '
        if len(tree.children) > 3:
            for child in tree.children[3:]:
                self.visit(child)

        self.graph += f'"{for_statement}"\n  "{for_statement}" -> '

        for var in self.variables[0]:
            if self.variables[0][var][2] == False:
                self.infos[self.state]['vars_logs'].append(f'the variable "{var}" was never used')

        self.cycle.pop()
        self.variables.pop(0)


    def do_while_loop(self, tree):
        'do_while_loop: "do" "{" content* "}" "while" "(" "!"? condition ")"'
        self.variables.insert(0, {})
        first_call = None

        if tree.children[0].data == 'content':
            self.visit(tree.children[0])
            first_call = self.graph.split("\n")[-1][3:-5]

        for child in tree.children[1:-1]:
            self.visit(child)

        self.graph_acc += 'while ('
        self.in_content += 1
        self.visit(tree.children[-1])
        self.in_content -= 1
        while_statement = self.graph_acc + ')'
        self.graph_acc = ""

        if first_call == None:
            first_call = while_statement

        self.graph += f'"{while_statement}"\n  "{while_statement}" [shape=diamond];\n  "{while_statement}" -> "{first_call}"\n  "{while_statement}" -> '

        if len(self.cycle) > 0:
            self.global_stats['nested_structures'] += 1
        self.cycle.append('do_while')

        for var in self.variables[0]:
            if self.variables[0][var][2] == False:
                self.infos[self.state]['vars_logs'].append(f'the variable "{var}" was never used')

        self.cycle.pop()
        self.variables.pop(0)


    def if_clause(self, tree):
        'if_clause: "if" "(" "!"? condition ")" "{" content* "}" else_clause?'
        self.variables.insert(0, {})
        self.graph_acc += 'if ('

        if len(self.cycle) > 0:
            self.global_stats['nested_structures'] += 1
        self.cycle.append('if')

        contents = []
        self.in_content += 1
        contents.append(self.visit(tree.children[0]))
        self.graph_acc += ")"
        if_statement = self.graph_acc
        self.graph_acc = ""
        self.in_content -= 1
        self.graph += f'"{if_statement}"\n  "{if_statement}" [shape=diamond];\n  "{if_statement}" -> '
        for child in tree.children:
            if child.data == 'content':
                contents.append(self.visit(child))

        self.graph += f'"__if__replace__"\n  "{if_statement}" -> ' 

        if tree.children[-1].data == 'else_clause':
            self.graph = self.graph.replace('__if__replace__', '__no__replace__')
            contents.append(self.visit(tree.children[-1]))

        self.graph = self.graph.replace('__no__replace__', '__if__replace__')
        
        if (len(contents) == 2 and contents == ['boolean', 'if']) or (len(contents) == 3 and contents == ['boolean', 'if', 'else']):
            if ('if' in contents) or ('if_else' in contents and tree.children[-1].data != 'else_clause'):
                self.global_stats['nested_replace_ifs'] += 1

        for var in self.variables[0]:
            if self.variables[0][var][2] == False:
                self.infos[self.state]['vars_logs'].append(f'the variable "{var}" was never used')

        self.cycle.pop()

        if tree.children[-1].data == 'else_clause':
            return 'if_else'
        else:
            self.variables.pop(0)
            return 'if'         
            

    def else_clause(self, tree):
        'else_clause: "else" if_clause? "{" content* "}"'
        self.variables.pop(0)
        self.variables.insert(0, {})
        self.visit_children(tree)

        for var in self.variables[0]:
            if self.variables[0][var][2] == False:
                self.infos[self.state]['vars_logs'].append(f'the variable "{var}" was never used')

        self.variables.pop(0)
        return 'else'


with open(f'../input/{sys.argv[1]}.txt') as file:
    content = file.read()

p = Lark(grammar)
parse_tree = p.parse(content)

dugojo = MyInterpreter()
data = dugojo.visit(parse_tree)


with open(f'../data/web/{sys.argv[1]}.json', 'w') as json_file:
    json.dump(data, json_file, indent=4)

with open(f'../data/graph/{sys.argv[1]}.txt', 'w') as dot_file:
    dot_file.write(dugojo.graph)