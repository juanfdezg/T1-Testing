from ast import *
from core.rewriter import RewriterCommand


class AssertTrueTransformer(NodeTransformer):
    
    def visit_Call(self, node):
        # Buscar llamadas a self.assertEquals
        if (isinstance(node.func, Attribute) and
                isinstance(node.func.value, Name) and
                node.func.value.id == "self" and
                node.func.attr == "assertEquals"):
            
            # Si el segundo argumento es un literal True
            if (len(node.args) == 2 and 
                    isinstance(node.args[1], NameConstant) and 
                    node.args[1].value is True):
                
                # Transformarlo a self.assertTrue(x)
                return Call(
                    func=Attribute(
                        value=Name(id='self', ctx=Load()), 
                        attr='assertTrue', 
                        ctx=Load()
                    ), 
                    args=[node.args[0]], 
                    keywords=[]
                )
        return self.generic_visit(node)

class AssertTrueCommand(RewriterCommand):
    
    def apply(self, node):
        transformer = AssertTrueTransformer()
        return transformer.visit(node)