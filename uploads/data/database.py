import copy
import csv
import random
from typing import List, Tuple
from uuid import uuid1
from datetime import datetime

import numpy as np
    
from item.box import Box
from item.cardboard import Cardboard
from item.medicine import Medicine
from order.order import Order
from vehicle.vehicle import create_vehicle
from vrp3d.vrp3d import VRP3D

import re


import mysql.connector

TEMP_COLD = 0
TEMP_CHILL_LOW = 1
TEMP_CHILL_HIGH = 2
TEMP_ROOM = 3

TEMP_CLASS = {
    "01" : TEMP_COLD,
    "02-A" : TEMP_CHILL_LOW,
    "02-B" : TEMP_CHILL_HIGH,
    "03" : TEMP_ROOM,
    "1" : TEMP_COLD,
    "2-A" : TEMP_CHILL_LOW,
    "2-B" : TEMP_CHILL_HIGH,
    "3" : TEMP_ROOM,
}


class DBRelation:
    def __init__(self, db_result: Tuple):
        self.id = db_result[0]
        self.branch_id = db_result[1]
        self.number = db_result[2]
        self.latitude = db_result[3]
        self.longitude = db_result[4]
        self.address = db_result[5]
        self.city = db_result[6]
        self.state = db_result[7]
        self.province = db_result[8]
        self.zip_code = db_result[9]
        self.channel = db_result[10]
        self.ship_method_code = db_result[11]
        self.ship_method_desc = db_result[12]
        self.delivery_area_group = db_result[13]

    def dump(self):
        return (
            self.id,
            self.branch_id,
            self.number,
            self.latitude,
            self.longitude,
            self.address,
            self.city,
            self.state,
            self.province,
            self.zip_code,
            self.channel,
            self.ship_method_code,
            self.ship_method_desc,
            self.delivery_area_group
        )



class DBBranch:
    def __init__(self, db_result: Tuple):
        self.id = db_result[0]
        self.code = db_result[1]
        self.name = db_result[2]
        self.address = db_result[3]
        self.latitude = db_result[4]
        self.longitude = db_result[5]

    def dump(self):
        return (
            self.id,
            self.code,
            self.name,
            self.address,
            self.latitude,
            self.longitude
        )


class DBProduct:
    def __init__(self, db_result: Tuple):
        self.id = db_result[0]
        self.code = db_result[1]
        self.HNA = db_result[2]
        self.HET = db_result[3]
        self.UOM = db_result[4]
        self.weight = db_result[5]
        self.length = db_result[6]
        self.width = db_result[7]
        self.height = db_result[8]
        self.is_life_saving = db_result[9]
        self.volume = db_result[10],
        self.delivery_category = db_result[11]

    def dump(self):
        return (
            self.id,
            self.code,
            self.HNA,
            self.HET,
            self.UOM,   
            self.weight,
            self.length,
            self.width,
            self.height,
            self.is_life_saving,
            self.volume,
            self.delivery_category
        )



class DBVehicle:
    def __init__(self, db_result: Tuple):
        self.id = db_result[0]
        self.type = db_result[1]
        self.max_weight = db_result[2]
        self.length = db_result[3]
        self.width = db_result[4]
        self.height = db_result[5]
        self.delivery_category = db_result[6]
        self.cost_per_kg = db_result[7]
        self.cost_per_km = db_result[8]
        self.vendor = db_result[9]
        self.max_duration = db_result[10]
        self.driver_id = db_result[11]
        self.branch_id = db_result[12]

    def dump(self):
        return (
            self.id,
            self.type,
            self.max_weight,
            self.length,
            self.width,
            self.height,
            self.delivery_category,
            self.cost_per_kg,
            self.cost_per_km,
            self.vendor,
            self.max_duration,
            self.driver_id,
            self.branch_id
        )


    

class DBCardboardBox:
    def __init__(self, db_result: Tuple):
        self.id = db_result[0]
        self.code = db_result[1]
        self.length = db_result[2]
        self.width = db_result[3]
        self.height = db_result[4]
        self.volume = db_result[5]
        self.max_weight = db_result[6]
        self.details = db_result[7]

    def dump(self):
        return (
            self.id,
            self.code,
            self.length,
            self.width,
            self.height,
            self.volume,
            self.max_weight,
            self.details
        )


    

