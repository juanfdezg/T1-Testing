from ast import *
from core.rewriter import RewriterCommand
from copy import deepcopy
class InlineTransformer(NodeTransformer):

    def __init__(self):
        self.var_values = {}
        self.var_usage = {}

    def visit_Assign(self, node):
        if isinstance(node.targets[0], Name):
            var_name = node.targets[0].id
            self.var_values[var_name] = node.value
            self.var_usage[var_name] = self.var_usage.get(var_name, 0)
        return node  # return node, not generic_visit(node) here

    def visit_Name(self, node):
        if isinstance(node.ctx, Load) and node.id in self.var_usage:
            self.var_usage[node.id] += 1
        return node

    def visit_FunctionDef(self, node):
        # First pass: gather all variable usages
        self.generic_visit(node)

        changed = True
        while changed:
            changed = False
            new_body = []
            for stmt in node.body:
                if isinstance(stmt, Assign) and isinstance(stmt.targets[0], Name):
                    var_name = stmt.targets[0].id
                    if self.var_usage[var_name] == 1:
                        changed = True
                        continue
                new_body.append(self.replace_vars(stmt))
            node.body = new_body

        return node

    def replace_vars(self, node):
        if isinstance(node, Name) and node.id in self.var_values and self.var_usage[node.id] == 1:
            return deepcopy(self.var_values[node.id])
        return self.generic_visit(node)

class InlineCommand(RewriterCommand):
    def apply(self, node):
        transformer = InlineTransformer()
        return transformer.visit(node)
