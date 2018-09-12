from itertools import groupby


MONTHLY_SPEND_AARDVARK = {
    "LC04": {
        "Integ": {
            "10/2018": 284,
            "11/2018": 1210,
            "12/2018": 1430,
            "01/2019": 1366,
            "02/2019": 1169,
            "03/2019": 991,
            "04/2019": 978,
            "05/2019": 737,
        },
        "PreProd": {
            "10/2018": 812,
            "11/2018": 1389,
            "12/2018": 1425,
            "01/2019": 1306,
            "02/2019": 1112,
            "03/2019": 936,
            "04/2019": 921,
            "05/2019": 694,
        },
        "Prod": {
            "10/2018": 1742,
            "11/2018": 1716,
            "12/2018": 1866,
            "01/2019": 1809,
            "02/2019": 1839,
            "03/2019": 1633,
            "04/2019": 1654,
            "05/2019": 1103,
        },
    },
    "SF18": {
        "Integ": {
            "12/2018": 1498,
            "01/2019": 1400,
            "02/2019": 1394,
            "03/2019": 1171,
            "04/2019": 1200,
            "05/2019": 963,
        },
        "PreProd": {
            "12/2018": 1780,
            "01/2019": 1667,
            "02/2019": 1703,
            "03/2019": 1474,
            "04/2019": 1441,
            "05/2019": 933,
        },
        "Prod": {
            "12/2018": 1686,
            "01/2019": 1779,
            "02/2019": 1792,
            "03/2019": 1570,
            "04/2019": 1539,
            "05/2019": 986,
        },
    },
    "Canton": {
        "Prod": {
            "01/2019": 28699,
            "02/2019": 26766,
            "03/2019": 22619,
            "04/2019": 24090,
            "05/2019": 16719,
        }
    },
    "BD04": {
        "Integ": {},
        "PreProd": {
            "10/2018": 7019,
            "11/2018": 3004,
            "12/2018": 2691,
            "01/2019": 2901,
            "02/2019": 3463,
            "03/2019": 3314,
            "04/2019": 3432,
            "05/2019": 723,
        },
    },
    "SCV18": {"Dev": {"05/2019": 9797}},
    "Crown": {
        "CR Portal Dev": {
            "11/2018": 208,
            "12/2018": 457,
            "01/2019": 671,
            "02/2019": 136,
            "03/2019": 1524,
            "04/2019": 2077,
            "05/2019": 1858,
        },
        "CR Staging": {
            "11/2018": 208,
            "12/2018": 457,
            "01/2019": 671,
            "02/2019": 136,
            "03/2019": 1524,
            "04/2019": 2077,
            "05/2019": 1858,
        },
        "CR Portal Test 1": {"03/2019": 806, "04/2019": 1966, "05/2019": 2597},
        "Jewels Prod": {"03/2019": 806, "04/2019": 1966, "05/2019": 2597},
        "Jewels Dev": {
            "11/2018": 145,
            "12/2018": 719,
            "01/2019": 1243,
            "02/2019": 2214,
            "03/2019": 2959,
            "04/2019": 4151,
            "05/2019": 4260,
        },
    },
}

CUMULATIVE_BUDGET_AARDVARK = {
    "10/2018": {"spend": 9857, "cumulative": 9857},
    "11/2018": {"spend": 7881, "cumulative": 17738},
    "12/2018": {"spend": 14010, "cumulative": 31748},
    "01/2019": {"spend": 43510, "cumulative": 75259},
    "02/2019": {"spend": 41725, "cumulative": 116984},
    "03/2019": {"spend": 41328, "cumulative": 158312},
    "04/2019": {"spend": 47491, "cumulative": 205803},
    "05/2019": {"spend": 45826, "cumulative": 251629},
    "06/2019": {"projected": 296511},
    "07/2019": {"projected": 341393},
    "08/2019": {"projected": 386274},
    "09/2019": {"projected": 431156},
}

MONTHLY_SPEND_BELUGA = {
    "NP02": {
        "Integ": {"02/2019": 284, "03/2019": 1210},
        "PreProd": {"02/2019": 812, "03/2019": 1389},
        "Prod": {"02/2019": 3742, "03/2019": 4716},
    },
    "FM": {"Integ": {"03/2019": 1498}, "Prod": {"03/2019": 5686}},
}

CUMULATIVE_BUDGET_BELUGA = {
    "02/2019": {"spend": 4838, "cumulative": 4838},
    "03/2019": {"spend": 14500, "cumulative": 19338},
    "04/2019": {"projected": 29007},
    "05/2019": {"projected": 38676},
    "06/2019": {"projected": 48345},
    "07/2019": {"projected": 58014},
    "08/2019": {"projected": 67683},
    "09/2019": {"projected": 77352},
}


class Reports:
    @classmethod
    def workspace_totals(cls, alternate):
        data = MONTHLY_SPEND_BELUGA if alternate else MONTHLY_SPEND_AARDVARK
        spent = sum(
            [
                spend
                for project in data.values()
                for env in project.values()
                for spend in env.values()
            ]
        )
        budget = 70_000 if alternate else 500_000
        return {"budget": budget, "spent": spent}

    @classmethod
    def monthly_totals(cls, alternate):
        data = MONTHLY_SPEND_BELUGA if alternate else MONTHLY_SPEND_AARDVARK
        project_totals = {}
        for project, environments in data.items():
            project_spend = [
                (month, spend)
                for env in environments.values()
                for month, spend in env.items()
            ]
            project_totals[project] = {
                month: sum([spend[1] for spend in spends])
                for month, spends in groupby(sorted(project_spend), lambda x: x[0])
            }

        monthly_spend = [
            (month, spend)
            for project in project_totals.values()
            for month, spend in project.items()
        ]
        workspace_totals = {}
        for month, spends in groupby(sorted(monthly_spend), lambda m: m[0]):
            workspace_totals[month] = sum([spend[1] for spend in spends])

        return {
            "environments": data,
            "projects": project_totals,
            "workspace": workspace_totals,
        }

    @classmethod
    def cumulative_budget(cls, alternate):
        return {
            "months": CUMULATIVE_BUDGET_BELUGA
            if alternate
            else CUMULATIVE_BUDGET_AARDVARK
        }
