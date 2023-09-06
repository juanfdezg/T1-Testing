from ..rule import *

class UnusedVariableVisitor(WarningNodeVisitor):
    def __init__(self):
        # queremos guardar las variables que han sido asignadas y sus líneas respectivas
        self.assigned_variables = {}
        # guardamos también las variables que han sido usadas en un conjunto (set) para evitar repetidos
        self.used_variables = set()

    def visit_Assign(self, node):
        # revisamos todos los targets, que son las variables a las que se asigna un valor (lo que va a la izquierda del =),
        for target in node.targets:
            if isinstance(target, Name):
                # guardamos la variable y su línea
                self.assigned_variables[target.id] = node.lineno
        self.generic_visit(node)

    def visit_Name(self, node):
        # revisamos si la variable se usa
        if isinstance(node.ctx, Load):
            self.used_variables.add(node.id)
        self.generic_visit(node)

# esta clase es para visitar las funciones y guardar los visitors de cada una
# tuvimos que implementarla porque antes estabamos usando ast.iter_child_nodes, pero está prohibido por enunciado
class FunctionVisitor(NodeVisitor):
    def __init__(self):
        self.visitors_funcion = []

    def visit_FunctionDef(self, node):
        visitor = UnusedVariableVisitor()
        visitor.visit(node)
        self.visitors_funcion.append(visitor)
        self.generic_visit(node)

class UnusedVariableTestRule(Rule):
    def analyze(self, node):
        warnings = []
        
        visitor_funcion = FunctionVisitor()
        visitor_funcion.visit(node)

        # iteramos sobre los visitors de cada función y revisamos si hay variables que no se usaron
        for visitor in visitor_funcion.visitors_funcion:
            for var in visitor.assigned_variables:
                if var not in visitor.used_variables:
                    warnings.append(Warning('UnusedVariable', visitor.assigned_variables[var], f'variable {var} has not been used'))

        return warnings

    @classmethod
    def name(cls):
        return 'not-used-variable'
