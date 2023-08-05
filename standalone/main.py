import os
import csv
import solver
import numpy as np

dir_path = os.path.dirname(os.path.realpath(__file__))

if __name__ == '__main__':
    id_to_index = {}
    require_resource = []
    production_speed = []
    production_machine = []
    index_to_base = []
    with open(os.path.join(dir_path, "..", "data/resource_table.csv"), "r") as file:
        table_reader = csv.reader(file, delimiter=',', quotechar='"')
        next(table_reader)
        for row in table_reader:
            production_machine.append(row[5])
            seconds_per_tick = float(row[4])
            if seconds_per_tick <= 0:
                seconds_per_tick = 1
            id = row[0]
            num_per_tick = float(row[1])
            speed = []
            if id not in id_to_index:
                id_to_index[id] = len(id_to_index)
            speed.append((id, num_per_tick / seconds_per_tick))

            alt_id = row[2]
            if alt_id != '':
                alt_num_per_tick = float(row[3])
                if alt_id not in id_to_index:
                    id_to_index[alt_id] = len(id_to_index)
                speed.append((alt_id, alt_num_per_tick / seconds_per_tick))

            production_speed.append(speed)

            resource = []
            for i in range(6, len(row), 2):
                sub_id = row[i]
                if sub_id == '':
                    break
                sub_num_per_tick = int(row[i + 1])
                if sub_id not in id_to_index:
                    id_to_index[sub_id] = len(id_to_index)
                resource.append((sub_id, sub_num_per_tick / seconds_per_tick))

            require_resource.append(resource)
            index_to_base.append(len(resource) == 0)

    # for p, r in zip(production_speed, require_resource):
    #     print(p, r)

    require_resource_matrix = np.zeros([len(id_to_index), len(require_resource)])
    for i, r in enumerate(require_resource):
        for x in r:
            require_resource_matrix[id_to_index[x[0]], i] = x[1]

    production_speed_matrix = np.zeros([len(id_to_index), len(require_resource)])
    for i, r in enumerate(production_speed):
        for x in r:
            production_speed_matrix[id_to_index[x[0]], i] = x[1]

    target_speed = np.zeros(len(id_to_index))
    # target_speed[id_to_index['Universe matrix']] = 10.0
    # target_speed[id_to_index['Small carrier rocket']] = 0.25
    # target_speed[id_to_index['Solar sail']] = 2.0
    target_speed[id_to_index['Sorter Mk.I']] = 1.0
    # target_speed[id_to_index['Sorter Mk.II']] = 0.5
    target_speed[id_to_index['Conveyor belt Mk.I']] = 15.0
    # target_speed[id_to_index['Conveyor belt Mk.II']] = 1.5
    target_speed[id_to_index['Assembling machine Mk.I']] = 0.25
    # target_speed[id_to_index['Assembling machine Mk.II']] = 0.3333
    # target_speed[id_to_index['Arc smelter']] = 0.3333
    # target_speed[id_to_index['Ray receiver']] = 0.125
    # target_speed[id_to_index['Oil refinery']] = 0.16666
    # target_speed[id_to_index['Fractionator']] = 0.3333
    # target_speed[id_to_index['Chemical plant']] = 0.2000
    # target_speed[id_to_index['Matrix lab']] = 0.3333


    allowed_bases = [
        ('Iron ore', 1.0),
        ('Copper ore', 1.0),
        ('Coal', 0.1),
        ('Titanium ore', 1.0),
        ('Silicon ore', 1.0),
        ('Water', 1.0),
        ('Sulfuric acid', 1.0),
        ('Hydrogen', 1.0),
        ('Stone', 1.0),
        ('Fire ice', 1.0),
        ('Critical photon', 1.0),
        ('Crude oil', 1.0),
        ('Organic crystal', 1.0)
    ]
    allowed_production = np.ones(len(production_speed))
    allowed_production[9] = 0.0 # disable Energetic graphite,1,Hydrogen,3,4,Refinery,Refined oil,1,Hydrogen,2,,,,,,,,
    # allowed_production[11] = 0.0 # disable Hydrogen,1,Refined oil,2,4,Refinery,Crude oil,2,,,,,,,,,,
    allowed_production[10] = 0.0 # disable Refined oil,3,,,4,Refinery,Refined oil,2,Hydrogen,1,Coal,1,,,,,,
    allowed_production[6] = 0.0 # disable Graphene,2,,,3,Chemical plant,Energetic graphite,3,Sulfuric acid,1,,,,,,,,
   
    base_production_cost = np.zeros(len(production_speed))
    for i, p in enumerate(production_speed):
        if index_to_base[i]:
            try:
                found = next(x for x in allowed_bases if x[0] == p[0][0])
                base_production_cost[i] = found[1]
            except StopIteration:
                allowed_production[i] = 0.0

    sol, s = solver.solve(require_resource_matrix, production_speed_matrix, allowed_production, target_speed, base_production_cost=base_production_cost)

    sorted_indices = sorted(list(range(len(production_speed))), key = lambda i: production_machine[i])

    print('=====================')
    for j in range(len(production_speed)):
        i = sorted_indices[j]
        if sol[i] > 1e-2:
            print('x', f'{sol[i]:.2f}', 'of', production_machine[i], 'for', end=' ')
            for p in production_speed[i]:
                print(p[0], '(' + f'{p[1]:.2f}' + ')', end=' ')
            print('from', end=' ')
            for r in require_resource[i]:
                print(r[0], '(' + f'{r[1]:.2f}' + ')', end=' ')
            print()
