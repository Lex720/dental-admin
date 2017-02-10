from dentaladmin import utils

database = utils.database_connection
errors = utils.database_errors


class Sequence:
    def __init__(self):
        self.db = database
        self.sequences = self.db.sequences

    def find_sequences(self, search, username=None):
        if username is None:
            query = {}
            if search is not None:
                query = {'$or': [
                    {'code': {'$regex': search, '$options': 'i'}},
                    {'date': {'$regex': search, '$options': 'i'}},
                    {'patient': {'$regex': search, '$options': 'i'}},
                    {'status': {'$regex': search, '$options': 'i'}},
                    {'doctor': {'$regex': search, '$options': 'i'}}
                ]}
        else:
            query = {'doctor': username}
            if search is not None:
                query = {'doctor': username, '$or': [
                    {'code': {'$regex': search, '$options': 'i'}},
                    {'date': {'$regex': search, '$options': 'i'}},
                    {'patient': {'$regex': search, '$options': 'i'}},
                    {'status': {'$regex': search, '$options': 'i'}}
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
        subtotal = treatment_price * int(treatment_quantity)
        if 'total' in sequence:
            new_total = sequence['total'] + float(subtotal)
        else:
            new_total = float(subtotal)
        document = {'date': date, 'diagnostic_code': int(diagnostic_code), 'treatment_code': treatment_code,
                    'treatment_quantity': int(treatment_quantity), 'subtotal': subtotal}
        try:
            self.sequences.update_one({'code': int(code)}, {'$set': {'total': round(new_total, 2), 'status': 2},
                                                            '$push': {'treatments': document}})
        except errors.OperationFailure:
            return "Oops, sequence not processed"
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

    def invoice_sequence(self, code):
        sequence = self.find_sequence(code)
        if sequence is None:
            return "Sequence not found"
        try:
            self.sequences.update_one({'code': int(code)}, {'$set': {'status': 0}})
        except errors.OperationFailure:
            return "Oops, sequence not invoiced"
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
