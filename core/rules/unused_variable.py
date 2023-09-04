from ..rule import *
import ast

class UnusedVariableVisitor(ast.NodeVisitor):
    def __init__(self):
        super().__init__()
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

class FunctionVisitor(ast.NodeVisitor):
    def __init__(self):
        super().__init__()
        self.function_visitors = []

    def visit_FunctionDef(self, node):
        visitor = UnusedVariableVisitor()
        visitor.visit(node)
        self.function_visitors.append(visitor)
        self.generic_visit(node)

class UnusedVariableTestRule(Rule):
    def analyze(self, node):
        warnings = []
        
        function_visitor = FunctionVisitor()
        function_visitor.visit(node)

        for visitor in function_visitor.function_visitors:
            for var in visitor.assigned_variables:
                if var not in visitor.used_variables:
                    warnings.append(Warning('UnusedVariable', visitor.assigned_variables[var], f'variable {var} has not been used'))

        return warnings

    @classmethod
    def name(cls):
        return 'not-used-variable'
