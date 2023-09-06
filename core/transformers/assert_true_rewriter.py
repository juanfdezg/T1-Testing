from ast import *
import ast
from core.rewriter import RewriterCommand

# implementamos clase de NodeTransformer
class AssertTrueTransformer(NodeTransformer):
    
    def visit_Call(self, node):
        # buscamos llama a self.assertEquals
        if (isinstance(node.func, Attribute) and isinstance(node.func.value, Name) and
                node.func.value.id == "self" and node.func.attr == "assertEquals"):
            
            # revisamos que reciba dos argumentos y que el segundo sea una constante True
            if (len(node.args) == 2 and 
                    isinstance(node.args[1], NameConstant) and node.args[1].value is True):
                
                # hacemos la transformación a self.assertTrue
                return Call(
                    func=Attribute(
                        value=Name(id='self', ctx=Load()), 
                        attr='assertTrue', 
                        ctx=Load()
                    ), 
                    # el primer argumento es el mismo
                    args=[node.args[0]], 
                    keywords=[]
                )
        return self.generic_visit(node)

class AssertTrueCommand(RewriterCommand):
    
    def apply(self, node):
        transformer = AssertTrueTransformer()
        return transformer.visit(node)