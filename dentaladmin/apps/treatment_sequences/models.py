from dentaladmin import utils

database = utils.database_connection
errors = utils.database_errors


class Sequence:
    def __init__(self):
        self.db = database
        self.sequences = self.db.sequences

    def find_sequences(self, search, username=None):
        code = None
        if username is not None:
            match = {'doctor': username}
            if search is not None:
                if search.isdigit() is True:
                    code = int(search)
                match = {'doctor': username,
                         '$or': [{'code': code},
                                 {'date': {'$regex': search, '$options': 'i'}},
                                 {'shift': {'$regex': search, '$options': 'i'}},
                                 {'patient_name': {'$regex': search, '$options': 'i'}}]
                         }
        else:
            match = {}
            if search is not None:
                if search.isdigit() is True:
                    code = int(search)
                match = {
                    '$or': [{'code': code},
                            {'date': {'$regex': search, '$options': 'i'}},
                            {'shift': {'$regex': search, '$options': 'i'}},
                            {'patient_name': {'$regex': search, '$options': 'i'}},
                            {'doctor_name': {'$regex': search, '$options': 'i'}}]
                }

        cursor = self.sequences.aggregate([
            {'$lookup': {
                'from': "patients",
                'localField': "patient",
                'foreignField': "dni",
                'as': "patient_data"}},
            {'$lookup': {
                'from': "users",
                'localField': "doctor",
                'foreignField': "username",
                'as': "doctor_data"}},
            {'$unwind': "$patient_data"},
            {'$unwind': "$doctor_data"},
            {"$project": {
                "code": 1,
                "status": 1,
                "date": 1,
                "shift": 1,
                "doctor": 1,
                "doctor_name": "$doctor_data.name",
                "patient_name": "$patient_data.name"}},
            {'$match': match}
        ])

        sequences = list(cursor)
        return sequences

    def find_sequence(self, code):
        sequence = self.sequences.find_one({'code': int(code)})
        if not sequence:
            return None
        return sequence

    def add_sequence(self, date, shift, doctor, patient, status=1):
        count = self.sequences.find({}).count()
        code = count + 1
        sequence = {'code': code, 'date': date, 'shift': shift, 'doctor': doctor, 'patient': patient, 'status': status}
        try:
            self.sequences.insert_one(sequence)
        except errors.OperationFailure:
            return "oops, mongo error"
        return True

    def add_sequence_from_patient(self, date, shift, doctor, patient, status=1):
        shift_formatted = None
        count = self.sequences.find({}).count()
        code = count + 1
        if shift == 'AM':
            shift_formatted = 'morning'
        if shift == 'PM':
            shift_formatted = 'afternoon'
        sequence = {'code': code, 'date': date, 'shift': shift_formatted, 'doctor': doctor, 'patient': patient,
                    'status': status}
        try:
            self.sequences.insert_one(sequence)
        except errors.OperationFailure:
            return False
        return code

    def process_sequence(self, code, diagnostic_code, treatment_code, treatment_price, treatment_quantity):
        sequence = self.find_sequence(code)
        if sequence is None:
            return "Sequence not found"
        date = utils.get_today_date()
        subtotal = float(treatment_price) * int(treatment_quantity)
        if 'total' in sequence:
            new_total = sequence['total'] + float(subtotal)
        else:
            new_total = float(subtotal)
        document = {'date': date, 'diagnostic_code': int(diagnostic_code), 'treatment_code': treatment_code,
                    'treatment_quantity': int(treatment_quantity), 'subtotal': round(subtotal, 2)}
        try:
            self.sequences.update_one({'code': int(code)}, {'$set': {'total': round(new_total, 2), 'status': 2},
                                                            '$push': {'treatments': document}})
        except errors.OperationFailure:
            return "Oops, sequence not processed"
        return True

    def delete_sequence_treatment(self, code, code2, subtotal):
        sequence = self.sequences.find_one({'code': int(code), 'treatments.diagnostic_code': int(code2)})
        if sequence is None:
            return "Sequence not found"
        new_total = sequence['total'] - float(subtotal)
        try:
            self.sequences.update_one({'code': int(code)}, {'$set': {'total': round(new_total, 2)},
                                                            '$pull': {'treatments': {'diagnostic_code': int(code2)}}})
            cursor = self.sequences.aggregate([
                {'$match': {'code': int(code)}},
                {'$unwind': '$treatments'},
                {'$group': {'_id': '', 'count': {'$sum': 1}}}
            ])
            result = list(cursor)
            if result:
                pass
            else:
                try:
                    self.sequences.update_one({'code': int(code)}, {'$set': {'status': 1}})
                except errors.OperationFailure:
                    return "Oops, treatment deleted but sequence not updated"
        except errors.OperationFailure:
            return "Oops, treatment not deleted"
        return True

    def close_sequence(self, code):
        sequence = self.find_sequence(code)
        if sequence is None:
            return "Sequence not found"
        try:
            self.sequences.update_one({'code': int(code)}, {'$set': {'status': 3}})
        except errors.OperationFailure:
            return "Oops, sequence not closed"
        return True

    def cancel_sequence(self, code):
        sequence = self.find_sequence(code)
        if sequence is None:
            return "Sequence not found"
        try:
            self.sequences.update_one({'code': int(code)}, {'$set': {'status': 0}})
        except errors.OperationFailure:
            return "Oops, sequence not canceled"
        return True

    def cancel_sequences_from_patient(self, dni):
        sequence = self.sequences.find({'patient': dni, '$or': [{'status': 1}, {'status': 2}]})
        if sequence is None:
            return False
        try:
            self.sequences.update({'patient': dni, '$or': [{'status': 1}, {'status': 2}]}, {'$set': {'status': 0}},
                                  upsert=False, multi=True)
        except errors.OperationFailure:
            return False
        return True
