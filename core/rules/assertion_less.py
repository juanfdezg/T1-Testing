from ..rule import *
import ast

class AssertionLessVisitor(WarningNodeVisitor):

    # Implementar Clase     
    def __init__(self):
        # Lista para guardar los números de línea de las funciones de testeo sin aserciones
        self.lines = []

    def visit_FunctionDef(self, node):
        # Si el nombre de la función comienza con 'test_', verificamos si tiene alguna aserción
        if node.name.startswith('test_'):
            self.has_assert = False
            # Usamos el visit_Call para identificar las aserciones dentro de esta función
            self.generic_visit(node)
            if not self.has_assert:
                self.lines.append(node.lineno)

    def visit_Call(self, node):
        # Si es una llamada y comienza con 'assert', marca que la función tiene una aserción
        if isinstance(node.func, ast.Attribute) and node.func.attr.startswith('assert'):
            self.has_assert = True


class AssertionLessTestRule(Rule):

    # Implementar Clase 
    def analyze(self, node):
        # Creamos una instancia del visitante
        visitor = AssertionLessVisitor()
        
        # Usamos el visitante para recorrer el nodo (AST)
        visitor.visit(node)
        
        # Por cada línea recogida por el visitante, generamos una advertencia
        warnings = [Warning('AssertionLessWarning', line, 'it is an assertion less test') for line in visitor.lines]
        
        return warnings

    @classmethod
    def name(cls):
        return 'assertion-less'

