from .handlers import TRANSACTION_HANDLERS


def delete_transaction_instance(
    transaction_type, source=None, destination=None, amount=None, ledger=None, **kwargs
):
    """
    Dispatcher for handling different transaction types.
    - transaction_type: str, the type of transaction.
    - source: Object, the source object for the transaction.
    - destination: Object, the destination object for the transaction (optional).
    - amount: Decimal, the amount involved in the transaction (optional).
    - ledger: Ledger object, the ledger entry associated with the transaction (optional).
    """
    handler = TRANSACTION_HANDLERS.get(transaction_type)
    if handler:
        handler(source, destination=destination, amount=amount, ledger=ledger, **kwargs)
    else:
        raise ValueError(f"Unsupported transaction type: {transaction_type}")
