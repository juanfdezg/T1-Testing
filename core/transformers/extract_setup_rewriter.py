from ast import *
import ast
from core.rewriter import RewriterCommand

# nos costó bastante implementar este rewriter, por lo que usamos varias líneas de código, pero funciona bien.
# intentamos dejar comentado lo mayor posible para que se entienda mejor.

class SetupExtractorTransformer(NodeTransformer):

    def visit_ClassDef(self, node):

        # guardamos todos los métodos que empiezan con test_
        metodos_test = []
        for n in node.body:
            if isinstance(n, FunctionDef) and n.name.startswith("test_"):
                metodos_test.append(n)

        asignaciones_comun = None

        # queremos encontrar asignaciones comunes en todos los métodos test
        for metodo in metodos_test:
            # en esta lista vamos a guardar todos los assigns de cada método
            assigns = []
            for elemento in metodo.body:
                if isinstance(elemento, Assign):
                    assigns.append(elemento)

            # si es el primer método, guardamos los assigns. este if solo se ejecuta para el primer método
            if asignaciones_comun is None:
                asignaciones_comun = assigns
            
            # si no es el primer método, revisamos si los assigns de este método son iguales a los assigns en común
            else:
                nuevas_asignaciones_comun = []
                for a in asignaciones_comun:
                    for b in assigns:
                        if self.is_same_assignment(a, b):
                            nuevas_asignaciones_comun.append(a)
                            # hacemos un break para que no se agregue el mismo assign dos veces
                            break
                asignaciones_comun = nuevas_asignaciones_comun

        # si no hay asignaciones comunes, no hay nada que hacer y retornamos el nodo original
        if not asignaciones_comun:
            return node 

        # reemplazamos los assigns por self.atributo
        for metodo in metodos_test:
            nuevo_body = []

            for elemento in metodo.body:
                elemento_codigo = ast.dump(elemento)
                
                # verificamos si alguna de las asignaciones comunes es igual al código del elemento actual
                coincide = False
                for assign in asignaciones_comun:
                    if ast.dump(assign) == elemento_codigo:
                        coincide = True
                        break

                # si es que no coincide con ninguna asignación común, hacemos el reemplazo y agregamos el elemento al nuevo body
                if not coincide:
                    self.replace_with_self_attributes(elemento)
                    nuevo_body.append(elemento)

            # actualizamos el cuerpo del método
            metodo.body = nuevo_body

        # agregamos las líneas de código comunes al metodo setup
        metodo_setup = FunctionDef(name="setUp",
                                   args=arguments(posonlyargs=[], args=[arg(arg='self')], vararg=None, kwonlyargs=[], kw_defaults=[],
                                                  kwarg=None, defaults=[]),
                                   body=asignaciones_comun,
                                   decorator_list=[])
        
        # para que el método setup aparezca primero en el código, sin esta línea el código nos tira un error
        metodo_setup.lineno = 1

        # print(f'antes: {ast.dump(metodo_setup)}')
        
        # reemplazamos los assigns por self.atributo en el método setup
        for elemento in metodo_setup.body:
            if isinstance(elemento, Assign):
                for target in elemento.targets:
                    if isinstance(target, Name):
                        target.id = "self." + target.id

        # print(f'después: {ast.dump(metodo_setup)}')

        # agregamos el método setup
        node.body.insert(0, metodo_setup)

        # print(ast.dump(node, indent=2))

        # retornamos el nodo con el método setup agregado
        return node

    # este método lo usamos para revisar si dos assigns son iguales, lo simplificamos a una línea de código
    def is_same_assignment(self, a, b):
        return isinstance(a, Assign) and isinstance(b, Assign) and dump(a) == dump(b)

    def replace_with_self_attributes(self, node):
        if isinstance(node, ast.Name) and node.id != "self":
            # reemplazamos el nombre de la variable por self.nombre_variable
            node.id = "self." + node.id

        # usamos dir para obtener todos los atributos del nodo
        for atributo in dir(node):
            # queremos ignorar los nodos que empiezan con _ porque son atributos internos
            if not atributo.startswith('_') and isinstance(getattr(node, atributo), ast.AST):
                # reemplazamos los atributos del nodo por self.atributo recursivamente
                setattr(node, atributo, self.replace_with_self_attributes(getattr(node, atributo)))
            
            # si es que el atributo es una lista, la recorremos y reemplazamos también recursivamente
            elif isinstance(getattr(node, atributo), list):
                # usamos esta lista para guardar los nuevos atributos
                new_list = []
                for item in getattr(node, atributo):
                    if isinstance(item, ast.AST):
                        new_list.append(self.replace_with_self_attributes(item))
                    else:
                        new_list.append(item)
                setattr(node, atributo, new_list)

        # retornamos el nodo con los atributos reemplazados
        return node


class ExtractSetupCommand(RewriterCommand):
    def apply(self, node):
        transformer = SetupExtractorTransformer()
        return transformer.visit(node)

    @classmethod
    def name(cls):
        return 'extract-setup'

