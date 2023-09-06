from ..rule import *
import ast

class AssertionTrueVisitor(WarningNodeVisitor):
    def __init__(self):
        self.lines = []
        # Vamos a usar un conjunto (set) para guardar variables que se establecen en True, así no tenemos repetidos y evitamos problemas futuros
        self.true_vars = set()

    def visit_Assign(self, node):
        # primero revisamos todos los targets, que son las variables a las que se asigna un valor (lo que va a la izquierda del =),
        # ya que pueden ser varias en una línea, como a, b = True, True
        for target in node.targets:
            # revisamos si en la asignación se le asigna una CONSTANTE igual a True
            if isinstance(target, ast.Name) and isinstance(node.value, ast.NameConstant) and node.value.value is True:
                self.true_vars.add(target.id)
        self.generic_visit(node)


    def visit_Call(self, node):
        # revisamos si el nodo es un método llamado assertTrue y tiene como argumento True o alguna variable que se estableció en True anteriormente
        if isinstance(node.func, ast.Attribute) and node.func.attr == 'assertTrue' and len(node.args) == 1:
            if (isinstance(node.args[0], ast.NameConstant) and node.args[0].value is True) or \
               (isinstance(node.args[0], ast.Name) and node.args[0].id in self.true_vars):
                # si es así, guardamos la línea
                self.lines.append(node.lineno)
        self.generic_visit(node)


    

class AssertionTrueTestRule(Rule):
    def analyze(self, node):
        # creamos un visitante y lo ejecutamos sobre el nodo
        visitor = AssertionTrueVisitor()
        visitor.visit(node)
        
        # iteramos sobre las líneas que nos marca el visitor, y creamos un warning por cada una
        warnings = []
        for line in visitor.lines:
            warning = Warning('AssertTrueWarning', line, 'useless assert true detected')
            warnings.append(warning)
        
        return warnings
        
    @classmethod
    def name(cls):
        return 'assertion-true'

