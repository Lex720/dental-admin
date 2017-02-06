from dentaladmin import utils

database = utils.database_connection
errors = utils.database_errors


class Sequence:
    def __init__(self):
        self.db = database
        self.sequences = self.db.sequences

    def find_sequences(self, search):
        query = {}
        if search is not None:
            query = {'$or': [
                {'code': {'$regex': search, '$options': 'i'}},
                {'date': {'$regex': search, '$options': 'i'}},
                {'doctor': {'$regex': search, '$options': 'i'}}
            ]}
        sequences = self.sequences.find(query)
        count = sequences.count()
        if count > 0:
            return sequences
        return None

    def find_sequence(self, code):
        sequence = self.sequences.find_one({'code': int(code)})
        if not sequence:
            return None
        return sequence

    def add_sequence(self, date, doctor, patient, status=0):
        count = self.sequences.find({}).count()
        code = count + 1
        sequence = {'code': code, 'date': date, 'doctor': doctor, 'patient': patient, 'status': status}
        try:
            self.sequences.insert_one(sequence)
        except errors.OperationFailure:
            return "oops, mongo error"
        return True

    def add_sequence_from_patient(self, date, doctor, patient, status=0):
        count = self.sequences.find({}).count()
        code = count + 1
        sequence = {'code': code, 'date': date, 'doctor': doctor, 'patient': patient, 'status': status}
        try:
            self.sequences.insert_one(sequence)
        except errors.OperationFailure:
            return False
        return code

    def edit_sequence(self, code, name, date_of_birth, email, phone, address, visit_reason):
        sequence = self.find_sequence(code)
        if sequence is None:
            return "Patient not found"
        try:
            self.sequences.update_one({'code': code}, {
                '$set': {'name': name, 'date_of_birth': date_of_birth, 'email': email, 'phone': phone,
                         'address': address, 'visit_reason': visit_reason}})
        except errors.OperationFailure:
            return "Oops, sequence not updated"
        return True

    def close_sequence(self, code):
        sequence = self.find_sequence(code)
        if sequence is None:
            return "Patient not found"
        try:
            self.sequences.update_one({'code': code}, {'$set': {'status': 0}})
        except errors.OperationFailure:
            return "Oops, sequence not deleted"
        return True

    def invoice_sequence(self, code):
        sequence = self.find_sequence(code)
        if sequence is None:
            return "Patient not found"
        try:
            self.sequences.update_one({'code': code}, {'$set': {'status': 0}})
        except errors.OperationFailure:
            return "Oops, sequence not deleted"
        return True
