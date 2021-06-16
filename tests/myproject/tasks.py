def task_1():
    from .core import do_some_common_work

    do_some_common_work()


def task_2():
    from .core import do_some_common_work
    from .core import call_function_from_business_logic

    do_some_common_work()
    call_function_from_business_logic()
