import ast
from ..rule import *


class DuplicatedSetupVisitor(NodeVisitor):
    # Clase a Implementar
    def __init__(self):
        # guardamos los métodos que representan tests
        self.metodos_test = []

    def visit_FunctionDef(self, node):
        # si el método/función empieza con 'test' lo guardamos
        if node.name.startswith('test'):
            self.metodos_test.append(node)
        self.generic_visit(node)

class DuplicatedSetupRule(Rule):
    # Clase a Implementar
    def analyze(self, node):
        visitor = DuplicatedSetupVisitor()
        visitor.visit(node)

        metodos_test = visitor.metodos_test
        # si es menor a 2 no hay forma de que haya duplicados
        if len(metodos_test) < 2:
            return []

        lineas_en_comun = self.contar_lineas_comun(metodos_test)
        # líneas en común significa que hay duplicados
        if lineas_en_comun > 0:
            warning_message = 'there are ' + str(lineas_en_comun) + ' duplicated setup statements'
            return [Warning('DuplicatedSetup', lineas_en_comun, warning_message)]
        

        return []


    # función para contar la cantidad de líneas iniciales que son comunes a todos los métodos
    def contar_lineas_comun(self, metodos_test):
        # revisamos la primera línea de cada método, si son iguales, revisamos la segunda, y así sucesivamente
        primer_metodo = metodos_test[0]
        contador = 0

        for i in range(len(primer_metodo.body)):
            # usamos ast.dump para ver el nodo como string, y así poder comparar dps
            line = ast.dump(primer_metodo.body[i])

            todos_igual = True
            for metodo in metodos_test:
                # si es que ya no hay más lineas en el método o si la línea no es igual, entonces no hay más líneas en común
                if i >= len(metodo.body) or ast.dump(metodo.body[i]) != line:
                    todos_igual = False
                    break

            # si todas las líneas son iguales, aumentamos el contador
            if todos_igual:
                contador += 1
            else:
                break

        return contador
