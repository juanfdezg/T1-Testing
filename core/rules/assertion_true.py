from ..rule import *
import ast

class AssertionTrueVisitor(WarningNodeVisitor):
    def __init__(self):
        self.lines = []
        # Este diccionario almacenará variables que se establecen en True
        self.true_vars = set()

    def visit_Assign(self, node):
        # Detecta asignaciones donde la variable se establece en True
        if isinstance(node.value, ast.NameConstant) and node.value.value is True:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.true_vars.add(target.id)
        self.generic_visit(node)

    def visit_Call(self, node):
        # Revisa si el nodo es un método llamado assertTrue y si su argumento es True
        if isinstance(node.func, ast.Attribute) and \
           node.func.attr == 'assertTrue' and \
           len(node.args) == 1:
            if (isinstance(node.args[0], ast.NameConstant) and node.args[0].value is True) or \
               (isinstance(node.args[0], ast.Name) and node.args[0].id in self.true_vars):
                self.lines.append(node.lineno)
        self.generic_visit(node)


    


class AssertionTrueTestRule(Rule):
    def analyze(self, node):
        # Creamos una instancia del visitante
        visitor = AssertionTrueVisitor()
        
        # Usamos el visitante para recorrer el nodo (AST)
        visitor.visit(node)
        
        # Por cada línea recogida por el visitante, generamos una advertencia
        warnings = [Warning('AssertTrueWarning', line, 'useless assert true detected') for line in visitor.lines]
        
        return warnings
        
    @classmethod
    def name(cls):
        return 'assertion-true'

