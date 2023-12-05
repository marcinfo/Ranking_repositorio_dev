from rolepermissions.roles import AbstractUserRole

class Diretor(AbstractUserRole):
    available_permissions = {'melhores': True,}
class Nao_liberado(AbstractUserRole):
    available_permissions = {
        'sem_acao': True,
    }

class Staff(AbstractUserRole):
    available_permissions = {

        'contrato': True,

    }
class Gerente(AbstractUserRole):
    available_permissions = {
    'contrato': True,
    }
class Administrador(AbstractUserRole):
    available_permissions = {
        'contrato': True,
        'melhores': True,
        'administrar':True,
    }

