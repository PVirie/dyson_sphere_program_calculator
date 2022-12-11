import numpy as np
from qpsolvers import solve_qp
from scipy import optimize


class MaxIterationReached(Exception):
    pass


class NoSolutionError(Exception):
    pass


class UnboundedProblem(Exception):
    pass


class Numerical(Exception):
    pass


def solve(require_resource_rate, production_speed, allowed_production, target_speed, base_production_cost=None):
    """
    require_resource_rate: num_resource x num_production
    production_speed : num_resource x num_production
    allowed_production : num_production
    target_speed : num_resource
    base_production_cost: num_production

    return a vector that count fabricator units for each resource (num_resource).
    """
    require_resource_rate = np.asarray(require_resource_rate)
    production_speed = np.asarray(production_speed)
    allowed_production = np.asarray(allowed_production)
    target_speed = np.asarray(target_speed)
    num_production = require_resource_rate.shape[1]
    num_resource = require_resource_rate.shape[0]

    if base_production_cost is None:
        c = np.concatenate([np.ones(num_production), np.zeros(num_resource)], axis=0)
    else:
        c = np.concatenate([np.array(base_production_cost) + 1e-2, np.zeros(num_resource)], axis=0)

    A_ub = np.concatenate([np.zeros([num_resource, num_production]), -np.eye(num_resource)], axis=1)
    b_ub = -target_speed

    A_eq = np.concatenate([
    np.reshape(np.concatenate([1.0 - allowed_production, np.zeros(num_resource)], axis=0), [1, -1]),
        np.concatenate([-(production_speed - require_resource_rate), np.eye(num_resource)], axis=1)], axis=0)
    b_eq = np.zeros(1 + num_resource)

    lb = np.zeros(num_production + num_resource)

    res = optimize.linprog(c=c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=[(lower, None) for lower in lb])
    if res.status != 0:
        if res.status == 1:
            raise MaxIterationReached()
        elif res.status == 2:
            raise NoSolutionError()
        elif res.status == 3:
            raise UnboundedProblem()
        elif res.status == 4:
            raise Numerical()

    return res.x[:num_production], res.x[num_production:]


if __name__ == '__main__':

    result, _ = solve(
        [[0, 0, 0, 0, 0], [1, 0, 1, 0, 0], [1, 1, 0, 0, 0]],
        [[1, 0, 0, 0, 0], [0, 1, 0, 1, 0], [0, 0, 1, 0, 1]],
        [1, 1, 0, 0, 1],
        [2, 0, 0])
    print(result)
