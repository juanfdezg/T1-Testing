import ast
from ..rule import *


class DuplicatedSetupVisitor(ast.NodeVisitor):
    # Clase a Implementar
    def __init__(self):
        self.test_methods = []

    def visit_FunctionDef(self, node):
        if node.name.startswith('test'):
            self.test_methods.append(node)
        self.generic_visit(node)

class DuplicatedSetupRule(Rule):
    # Clase a Implementar
    def analyze(self, node):
        visitor = DuplicatedSetupVisitor()
        visitor.visit(node)

        test_methods = visitor.test_methods
        if len(test_methods) < 2:
            return []

        common_setup_count = self.count_common_setup(test_methods)
        if common_setup_count:
            warning_message = 'there are ' + str(common_setup_count) + ' duplicated setup statements'
            return [Warning('DuplicatedSetup', common_setup_count, warning_message)]
        return []

    def count_common_setup(self, test_methods):
        first_method = test_methods[0]
        count = 0

        for i in range(len(first_method.body)):
            line = ast.dump(first_method.body[i])

            all_match = True
            for method in test_methods:
                if i >= len(method.body) or ast.dump(method.body[i]) != line:
                    all_match = False
                    break

            if all_match:
                count += 1
            else:
                break

        return count
