import socket


def do_some_common_work():
    pass


def call_function_from_business_logic():
    from .business_logic import process_order

    process_order()
