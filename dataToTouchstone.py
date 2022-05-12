import Control


def save_two_port():
    S11 = Control.get_trace_data("S11")
    S21 = Control.get_trace_data("S21")
    S12 = Control.get_trace_data("S12")
    S22 = Control.get_trace_data("S22")
    print(S11)