class DBDeliveryCategory:
    def __init__(self, db_result: Tuple):
        self.delivery_category = db_result[0]
        self.temperature_detail = db_result[1]
        self.temperature_min = db_result[2]
        self.temperature_max = db_result[3]

    def dump(self):
        return (
            self.delivery_category,
            self.temperature_detail,
            self.temperature_min,
            self.temperature_max
        )

class DBDriver:
    def __init__(self, db_result: Tuple):
        self.id = db_result[0]
        self.name = db_result[1]

    def dump(self):
        return (
            self.id,
            self.name
        )

class DBAvailableVehicle:
    def __init__(self, db_result: Tuple):
        self.id = db_result[0]
        self.vehicle_id = db_result[1]
        self.available_date = db_result[2]

    def dump(self):
        return (
            self.id,
            self.vehicle_id,
            self.available_date,
        )

class DBShipment:
    def __init__(self, db_result: Tuple):
        self.id = db_result[0]
        self.vehicle_id = db_result[1]
        self.branch_id = db_result[2]
        self.dispatch_date = db_result[3]
        self.status = db_result[4]
        self.distance_cost = db_result[5]
        self.weight_cost = db_result[6]

    def dump(self):
        return (
            self.id,
            self.vehicle_id,
            self.branch_id,
            self.dispatch_date,
            self.status,
            self.distance_cost,
            self.weight_cost
        )

class DBOrders:
    def __init__(self, db_result: Tuple):
        self.id = db_result[0]
        self.relation_id = db_result[1]
        self.branch_id = db_result[2]
        self.shipment_id = db_result[3]
        self.status = db_result[4]

    def dump(self):
        return (
            self.id,
            self.relation_id,
            self.branch_id,
            self.shipment_id,
            self.status
        )

class DBOrderDetail:
    def __init__(self, db_result: Tuple):
        self.order_id = db_result[0]
        self.product_id = db_result[1]
        self.quantity = db_result[2]

    def dump(self):
        return (
            self.order_id,
            self.product_id,
            self.quantity
        )
    
class DBOrderDetailMishap:
    def __init__(self, db_result: Tuple):
        self.order_id = db_result[0]
        self.product_id = db_result[1]
        self.quantity_delivered = db_result[2]

    def dump(self):
        return (
            self.order_id,
            self.product_id,
            self.quantity_delivered
        )

class DBRouteData:
    def __init__(self, db_result: Tuple):
        self.id = db_result[0]
        self.relation_id = db_result[1]
        self.shipment_id = db_result[2]
        self.visitation_order = db_result[3]
        self.departure_time = db_result[4]
        self.delivered_time = db_result[5]

    def dump(self):
        return (
            self.id,
            self.relation_id,
            self.shipment_id,
            self.visitation_order,
            self.departure_time,
            self.delivered_time
        )

class DBDeliveryTrouble:
    def __init__(self, db_result: Tuple):
        self.id = db_result[0]
        self.vehicle_id = db_result[1]
        self.trouble_type = db_result[2]
        self.details = db_result[3]
        self.status = db_result[4]
        self.event_time = db_result[5]

    def dump(self):
        return (
            self.id,
            self.vehicle_id,
            self.trouble_type,
            self.details,
            self.status,
            self.event_time
        )




