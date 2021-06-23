import bisect
import csv

from test_proj.logging import *


def handle_request_1():
    from .tasks import task_1

    task_1()


def handle_request_2():
    from .tasks import task_2

    task_2()


def run_server():
    log("Server started")

    handle_request_1()
    handle_request_2()
