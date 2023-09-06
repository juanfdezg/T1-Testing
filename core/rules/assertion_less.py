from ..rule import *
import ast

class AssertionLessVisitor(WarningNodeVisitor):

    # Implementar Clase     
    def __init__(self):
        # guardamos los números de línea de las funciones de testing sin asserts
        self.lines = []

    # definición de una función/método
    def visit_FunctionDef(self, node):
        # verificamos si tiene algun assert
        if node.name.startswith('test_'):
            self.tiene_assert = False
            
            # queremos seguir explorando el resto de nodos dentro de la función, para saber si tiene asserts
            self.generic_visit(node)
            if not self.tiene_assert:
                self.lines.append(node.lineno)

    # llamada a una función/método (podría ser assert)
    def visit_Call(self, node):
        # si se llama el método como atributo y empieza con 'assert', entonces la función tiene un assert
        if isinstance(node.func, ast.Attribute) and node.func.attr.startswith('assert'):
            self.tiene_assert = True


class AssertionLessTestRule(Rule):

    # Implementar Clase 
    def analyze(self, node):
        # creamos un visitante y lo ejecutamos sobre el nodo
        visitor = AssertionLessVisitor()
        visitor.visit(node)
        
        # iteramos sobre las líneas que nos marca el visitor, y creamos un warning por cada una
        warnings = []
        for line in visitor.lines:
            warning = Warning('AssertionLessWarning', line, 'it is an assertion less test')
            warnings.append(warning)
        
        return warnings

    @classmethod
    def name(cls):
        return 'assertion-less'

