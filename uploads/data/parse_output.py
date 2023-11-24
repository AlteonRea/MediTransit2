
from data.problem_generator import MasterRelasi
from data.problem_generator import MasterProduk
from data.problem_generator import MasterCabang
from data.problem_generator import ProblemGenerator
from order.order import Order

from item.box import Box
from item.medicine import Medicine

import copy

import shutil
import os

def parse_output(problems, solutions, depot_coords, kode_cabangs, output_file_name="Dummy"):
    folder = 'PackingResults'
    if not os.path.exists(folder):
        os.makedirs(folder)

    #clear
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)

    with open(f"{output_file_name}_result.csv", "w") as file:
        for k in range(len(problems)):
            solution = solutions[k]
            problem = problems[k]
            kode_cabang = kode_cabangs[k]
            for i in range(solution.num_vehicle):
                vehicle = problem.vehicle_list[i]
                c_tour_list = solution.tour_list[i]

                if len(c_tour_list) == 0:
                    continue

                with open(f"PackingResults/{vehicle.id}.txt", "w") as file2:
                    vehicle.box.generate_packing_animation(str(vehicle.id), "PackingResults", "..")

                    file.write(f"{vehicle.id},{vehicle.vehicle_type},{vehicle.vendor},{kode_cabang},{depot_coords[k][0]},{depot_coords[k][1]},-1")

                    tempitems = []

                    for jtemp in range(len(c_tour_list)):
                        j = c_tour_list[jtemp]
                        order = problem.order_list[j]

                        coords = order.coord
                        file.write(f",{coords[0]},{coords[1]},{order.id}")

                        #file2.write(f"Order {order.id}\n")
                        with open(f"PackingResults/Order{order.id}.txt", "w") as file4:
                            for itemindex in range(len(order.packed_item_list)):
                                item = order.packed_item_list[itemindex]
                                if isinstance(item, Box):

                                    item.generate_packing_animation(f"{order.id}-{itemindex + 1}", f"PackingResults/{vehicle.id}", "../..")
                                    file4.write(f"({itemindex + 1}). Kardus {item.name} :\n")

                                    if not os.path.exists(f"PackingResults/{vehicle.id}"):
                                        os.makedirs(f"PackingResults/{vehicle.id}")
                                    with open(f"PackingResults/{vehicle.id}/{order.id}-{itemindex + 1}.txt", "w") as file3:
                                        file3.write(f"Siapkan Kardus ({itemindex + 1}) {item.name} untuk Order {order.id}\n")
                                        for item_in_box_index in range(len(item.packed_items)):
                                            item_in_box = item.packed_items[item_in_box_index]
                                            file3.write(f"\t({item_in_box_index + 1}). Rotasi Obat {item_in_box.name} dari Order {order.id} menjadi ({item_in_box.size[0]}, {item_in_box.size[1]}, {item_in_box.size[2]}), dan letakkan pada posisi : ({item_in_box.position[0]}, {item_in_box.position[1]}, {item_in_box.position[2]})\n")
                                            file4.write(f"\t({item_in_box_index + 1}). Obat {item_in_box.name}\n")

                                elif isinstance(item, Medicine):
                                    file4.write(f"({itemindex + 1}). Obat {item.name}\n")
                                tempitems.append((item, order.id))
                                #file2.write(f"\t({itemindex + 1}). Rotasi {itemtype} {item.name} dari Order {order.id} menjadi ({item.size[0]}, {item.size[1]}, {item.size[2]}), dan letakkan pada posisi : ({item.position[0]}, {item.position[1]}, {item.position[2]})\n")

                    tempitems = sorted(tempitems, key=lambda item: item[0].insertion_order)
                    for tempitemindex in range(len(tempitems)):
                        item = tempitems[tempitemindex][0]
                        orderid = tempitems[tempitemindex][1]
                        itemtype = None
                        if isinstance(item, Box):
                            itemtype = "Dus"
                        elif isinstance(item, Medicine):
                            itemtype = "Obat"
                        file2.write(f"({tempitemindex + 1}). Rotasi {itemtype} {item.name} dari Order {orderid} menjadi ({item.size[0]}, {item.size[1]}, {item.size[2]}), dan letakkan pada posisi : ({item.position[0]}, {item.position[1]}, {item.position[2]})\n")

                    file.write(f",{depot_coords[k][0]},{depot_coords[k][1]},-1\n")


def parse_input(input_file_name="Dummy"):
    orders = {}
    with open(f"{input_file_name}.csv", "r") as file:
        lines = file.readlines()

        for line in lines:
            cells = line.split(",")
            cells[-1] = cells[-1].replace("\n", "")
            # order id, customer id, product id, quantity, id cabang
            if cells[0] not in orders.keys():
                r = MasterRelasi.get_relasi(cells[1])
                # list medicine, list quantity, koordinat relasi, id cabang, costumer id
                orders[cells[0]] = [[], [], (r["Latitude"], r["Longitude"]), cells[4], cells[1]]
            tempmed = ProblemGenerator.generate_medicine(cells[2], cells[0], cells[1], 0)
            orders[cells[0]][0].append(copy.deepcopy(tempmed))
            orders[cells[0]][1].append(cells[3])
    
    orders_per_cabang = {}
    for item in orders.items():
        orders_per_cabang[item[1][3]] = []

    for item in orders.items():
        medscopy = []
        for med in range(len(item[1][0])):
            for i in range(int(item[1][1][med])):
                medcopy = copy.deepcopy(item[1][0][med])
                medscopy.append(medcopy)
        orders_per_cabang[item[1][3]].append(Order(item[0], item[1][4], medscopy, item[1][2]))

    cabang_coordinates = {}
    cabang_codes = {}
    for key in orders_per_cabang.keys():
        cabang_coordinates[key] = MasterCabang.get_depot_coordinate(key)
        cabang_codes[key] = MasterCabang.get_depot_code(key)


    
    cabang_coordinates_ret = []
    orders_ret = []
    cabang_codes_ret = []
    for key in orders_per_cabang.keys():
        orders_ret.append(orders_per_cabang[key])
        cabang_coordinates_ret.append(cabang_coordinates[key])
        cabang_codes_ret.append(cabang_codes[key])

    return cabang_coordinates_ret, orders_ret, cabang_codes_ret
    #return cabang_coordinates.values(), orders_per_cabang.values(), cabang_codes.values()




