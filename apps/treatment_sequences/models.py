from dentaladmin import utils

database = utils.database_connection
errors = utils.database_errors


def get_sequence_match(search, username):
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
    return match


class Sequence:
    def __init__(self):
        self.db = database
        self.sequences = self.db.sequences

    def find_sequences(self, search, username=None):
        match = get_sequence_match(search, username)
        cursor = self.sequences.aggregate([
            {'$match': match},
            {'$lookup': {
                'from': 'patients',
                'localField': 'patient',
                'foreignField': 'dni',
                'as': 'patient_data'}},
            {'$lookup': {
                'from': 'users',
                'localField': 'doctor',
                'foreignField': 'username',
                'as': 'doctor_data'}},
            {'$unwind': '$patient_data'},
            {'$unwind': '$doctor_data'},
            {'$project': {
                'code': 1,
                'status': 1,
                'date': 1,
                'shift': 1,
                'doctor': 1,
                'doctor_name': '$doctor_data.name',
                'patient_name': '$patient_data.name'}},
            {'$sort': {'code': 1}}
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
        if shift == "AM":
            shift_formatted = "morning"
        if shift == "PM":
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

    def find_sequence_treatments(self, code):
        cursor = self.sequences.aggregate([
            {'$match': {'code': int(code), '$or': [{'status': 1}, {'status': 2}, {'status': 3}]}},
            {'$unwind': '$treatments'},
            {'$project': {
                '_id': 0,
                'date': '$treatments.date',
                'diagnostic_code': '$treatments.diagnostic_code',
                'treatment_code': '$treatments.treatment_code',
                'treatment_quantity': '$treatments.treatment_quantity',
                'subtotal': '$treatments.subtotal'}},
            {'$lookup': {
                'from': 'treatments',
                'localField': 'treatment_code',
                'foreignField': 'code',
                'as': 'treatment_data'}},
            {'$unwind': '$treatment_data'},
            {'$project': {
                'date': 1,
                'diagnostic_code': 1,
                'treatment_code': 1,
                'treatment_name': '$treatment_data.name',
                'treatment_price': '$treatment_data.price',
                'treatment_quantity': 1,
                'subtotal': 1}},
            {'$sort': {'date': 1}}
        ])

        treatments = list(cursor)
        if not treatments:
            return None
        return treatments

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

    def report_sequences(self, search, username=None):
        match = get_sequence_match(search, username)
        cursor = self.sequences.aggregate([
            {'$match': {'status': 3}},
            {'$match': match},
            {'$lookup': {
                'from': 'patients',
                'localField': 'patient',
                'foreignField': 'dni',
                'as': 'patient_data'}},
            {'$lookup': {
                'from': 'users',
                'localField': 'doctor',
                'foreignField': 'username',
                'as': 'doctor_data'}},
            {'$unwind': '$patient_data'},
            {'$unwind': '$doctor_data'},
            {'$project': {
                'code': 1,
                'date': 1,
                'total': 1,
                'earned': {'$divide': [{'$multiply': ['$total', 40]}, 100]},
                'doctor': 1,
                'doctor_name': '$doctor_data.name',
                'patient_name': '$patient_data.name'}},
            {'$sort': {'date': -1}}
        ])

        sequences = list(cursor)
        return sequences

    def report_sequences_total(self, search, username=None):
        match = get_sequence_match(search, username)
        cursor = self.sequences.aggregate([
            {'$match': {'status': 3}},
            {'$match': match},
            {'$group': {'_id': '', 'total': {'$sum': '$total'}}},
            {'$project': {'_id': 0, 'total': 1}},
        ])
        try:
            total = list(cursor)[0]['total']
        except IndexError:
            total = 0
        return total
