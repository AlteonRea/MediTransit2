import copy
import csv
import random
from typing import List
from uuid import uuid1

import numpy as np
    
from item.box import Box
from item.cardboard import Cardboard
from item.medicine import Medicine
from order.order import Order
from vehicle.vehicle import create_vehicle
from vrp3d.vrp3d import VRP3D

class MasterRelasi:
    Relasi = {}
    def load_csv():
        with open('data/Master Relasi Modified.csv', newline='') as f:
            reader = csv.reader(f)
            temp = np.array(list(reader))[1:]
            for i in temp:
                MasterRelasi.Relasi[i[1]] = ({
                    "Kode Cabang" : i[0],
                    "Customer Number": i[1],
                    "Alamat" : i[2],
                    "Latitude" : i[3],
                    "Longitude" : i[4],
                    "State" : i[5],
                    "City" : i[6],
                    "Province" : i[7],
                    "Zip Code" : i[8],
                    "Channel" : i[9],
                    "Ship Method Code" : i[10],
                    "Ship Method Desc" : i[11],
                    "Delivery Area Group" : i[12],
                })

    def get_destination_coordinates():
        MasterRelasi.load_csv()
        temp = np.empty([len(MasterRelasi.Relasi)], dtype=object)
        it = 0
        for i in MasterRelasi.Relasi.values():
            temp[it] = (float(i["Latitude"]), float(i["Longitude"]))
            it += 1
        return temp
    
    def get_relasi(customer_number):
        return MasterRelasi.Relasi[customer_number]
    
    def get_random_customer(kode_cabang):
        customers = list(MasterRelasi.Relasi.values())
        customers_of_depot = [cust for cust in customers if cust["Kode Cabang"] ==kode_cabang]
        return random.choice(customers_of_depot)


class MasterCabang:
    Cabang = {}
    def load_csv():
        with open('data/Master Cabang Modified.csv', newline='') as f:
            reader = csv.reader(f)
            temp = np.array(list(reader))[1:]
            for i in temp:
                MasterCabang.Cabang[i[0]] = {
                    "Kode Cabang" : i[1],
                    "Nama Cabang" : i[2],
                    "Alamat" : i[3],
                    "Latitude" : i[4],
                    "Longitude" : i[5],
                }

    def get_depot_coordinates():
        MasterCabang.load_csv()
        temp = np.empty([len(MasterCabang.Cabang)], dtype=object)
        it = 0
        for i in MasterCabang.Cabang.values():
            temp[it] = (float(i["Latitude"]), float(i["Longitude"]))
            it += 1
        return temp
    
    def get_depot_coordinate(id_cabang):
        return (float(MasterCabang.Cabang[id_cabang]["Latitude"]), float(MasterCabang.Cabang[id_cabang]["Longitude"]))
    
    def get_depot_code(id_cabang):
        return MasterCabang.Cabang[id_cabang]["Kode Cabang"]


class MasterProduk:
    Produk = {}
    def load_csv():
        with open('data/Master Produk Modified.csv', newline='') as f:
            reader = csv.reader(f)
            temp = np.array(list(reader))[1:]
            for i in temp:
                MasterProduk.Produk[i[0]] = {
                    "HNA" : i[1],
                    "HET" : i[2],
                    "UOM" : i[3],
                    "Berat Gram" : i[4],
                    "Panjang Cm" : i[5],
                    "Lebar Cm" : i[6],
                    "Tinggi Cm" : i[7],
                    "Is Life Saving" : i[8],
                    "Volume Cm3" : i[9],
                    "Kategori Pengiriman" : i[10],
                }

    def get_product(product_code):
        return MasterProduk.Produk[product_code]
    
    def get_random_product():
        return random.choice(list(MasterProduk.Produk.items()))

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

class MasterKendaraan:
    Kendaraan = {}
    def load_csv():
        with open('data/Master Kendaraan.csv', newline='') as f:
            reader = csv.reader(f)
            temp = np.array(list(reader))[1:]
            for i in temp:
                MasterKendaraan.Kendaraan[i[0]] = {
                    "Jenis Kendaraan" : i[1],
                    "Max Berat Gram" : i[2],
                    "Panjang Cm" : i[3],
                    "Lebar Cm" : i[4],
                    "Tinggi Cm" : i[5],
                    "Kategori Pengiriman" : i[6],
                    "Cost Per KG" : i[7],
                    "Cost Per KM" : i[8],
                    "Vendor" : i[9],
                    "Max Duration" : i[10]
                }

    def get_vehicle(vehicle_code):
        return MasterKendaraan.Kendaraan[vehicle_code]
    
    def get_random_vehicle():
        return random.choice(list(MasterKendaraan.Kendaraan.items()))
    

