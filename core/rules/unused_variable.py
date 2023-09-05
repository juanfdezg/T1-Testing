from ..rule import *
import ast

class UnusedVariableVisitor(WarningNodeVisitor):
    def __init__(self):
        self.assigned_variables = {}
        self.used_variables = set()

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.assigned_variables[target.id] = node.lineno
        self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.used_variables.add(node.id)
        self.generic_visit(node)

class UnusedVariableTestRule(Rule):
    def analyze(self, node):
        warnings = []
        self.function_visitors = []

        self.analyze_function(node)

        # Una vez recopilados todos los visitantes de las funciones, analizamos cada uno para obtener las advertencias
        for visitor in self.function_visitors:
            for var in visitor.assigned_variables:
                if var not in visitor.used_variables:
                    warnings.append(Warning('UnusedVariable', visitor.assigned_variables[var], f'variable {var} has not been used'))

        return warnings

    def analyze_function(self, node):
        if isinstance(node, ast.FunctionDef):
            visitor = UnusedVariableVisitor()
            visitor.visit(node)
            self.function_visitors.append(visitor)

        # Luego llamamos recursivamente a todos los nodos hijos
        for child in ast.iter_child_nodes(node):
            self.analyze_function(child)

    @classmethod
    def name(cls):
        return 'not-used-variable'


