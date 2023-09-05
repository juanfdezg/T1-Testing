from ast import *
from core.rewriter import RewriterCommand

class ExtractSetupCommand(RewriterCommand):
    
    def apply(self, node):
        transformer = SetupExtractorTransformer()
        return transformer.visit(node)

    @classmethod
    def name(cls):
        return 'extract-setup'


class SetupExtractorTransformer(NodeTransformer):

    def visit_ClassDef(self, node):
        test_methods = [n for n in node.body if isinstance(n, FunctionDef) and n.name.startswith("test_")]

        if not test_methods:
            return node  # return early if there are no test methods

        common_assigns = None

        # find common assignments across all test methods
        for method in test_methods:
            assigns = [stmt for stmt in method.body if isinstance(stmt, Assign)]
            if common_assigns is None:
                common_assigns = assigns
            else:
                common_assigns = [a for a, b in zip(common_assigns, assigns) if self.is_same_assignment(a, b)]

        if not common_assigns:
            return node  # return early if there are no common assignments

        # replace variables with attributes in test methods
        for method in test_methods:
            for stmt in method.body:
                if isinstance(stmt, Assign) and stmt in common_assigns:
                    method.body.remove(stmt)
                else:
                    self.replace_with_self_attributes(stmt)

        # add common assignments as self attributes in setUp
        setup_method = FunctionDef(name="setUp",
                                   args=arguments(posonlyargs=[], args=[], vararg=None, kwonlyargs=[], kw_defaults=[],
                                                  kwarg=None, defaults=[]),
                                   body=common_assigns,
                                   decorator_list=[])
        
        setup_method.lineno = 1  # añade esta línea

        for stmt in setup_method.body:
            if isinstance(stmt, Assign):
                for target in stmt.targets:
                    if isinstance(target, Name):
                        target.id = "self." + target.id

        # add setUp method to the class
        node.body.insert(0, setup_method)

        return node

    def is_same_assignment(self, a, b):
        return isinstance(a, Assign) and isinstance(b, Assign) and dump(a) == dump(b)

    def replace_with_self_attributes(self, node):
        if isinstance(node, Name):
            node.id = "self." + node.id
        else:
            for child in iter_child_nodes(node):
                self.replace_with_self_attributes(child)