class MasterDus:
    Dus = {}
    def load_csv():
        with open('data/Master Dus.csv', newline='') as f:
            reader = csv.reader(f)
            temp = np.array(list(reader))[1:]
            for i in temp:
                MasterDus.Dus[i[0]] = {
                    "Kode Dus" : i[0],
                    "Panjang Cm" : i[1],
                    "Lebar Cm" : i[2],
                    "Tinggi Cm" : i[3],
                    "Volume" : i[5],
                    "Max Berat Gram" : i[5],
                    "Details": i[6]
                }

    def get_dus(dus_code):
        return MasterDus.Dus[dus_code]
    

    

class MapData:
    Vertices = []
    DepotIndices = []

    def initialize():
        depot_coordinates = MasterCabang.get_depot_coordinates()
        destination_coordinates = MasterRelasi.get_destination_coordinates()
        MasterDus.load_csv()

        for i in range(len(depot_coordinates)):
            MapData.DepotIndices.append(i)

        MapData.Vertices = np.concatenate((depot_coordinates, destination_coordinates))


   



class ProblemGenerator:

    KENDARAAN_COUNTER = 0
    ORDER_COUNTER = 0
    CUSTOMER_COUNTER = 0

    def initialize():
        MasterProduk.load_csv()
        MasterKendaraan.load_csv()
        MapData.initialize()


    def get_random_destination_index():
        return random.randint(len(MapData.DepotIndices), len(MapData.Vertices) - 1)
    
    def get_random_destination():
        return MapData.Vertices[ProblemGenerator.get_random_destination_index()]
    
    def get_random_depot_index():
        return random.randint(0, len(MapData.DepotIndices) - 1)
    
    def get_random_depot():
        depots = list(MasterCabang.Cabang.values())
        depot = depots[ProblemGenerator.get_random_depot_index()]
        coord = [depot["Latitude"], depot["Longitude"]]
        kode_cabang = depot["Kode Cabang"]
        return kode_cabang, coord


    def generate_random_medicine_nocus():
        return ProblemGenerator.generate_random_medicine(str(uuid1()),str(uuid1()),str(uuid1()))

    def generate_random_medicines_nocus(number_of_medicines):
        return [ProblemGenerator.generate_random_medicine_nocus() for i in range(number_of_medicines)]
    
    def generate_medicine(product_id, order_id, customer_id, number):
        medt = MasterProduk.get_product(product_id)
        med = copy.deepcopy(medt)
        size0 = int(float(med["Panjang Cm"].replace(',', '')))
        size1 = int(float(med["Lebar Cm"].replace(',', '')))
        size2 = int(float(med["Tinggi Cm"].replace(',', '')))
        '''
        while size0 == 0 or size1 == 0 or size2 == 0:
            med = MasterProduk.get_product(product_id)
            size0 = int(float(med["Panjang Cm"].replace(',', '')))
            size1 = int(float(med["Lebar Cm"].replace(',', '')))
            size2 = int(float(med["Tinggi Cm"].replace(',', '')))
        '''
        return Medicine(str(order_id), str(customer_id), product_id, number, med["UOM"], (size0, size1, size2), int(float(med["Berat Gram"].replace(',', ''))), TEMP_CLASS[med["Kategori Pengiriman"]])
    
    def generate_random_medicine(order_id, customer_id, number): 
        medp = MasterProduk.get_random_product()
        med = medp[1]
        size0 = int(float(med["Panjang Cm"].replace(',', '')))
        size1 = int(float(med["Lebar Cm"].replace(',', '')))
        size2 = int(float(med["Tinggi Cm"].replace(',', '')))
        while size0 == 0 or size1 == 0 or size2 == 0:
            medp = MasterProduk.get_random_product()
            med = medp[1]
            size0 = int(float(med["Panjang Cm"].replace(',', '')))
            size1 = int(float(med["Lebar Cm"].replace(',', '')))
            size2 = int(float(med["Tinggi Cm"].replace(',', '')))
        size = np.asanyarray([size0,size1,size2], dtype=np.int64)
        return Medicine(str(order_id), str(customer_id), str(medp[0]), number, med["UOM"], size, int(float(med["Berat Gram"].replace(',', ''))), TEMP_CLASS[med["Kategori Pengiriman"]])
    
    def generate_random_medicines(number_of_medicines, order_id, customer_id, number):
        return [ProblemGenerator.generate_random_medicine(order_id, customer_id, number) for i in range(number_of_medicines)]


    def generate_random_order(max_each_quantity, max_total_quantity, kode_cabang):
        customer = MasterRelasi.get_random_customer(kode_cabang)
        customer_id = customer["Customer Number"]
        customer_coords = (float(customer["Latitude"]), float(customer["Longitude"]))
        items = []
        sum_quantity = 0
        ProblemGenerator.ORDER_COUNTER += 1
        while sum_quantity < max_total_quantity:
            current_quantity = min(max_total_quantity - sum_quantity, random.randint(1, max_each_quantity))
            sum_quantity += current_quantity
            med = ProblemGenerator.generate_random_medicine(ProblemGenerator.ORDER_COUNTER, customer_id, 0)
            for i in range(current_quantity):
                new_med = copy.deepcopy(med)
                new_med.number = i
                items.append(copy.deepcopy(new_med))
        return Order(ProblemGenerator.ORDER_COUNTER, customer_id, items, customer_coords)

    def generate_random_orders(number_of_orders, max_each_quantity, max_total_quantity, kode_cabang):
        return [ProblemGenerator.generate_random_order(max_each_quantity, max_total_quantity, kode_cabang) for i in range(number_of_orders)]

    def generate_random_vehicle():
        temp = MasterKendaraan.get_random_vehicle()[1]
        size0, size1, size2 = int(float(temp["Panjang Cm"])), int(float(temp["Lebar Cm"])), int(float(temp["Tinggi Cm"]))
        size = np.asanyarray([size0,size1,size2], dtype=np.int64)
        ProblemGenerator.KENDARAAN_COUNTER += 1
        return create_vehicle(temp["Vendor"], size, int(float(temp["Max Berat Gram"])), int(float(temp["Cost Per KM"])), int(float(temp["Cost Per KG"])), TEMP_CLASS[temp["Kategori Pengiriman"]], int(float(temp["Max Duration"])), temp["Jenis Kendaraan"], ProblemGenerator.KENDARAAN_COUNTER)


    def generate_random_vehicles(number_of_vehicles):
        return [ProblemGenerator.generate_random_vehicle() for i in range(number_of_vehicles)]
    
    def get_random_dus():
        temp = random.choice(list(MasterDus.Dus.items()))[1]
        size0,size1,size2 = int(float(temp["Panjang Cm"])), int(float(temp["Lebar Cm"])), int(float(temp["Tinggi Cm"]))
        size = np.asanyarray([size0,size1,size2], dtype=np.int64)
        return Box(size, int(float(temp["Max Berat Gram"])), temp["Kode Dus"])
    
    def get_random_duses(number_of_duses):
        return [ProblemGenerator.get_random_dus() for i in range(number_of_duses)]

    def get_all_duses(num_each_dus_size=100) -> List[Cardboard]:
        all_dustype_list = list(MasterDus.Dus.values())
        duses = []
        for i in range(len(all_dustype_list)):
            dustype = all_dustype_list[i]
            for j in range(num_each_dus_size):
                size0,size1,size2 = int(float(dustype["Panjang Cm"])), int(float(dustype["Lebar Cm"])), int(float(dustype["Tinggi Cm"]))
                size = np.asanyarray([size0,size1,size2], dtype=np.int64)
                code = dustype["Kode Dus"]
                details = dustype["Details"]
                dus = Cardboard(code, details, size, int(float(dustype["Max Berat Gram"])))
                duses += [dus]
        return duses


    def generate_problem(number_of_vehicles, number_of_orders, max_each_quantity, max_total_quantity):
        return VRP3D(ProblemGenerator.generate_random_vehicles(number_of_vehicles), ProblemGenerator.generate_random_orders(number_of_orders, max_each_quantity, max_total_quantity), MapData.get_random_depot())