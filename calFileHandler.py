import Control


def save_sol_file(actual_port: int, libre_port: int):
    Control.save_calibration("CAL/4PORT/UNMERGED/SOL" + str(actual_port) + str(libre_port))


def save_through_file(actual_ports: int, libre_ports: int):
    Control.save_calibration("CAL/4PORT/UNMERGED/THROUGH" + str(actual_ports) + str(libre_ports))
