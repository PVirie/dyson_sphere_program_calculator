import csv
import solver
import numpy as np


if __name__ == '__main__':
    id_to_index = {}
    require_resource = []
    production_speed = []
    production_machine = []
    index_to_base = []
    with open("resource_table.csv", "r") as file:
        table_reader = csv.reader(file, delimiter=',', quotechar='"')
        next(table_reader)
        for row in table_reader:
            production_machine.append(row[5])
            seconds_per_tick = float(row[4])
            index_to_base.append(seconds_per_tick <= 0)
            if seconds_per_tick <= 0:
                seconds_per_tick = 1
            id = row[0]
            num_per_tick = int(row[1])
            speed = []
            if id not in id_to_index:
                id_to_index[id] = len(id_to_index)
            speed.append((id, num_per_tick / seconds_per_tick))

            alt_id = row[2]
            if alt_id != '':
                alt_num_per_tick = int(row[3])
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
    # target_speed[id_to_index['Universe matrix']] = 1.0
    # target_speed[id_to_index['Small carrier rocket']] = 0.25
    # target_speed[id_to_index['Solar sail']] = 2.0
    target_speed[id_to_index['Assembling machine Mk.II']] = 0.3333
    # target_speed[id_to_index['Sorter Mk.II']] = 2.0
    # target_speed[id_to_index['Conveyor belt Mk.II']] = 3.0

    allowed_bases = ['Iron ore', 'Copper ore', 'Coal', 'Titanium ore', 'Silicon ore', 'Water', 'Sulfuric acid', 'Hydrogen', 'Stone', 'Organic crystal', 'Fire ice', 'Crude oil', 'Critical photon']
    allowed_production = np.ones(len(production_speed))
    for i, p in enumerate(production_speed):
        if index_to_base[i]:
            if p[0][0] not in allowed_bases:
                allowed_production[i] = 0.0

    sol, s = solver.solve(require_resource_matrix, production_speed_matrix, allowed_production, target_speed, minimize_base_resource=True)

    print('=====================')
    for i in range(len(require_resource)):
        if sol[i] > 1e-6:
            print('x', f'{sol[i]:.2f}', 'of', production_machine[i], 'for', end=' ')
            for p in production_speed[i]:
                print(p[0], '(' + f'{p[1]:.2f}' + ')', end=' ')
            print('from', end=' ')
            for r in require_resource[i]:
                print(r[0], '(' + f'{r[1]:.2f}' + ')', end=' ')
            print()
