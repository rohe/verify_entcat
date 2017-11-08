import shelve


class ResultDB(object):
    """
    Manager of the database containing all the latest test results for all 
    IdP's.
    """

    def __init__(self, db_path):
        """
        Creates a new manager of the database at the specified path.

        :param db_path location of the database (will be created if it 
        doesn't exist)
        """
        self.db = shelve.open(db_path, writeback=True)
        try:
            self.idp = self.db['idp']
        except KeyError:
            self.idp = []

    def update_test_result(self, idp, test, result):
        """
        Updates the result of an IdP on a test.

        :param idp IdP identifier
        :param test test identifier
        :param result the raw result (as dictionary).
        """

        try:
            _data = self.db[idp]
        except KeyError:
            self.idp.append(idp)
            _data = {test: result}
        else:
            _data[test] = result

        self.db[idp] = _data

    def get_overview_data(self):
        """
        Fetch all the latest test results.

        :return: Dictionary containing all results for IdP idp on test t in 
        dict[idp][t]
        """
        overview = {}

        for idp in self.idp:
            if idp not in overview:
                overview[idp] = self.db[idp]
        return overview
