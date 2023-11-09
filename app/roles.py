from rolepermissions.roles import AbstractUserRole

class Diretor(AbstractUserRole):
    available_permissions = {
        'view_as_melhores': True,
    }
class Nao_Logado(AbstractUserRole):
    available_permissions = {
        'create_medical_record': True,
    }

class Staff(AbstractUserRole):
    available_permissions = {
        'edit_patient_file': True,
    }
class Grente(AbstractUserRole):
    available_permissions = {
        'edit_patient_file': True,
    }
class Administrador(AbstractUserRole):
    available_permissions = {
        'edit_patient_file': True,
    }
