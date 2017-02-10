from dentaladmin import utils

database = utils.database_connection
errors = utils.database_errors


class Treatment:
    def __init__(self):
        self.db = database
        self.treatments = self.db.treatments

    def find_treatments(self, search, status=1):
        query = {'status': status}
        if search is not None:
            query = {'status': status, '$or': [
                {'code': {'$regex': search, '$options': 'i'}},
                {'name': {'$regex': search, '$options': 'i'}},
                {'price': {'$regex': search, '$options': 'i'}}
            ]}
        treatments = self.treatments.find(query)
        count = treatments.count()
        if count > 0:
            return treatments
        return None

    def find_treatment(self, code, status=1):
        treatment = self.treatments.find_one({'code': code, 'status': status})
        if not treatment:
            return None
        return treatment

    def add_treatment(self, code, name, price, status=1):
        treatment_exist = self.treatments.find_one({'code': code, 'status': status})
        if treatment_exist:
            return "Oops, code is already taken"
        treatment = {'code': code, 'name': name, 'price': float(price), 'status': status}
        try:
            self.treatments.insert_one(treatment)
        except errors.OperationFailure:
            return "oops, mongo error"
        return True

    def edit_treatment(self, code, name, price):
        treatment = self.find_treatment(code)
        if treatment is None:
            return "Treatment not found"
        try:
            self.treatments.update_one({'code': code}, {
                '$set': {'name': name, 'price': float(price)}})
        except errors.OperationFailure:
            return "Oops, treatment not updated"
        return True

    def delete_treatment(self, code):
        treatment = self.find_treatment(code)
        if treatment is None:
            return "Treatment not found"
        try:
            self.treatments.update_one({'code': code}, {'$set': {'status': 0}})
        except errors.OperationFailure:
            return "Oops, treatment not deleted"
        return True

    def list_treatments(self, status=1):
        query = {'status': status}
        treatments = self.treatments.find(query)
        count = treatments.count()
        if count > 0:
            return treatments
        return None

    def get_treatment_by_code(self, code, status=1):
        query = {'code': code, 'status': status}
        treatment = self.treatments.find_one(query)
        if treatment is not None:
            return treatment
        return None
