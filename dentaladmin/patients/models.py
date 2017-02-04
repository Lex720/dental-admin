from dentaladmin import utils

database = utils.database_connection
errors = utils.database_errors


class Patient:
    def __init__(self):
        self.db = database
        self.patients = self.db.patients

    def find_patients(self, search, status=1):
        query = {'status': status}
        if search is not None:
            query = {'status': status, '$or': [
                {'dni': {'$regex': search, '$options': 'i'}},
                {'name': {'$regex': search, '$options': 'i'}},
                {'email': {'$regex': search, '$options': 'i'}},
                {'phone': {'$regex': search, '$options': 'i'}}
            ]}
        patients = self.patients.find(query)
        count = patients.count()
        if count > 0:
            return patients
        return None

    def find_patient(self, dni, status=1):
        patient = self.patients.find_one({'dni': dni, 'status': status})
        if not patient:
            return None
        return patient

    def add_patient(self, dni, name, date_of_birth, email, phone, address, visit_reason, status=1):
        patient_exist = self.patients.find_one({'dni': dni, 'status': status})
        email_exist = self.patients.find_one({'email': email, 'status': status})
        if patient_exist:
            return "Oops, dni is already taken"
        if email_exist:
            return "Oops, email is already taken"
        patient = {'dni': dni, 'name': name, 'date_of_birth': date_of_birth, 'email': email, 'phone': phone,
                   'address': address, 'visit_reason': visit_reason, 'status': status}
        try:
            self.patients.insert_one(patient)
        except errors.OperationFailure:
            return "oops, mongo error"
        return True

    def edit_patient(self, dni, name, date_of_birth, email, phone, address, visit_reason):
        patient = self.find_patient(dni)
        if patient is None:
            return "Patient not found"
        try:
            self.patients.update_one({'dni': dni}, {
                '$set': {'name': name, 'date_of_birth': date_of_birth, 'email': email, 'phone': phone,
                         'address': address, 'visit_reason': visit_reason}})
        except errors.OperationFailure:
            return "Oops, patient not updated"
        return True

    def delete_patient(self, dni):
        patient = self.find_patient(dni)
        if patient is None:
            return "Patient not found"
        try:
            self.patients.update_one({'dni': dni}, {'$set': {'status': 0}})
        except errors.OperationFailure:
            return "Oops, patient not deleted"
        return True
