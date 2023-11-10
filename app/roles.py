from rolepermissions.roles import AbstractUserRole

class Diretor(AbstractUserRole):
    available_permissions = {'melhores': True,}
class Nao_liberado(AbstractUserRole):
    available_permissions = {
        'sem_acao': True,
    }

class Staff(AbstractUserRole):
    available_permissions = {
        'indicadores': True,
        'contrato': True,

    }
class Gerente(AbstractUserRole):
    available_permissions = {
        'contratosinformados': True,

    }
class Administrador(AbstractUserRole):
    available_permissions = {
        'informar_indicadores': True,
        'cadastrar_modificar': True,
        'administrar':True,
    }

