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
            obj += range(num_production)
                .map((i) => {
                    return `x${i}`;
                })
                .join(" + ");
        } else {
            obj += range(num_production)
                .filter((i) => base_production_cost[i] > 0)
                .map((i) => {
                    return `${base_production_cost[i]} x${i}`;
                })
                .join(" + ");
        }
        // build bounds
        let bounds_production = range(num_production).map((i) => {
            return `0 <= x${i}`;
        });

        let bounds_resource = range(num_resource)
            .filter((i) => {
                return target_speed[i] > 0;
            })
            .map((i) => {
                return `${target_speed[i] > 0 ? target_speed[i] : 0} <= r${i}`;
            });

        // then build constraints

        // sum_i x(i)*allowed_production[i] = 0\n ...
        let allowance_constraints = range(num_production)
            .filter((i) => !allowed_production[i])
            .map((i) => {
                return `x${i} = 0`;
            });

        // sum_j (production_speed[i][j] - require_resource_rate[i][j])*x(j) = r(i)
        let min_constraints = range(num_resource)
            .map((i) => {
                const rows = range(num_production)
                    .filter((j) => Math.abs(production_speed[i][j] - require_resource_rate[i][j]) > 1e-6)
                    .map((j) => {
                        return `${production_speed[i][j] - require_resource_rate[i][j]} x${j}`;
                    });
                if (rows.length == 0) return null;
                return `${rows.join(" + ")} - r${i} = 0`;
            })
            .filter((r) => r != null);

        return {
            obj: obj,
            constraints: allowance_constraints.concat(min_constraints),
            bounds: bounds_production.concat(bounds_resource),
        };
    };

    return {
        build_matrices: build_matrices,
    };
})();
