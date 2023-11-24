from random import seed

from item.box import Box
from data.problem_generator import ProblemGenerator
from vns.saving import saving
from vns.repack import repack
from vns.route_dp import improve_tours_by_dp
from vrp3d.vrp3d import VRP3D

from data.parse_output import parse_output, parse_input
from data.database import Database


def run():
    Database.Initialize()
    

    # map id cabang ke list of order
    o_map = {}
    # map id cabang ke list of vec
    v_map = {}
    
    order_list1 = Database.get_pending_orders()
    for order in order_list1:
        id_cabang = Database.get_by_columns(Database.ORDERS, ["id"], [[order.id]])[0].branch_id
        
        if id_cabang not in o_map.keys():
            o_map[id_cabang] = []
        o_map[id_cabang].append(order)

        if id_cabang not in v_map.keys():
            v_map[id_cabang] = Database.get_available_vehicles_by_branch(id_cabang)


    problems = []
    solutions = []
    
    for k, v in o_map.items():
        depot_coord = Database.get_depots_coords([k])[0]
        order_list = o_map[k]
        vehicle_list = v_map[k]
        cbox_type_list = Database.get_all_duses(100)
        cbox_type_list = sorted(cbox_type_list, key=lambda box: box.volume)    
        for i, order in enumerate(order_list):
            print("Packing order ",i," into cardboxes")
            order_list[i].pack_items_into_cardboard_boxes(cbox_type_list)

        problem = VRP3D(vehicle_list,
                        order_list,
                        depot_coord,
                        k)
        print("START SOLUTION GENERATION")

                        
        solution = saving(problem)
        problem.reset(solution)
        
        solution = improve_tours_by_dp(solution, problem)
        problem.reset(solution)
        
        problems.append(problem)
        solutions.append(solution)

    Database.deliver_orders(problems, solutions)
    parse_output(problems, solutions, Database.get_depots_coords(list(o_map.keys())), list(o_map.keys()))


if __name__ == "__main__":
    seed(20)
    run()