class Database:
    Database = None
    Cursor = None

    RELATION = "RELATION"
    BRANCH = "BRANCH"
    PRODUCT = "PRODUCT"
    VEHICLE = "VEHICLE"
    CARDBOARD_BOX = "CARDBOARDBOX"
    DELIVERY_CATEGORY = "DELIVERYCATEGORY"
    DRIVER = "DRIVER"
    AVAILABLE_VEHICLE = "AVAILABLEVEHICLE"
    SHIPMENT = "SHIPMENT"
    ORDERS = "ORDERS"
    ORDER_DETAIL = "ORDERDETAIL"
    ROUTE_DATA = "ROUTEDATA"
    DELIVERY_TROUBLE = "DELIVERYTROUBLE"

    DBType = {
        RELATION : DBRelation,
        BRANCH : DBBranch,
        PRODUCT : DBProduct,
        VEHICLE : DBVehicle,
        CARDBOARD_BOX : DBCardboardBox,
        DELIVERY_CATEGORY : DBDeliveryCategory,
        DRIVER : DBDriver,
        AVAILABLE_VEHICLE : DBAvailableVehicle,
        SHIPMENT : DBShipment,
        ORDERS : DBOrders,
        ORDER_DETAIL : DBOrderDetail,
        ROUTE_DATA : DBRouteData,
        DELIVERY_TROUBLE : DBDeliveryTrouble
    }

    DRIVER_ID = "DRIVER_ID"
    ORDER_ID = "ORDER_ID"
    PRODUCT_ID = "PRODUCT_ID"
    RELATION_ID = "RELATION_ID"
    SHIPMENT_ID = "SHIPMENT_ID"
    BRANCH_ID = "BRANCH_ID"


    def Initialize():
        Database.Database = mysql.connector.connect(
            host="localhost",
            user="MediTransit",
            password="MedTrans", 
            database='MediTransit',
            auth_plugin='mysql_native_password'
        )
        
        Database.Cursor = Database.Database.cursor()

    def Rebuild():
        fd = open('data/MediTransitInit.sql', 'r')
        sqlFile = fd.read()
        fd.close()

        sqlCommands = sqlFile.split(';')

        for command in sqlCommands:
            Database.Cursor.execute(command)
        Database.Database.commit()
        

    def dump_to_database(table, entries):
        for entry in entries:
            temp = ""
            for attr in entry:
                if attr is not None:
                    temp += "'" + str(attr) + "',"
                else:
                    temp += "NULL,"
            Database.Cursor.execute(f"insert into {table} values ({temp[:-1]})")
        Database.Database.commit()

    def get_all(table):
            Database.Cursor.execute(f"select * from {table}")
            myresult = Database.Cursor.fetchall()
            
            ret = []
            for res in myresult:
                ret.append(Database.DBType[table](res))

            return ret
    
    def get_by_ids(table, ids):
        temp = ""
        for id in ids:
            temp += "'" + str(id) + "',"
        Database.Cursor.execute(f"select * from {table} where id in ({temp[:-1]})")
        myresult = Database.Cursor.fetchall()
        
        ret = []
        for res in myresult:
            ret.append(Database.DBType[table](res))

        return ret
    
    def get_max_id(table):
        Database.Cursor.execute(f"select max(id) from {table}")
        myresult = Database.Cursor.fetchall()[0][0]
        if myresult is None:
            myresult = 0

        return myresult
    

    def get_by_columns(table, column_strings, columns):
        temp = ""
        for i, column_string in enumerate(column_strings):
            temp += column_string + " in (" 
            for column in columns[i]:
                temp += "'" + str(column) + "',"
            temp = temp[:-1] + ") and "
        temp = temp[:-6] + ")"
        Database.Cursor.execute(f"select * from {table} where {temp}")
        myresult = Database.Cursor.fetchall()
        
        ret = []
        for res in myresult:
            ret.append(Database.DBType[table](res))

        return ret
    

    def update(table, column_strings, columns, new_columns, new_values):
        temp2 = ""
        for i, new_col in enumerate(new_columns):
            temp2 += new_col + "='" + str(new_values[i]) + "',"
        temp2 = temp2[:-1]

        temp = ""
        for i, column_string in enumerate(column_strings):
            temp += column_string + " in (" 
            for column in columns[i]:
                temp += "'" + str(column) + "',"
            temp = temp[:-1] + ") and "
        temp = temp[:-6] + ")"
        Database.Cursor.execute(f"update {table} set {temp2} where {temp}")
        Database.Database.commit()
    

    def delete(table, column_strings, columns):
        temp = ""
        for i, column_string in enumerate(column_strings):
            temp += column_string + " in (" 
            for column in columns[i]:
                temp += "'" + str(column) + "',"
            temp = temp[:-1] + ") and "
        temp = temp[:-6] + ")"
        Database.Cursor.execute(f"delete from {table} where {temp}")
        Database.Database.commit()

    def random_depot():
        depot = random.choice(Database.get_all(Database.BRANCH))
        coord = [depot.latitude, depot.longitude]
        return depot.id, coord
    
    def get_depots_coords(ids):
        depot = Database.get_by_ids(Database.BRANCH, ids)
        ret = [(d.latitude, d.longitude) for d in depot]
        return ret

    
    def get_medicine(product_id, order_id, customer_id, number):
        med = Database.get_by_ids(Database.PRODUCT, [product_id])[0]
        size = np.asanyarray([med.length,med.width,med.height], dtype=np.int64)
        return Medicine(med.id, str(order_id), str(customer_id), str(med.id), number, med.UOM, size, int(float(med.weight)), TEMP_CLASS[med.delivery_category])
    

    def random_medicine(order_id, customer_id, number): 
        med = random.choice(Database.get_all(Database.PRODUCT))
        size = np.asanyarray([med.length,med.width,med.height], dtype=np.int64)
        return Medicine(med.id, str(order_id), str(customer_id), str(med.id), number, med.UOM, size, int(float(med.weight)), TEMP_CLASS[med.delivery_category])
    
    def random_medicines(number_of_medicines, order_id, customer_id, number):
        return [Database.random_medicine(order_id, customer_id, number) for i in range(number_of_medicines)]

    def generate_random_order(max_each_quantity, max_total_quantity):
        customer = random.choice(Database.get_all(Database.RELATION))
        sum_quantity = 0
        last_order_id = Database.get_max_id(Database.ORDERS) + 1

        db_order = (last_order_id, customer.id, customer.branch_id, None, "Pending")

        Database.dump_to_database(Database.ORDERS, [db_order])
        while sum_quantity < max_total_quantity:
            current_quantity = min(max_total_quantity - sum_quantity, random.randint(1, max_each_quantity))
            sum_quantity += current_quantity
            med = Database.random_medicine(last_order_id, customer.id, 0)
            db_orderdetail = (last_order_id, med.id, current_quantity)
            Database.dump_to_database(Database.ORDER_DETAIL, [db_orderdetail])

    def generate_random_orders(number_of_orders, max_each_quantity, max_total_quantity):
        return [Database.generate_random_order(max_each_quantity, max_total_quantity) for i in range(number_of_orders)]

    def get_pending_orders():
        db_orders = Database.get_by_columns(Database.ORDERS, ["status"], [["Pending", "Not-Sent"]])
        orders = []
        for db_order in db_orders:
            db_orderdetails =  Database.get_by_columns(Database.ORDER_DETAIL, ["order_id"], [[db_order.id]])
            meds = []
            it = 1
            for db_orderdetail in db_orderdetails:
                med = Database.get_by_columns(Database.PRODUCT, ["id"], [[db_orderdetail.product_id]])[0]
                size = np.asanyarray([med.length,med.width,med.height], dtype=np.int64)
                medtemp = Medicine(med.id, str(db_order.id), str(db_order.relation_id), str(med.id), it, med.UOM, size, int(float(med.weight)), TEMP_CLASS[med.delivery_category])
                for k in range(db_orderdetail.quantity):
                    medtemp2 = copy.deepcopy(medtemp)
                    medtemp2.number = it
                    it += 1
                    meds.append(medtemp2)
            db_customer = Database.get_by_columns(Database.RELATION, ["id"], [[db_order.relation_id]])[0]
            orders.append(Order(db_order.id, db_order.relation_id, meds, (db_customer.latitude, db_customer.longitude)))

        return orders



    
    def random_dus():
        dus = random.choice(Database.get_all(Database.CARDBOARD_BOX))
        size = np.asanyarray([dus.length,dus.width,dus.height], dtype=np.int64)
        return Box(size, dus.max_weight, dus.code)
    
    def random_duses(number_of_duses):
        return [Database.random_dus() for i in range(number_of_duses)]

    def get_all_duses(num_each_dus_size=100) -> List[Cardboard]:
        all_dustype_list = Database.get_all(Database.CARDBOARD_BOX)
        duses = []
        for i in range(len(all_dustype_list)):
            dustype = all_dustype_list[i]
            for j in range(num_each_dus_size):
                size = np.asanyarray([dustype.length,dustype.width,dustype.height], dtype=np.int64)
                dus = Cardboard(dustype.id, dustype.code, dustype.details, size, dustype.max_weight)
                duses += [dus]
        return duses


    def generate_available_vehicles(number_of_vehicle):
        vehicles = []
        Database.Cursor.execute(f"select * from Vehicle where Vehicle.id not in (select vehicle_id from AvailableVehicle)")
        myresult = Database.Cursor.fetchall()
        
        vehicles = []
        for res in myresult:
            vehicles.append(DBVehicle(res))

        #vehicles = Database.get_all(Database.VEHICLE)
        
        random.shuffle(vehicles)
        generated_vehicles = vehicles[:number_of_vehicle]

        last_avail_vehicle_id = Database.get_max_id(Database.AVAILABLE_VEHICLE) + 1
        for vehicle in generated_vehicles:
            avail_vehicle = DBAvailableVehicle((last_avail_vehicle_id, vehicle.id, datetime.now())).dump()
            last_avail_vehicle_id += 1
            Database.dump_to_database(Database.AVAILABLE_VEHICLE, [avail_vehicle])

    def get_available_vehicles():
        vehicles = Database.get_all(Database.AVAILABLE_VEHICLE)
        vehicles2 = Database.get_by_columns(Database.VEHICLE, ["ID"], [[vec.vehicle_id for vec in vehicles]])
        vecs = [create_vehicle(vec.vendor, np.asanyarray([vec.length,vec.width,vec.height], dtype=np.int64), 
                               vec.max_weight, vec.cost_per_km, vec.cost_per_kg, TEMP_CLASS[vec.delivery_category], vec.max_duration, vec.type, vec.id) for vec in vehicles2]
        return vecs
        
    def get_available_vehicles_by_branch(branch_id):
        vehicles = Database.get_all(Database.AVAILABLE_VEHICLE)
        vehicles2 = Database.get_by_columns(Database.VEHICLE, ["ID"], [[vec.vehicle_id for vec in vehicles]])
        vehicles3 = []
        for vec in vehicles2:
            if vec.branch_id == branch_id:
                vehicles3.append(vec)
        vecs = [create_vehicle(vec.vendor, np.asanyarray([vec.length,vec.width,vec.height], dtype=np.int64), 
                               vec.max_weight, vec.cost_per_km, vec.cost_per_kg, TEMP_CLASS[vec.delivery_category], vec.max_duration, vec.type, vec.id) for vec in vehicles3]
        return vecs


    def get_fast_moving_products():
        Database.Cursor.execute(f"select Product.id, Product.code, Product.HNA, Product.HET, Product.UOM, Product.weight, \
                                Product.length, Product.width, Product.height, Product.is_life_saving, Product.volume, Product.delivery_category, count(*) \
                                from Product inner join OrderDetail on Product.id = OrderDetail.product_id \
                                group by Product.id order by count(*)")
        myresult = Database.Cursor.fetchall()
        
        ret = []
        for res in myresult:
            ret.append((Database.DBType[Database.PRODUCT](res[:-1]), res[-1]))

        for res in ret:
            print(res[0], res[1])

        return ret
    
    def deliver_orders(problems, solutions):
        for i in range(len(solutions)):
            solution = solutions[i]
            problem = problems[i]
            branch_id = problem.depot_id
            last_do_id = Database.get_max_id(Database.SHIPMENT) + 1
            last_route_data_id = Database.get_max_id(Database.ROUTE_DATA) + 1
            for j in range(solution.num_vehicle):
                c_tour_list = solution.tour_list[j]
                if len(c_tour_list) == 0:
                   continue
                vec = problem.vehicle_list[j]
                db_do = DBShipment((last_do_id, vec.id, branch_id, datetime.now(), "On-Delivery", problem.distance_cost_list[j], problem.weight_cost_list[j]))
                Database.dump_to_database(Database.SHIPMENT, [db_do.dump()])
                last_do_id += 1

                Database.delete(Database.AVAILABLE_VEHICLE, ["vehicle_id"], [[int(vec.id)]])

                k = 1
                for tour in c_tour_list:
                    order = problem.order_list[tour]
                    Database.update(Database.ORDERS, ["id"], [[int(order.id)]], ["status", "shipment_id"], ["On-Delivery", db_do.id])

                    Database.dump_to_database(Database.ROUTE_DATA, [DBRouteData((last_route_data_id, order.customer_id, db_do.id, k, None, None)).dump()])
                    k += 1
                    last_route_data_id += 1
        
        # change the status of unsent orders to "Not-Sent"
        Database.update(Database.ORDERS, ["status"], [["Pending"]], ["status"], ["Not-Sent"])


    #def generate_problem(number_of_vehicles, number_of_orders, max_each_quantity, max_total_quantity):
    #    return VRP3D(ProblemGenerator.generate_random_vehicles(number_of_vehicles), ProblemGenerator.generate_random_orders(number_of_orders, max_each_quantity, max_total_quantity), MapData.get_random_depot())
        