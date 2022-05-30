import Control
import json
import os


def save_sol_file(actual_port: int, libre_port: int):
    if libre_port == 1:
        Control.set_cal_type("PORT_1")
    else:
        Control.set_cal_type("PORT_2")
    Control.save_calibration("CAL/4PORT/UNMERGED/SOL" + str(actual_port) + str(libre_port))


def save_through_file(actual_ports: str):
    print("saving through file")
    Control.set_cal_type("SOLT")
    Control.save_calibration("CAL/4PORT/UNMERGED/THROUGH_" + actual_ports)


def merge_into_6_solt_files():
    pass


def merge_into_1_solt_file():
    directory_unmerged_str = 'CAL/4PORT/UNMERGED/'
    directory_merged_str = 'CAL/4PORT/MERGED/'
    cal_file_names = list(filter(lambda x: x.endswith('.cal'), os.listdir(directory_unmerged_str)))
    template_cal_dict = None
    with open(directory_unmerged_str + cal_file_names[0], "r") as f:
        template_cal_dict = json.load(f)
        del template_cal_dict['measurements']

    sol_ports_list = [[], []]
    through_1_2_measurement_list = []
    for file_name in cal_file_names:
        if file_name.startswith("SOL"):
            four_port_port = int(file_name[3])
            libre_port = int(file_name[4])
            with open(directory_unmerged_str + file_name, "r") as f:
                json_dict = json.load(f)
                for measurement in json_dict['measurements']:
                    if measurement['name'].startswith("Port " + str(libre_port)):
                        sol_ports_list[four_port_port - 1].append(measurement)

        elif file_name.startswith("THROUGH"):
            with open(directory_unmerged_str + file_name, "r") as f:
                json_dict = json.load(f)
                for measurement in json_dict['measurements']:
                    if measurement['name'] == "Through":
                        through_1_2_measurement_list.append(measurement)

    template_cal_dict['measurements'] = sol_ports_list[0] + sol_ports_list[1] + through_1_2_measurement_list

    with open(directory_merged_str + "PORT_12_SOLT.cal", "w") as f:
        json.dump(template_cal_dict, f, indent=1)


def main():
    #  for testing
    merge_into_1_solt_file()


if __name__ == "__main__":
    main()
