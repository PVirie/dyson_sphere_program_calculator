op = (function () {
    // require_resource_rate: num_resource x num_production
    // production_speed : num_resource x num_production
    // allowed_production : num_production
    // target_speed : num_resource
    // base_production_cost: num_production

    function range(size, startAt = 0) {
        return [...Array(size).keys()].map((i) => i + startAt);
    }

    const build_matrices = function (require_resource_rate, production_speed, allowed_production, target_speed, base_production_cost = null) {
        const num_production = require_resource_rate[0].length;
        const num_resource = require_resource_rate.length;

        // first build objective function
        // e.g., x1 + 2 x2 + 4 x3 + x4
        let obj = "";
        if (base_production_cost == null) {
            obj += range(num_production, 1).join(" + ");
        } else {
            obj += range(num_production, 1)
                .filter((i) => base_production_cost[i] > 0)
                .map((i) => {
                    return `${base_production_cost[i - 1]} x${i}`;
                })
                .join(" + ");
        }
        // build bounds
        let bounds = range(num_production + num_resource, 1).map((i) => {
            return `x${i} >= 0`;
        });

        // then build constraints
        // x(i+num_production) >= target_speed[i-1]\n ...
        let ineq_constraints = range(num_resource, 1)
            .filter((i) => target_speed[i - 1] > 0)
            .map((i) => {
                return `x${i + num_production} >= ${target_speed[i - 1]}`;
            });

        // sum_i x(i)*allowed_production[i-1] = 0\n ...
        let allowance_constraints = range(num_production, 1)
            .filter((i) => !allowed_production[i - 1])
            .map((i) => {
                return `x${i} = 0`;
            });

        // sum_j (production_speed[i-1][j-1] - require_resource_rate[i-1][j-1])*x(j) = x(i + num_production)
        let min_constraints = range(num_resource, 1)
            .map((i) => {
                const rows = range(num_production, 1)
                    .filter((j) => production_speed[i - 1][j - 1] > 0)
                    .map((j) => {
                        return `${production_speed[i - 1][j - 1] - require_resource_rate[i - 1][j - 1]} x${j}`;
                    });
                if (rows.length == 0) return null;
                return `${rows.join(" + ")} = x${i + num_production}`;
            })
            .filter((r) => r != null);

        return {
            obj: obj,
            constraints: ineq_constraints.concat(allowance_constraints).concat(min_constraints),
            bounds: bounds,
        };
    };

    return {
        build_matrices: build_matrices,
    };
})();
