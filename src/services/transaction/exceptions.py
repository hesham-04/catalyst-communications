class TransactionError(Exception):
    """
    Custom exception for transaction-related errors.
    """

    def __init__(self, message, details=None):
        super().__init__(message)
        self.details = details
        print("TransactionError: ", message)
        print("Details: ", details)
