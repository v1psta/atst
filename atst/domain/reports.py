from datetime import datetime
from itertools import groupby


MONTHLY_SPEND_AARDVARK = {
    "LC04": {
        "Integ": {
            "02/2018": 284,
            "03/2018": 1210,
            "04/2018": 1430,
            "05/2018": 1366,
            "06/2018": 1169,
            "07/2018": 991,
            "08/2018": 978,
            "09/2018": 737,
        },
        "PreProd": {
            "02/2018": 812,
            "03/2018": 1389,
            "04/2018": 1425,
            "05/2018": 1306,
            "06/2018": 1112,
            "07/2018": 936,
            "08/2018": 921,
            "09/2018": 694,
        },
        "Prod": {
            "02/2018": 1742,
            "03/2018": 1716,
            "04/2018": 1866,
            "05/2018": 1809,
            "06/2018": 1839,
            "07/2018": 1633,
            "08/2018": 1654,
            "09/2018": 1103,
        },
    },
    "SF18": {
        "Integ": {
            "04/2018": 1498,
            "05/2018": 1400,
            "06/2018": 1394,
            "07/2018": 1171,
            "08/2018": 1200,
            "09/2018": 963,
        },
        "PreProd": {
            "04/2018": 1780,
            "05/2018": 1667,
            "06/2018": 1703,
            "07/2018": 1474,
            "08/2018": 1441,
            "09/2018": 933,
        },
        "Prod": {
            "04/2018": 1686,
            "05/2018": 1779,
            "06/2018": 1792,
            "07/2018": 1570,
            "08/2018": 1539,
            "09/2018": 986,
        },
    },
    "Canton": {
        "Prod": {
            "05/2018": 28699,
            "06/2018": 26766,
            "07/2018": 22619,
            "08/2018": 24090,
            "09/2018": 16719,
        }
    },
    "BD04": {
        "Integ": {},
        "PreProd": {
            "02/2018": 7019,
            "03/2018": 3004,
            "04/2018": 2691,
            "05/2018": 2901,
            "06/2018": 3463,
            "07/2018": 3314,
            "08/2018": 3432,
            "09/2018": 723,
        },
    },
    "SCV18": {"Dev": {"05/2019": 9797}},
    "Crown": {
        "CR Portal Dev": {
            "03/2018": 208,
            "04/2018": 457,
            "05/2018": 671,
            "06/2018": 136,
            "07/2018": 1524,
            "08/2018": 2077,
            "09/2018": 1858,
        },
        "CR Staging": {
            "03/2018": 208,
            "04/2018": 457,
            "05/2018": 671,
            "06/2018": 136,
            "07/2018": 1524,
            "08/2018": 2077,
            "09/2018": 1858,
        },
        "CR Portal Test 1": {"07/2018": 806, "08/2018": 1966, "09/2018": 2597},
        "Jewels Prod": {"07/2018": 806, "08/2018": 1966, "09/2018": 2597},
        "Jewels Dev": {
            "03/2018": 145,
            "04/2018": 719,
            "05/2018": 1243,
            "06/2018": 2214,
            "07/2018": 2959,
            "08/2018": 4151,
            "09/2018": 4260,
        },
    },
}

CUMULATIVE_BUDGET_AARDVARK = {
    "02/2018": {"spend": 9857, "cumulative": 9857},
    "03/2018": {"spend": 7881, "cumulative": 17738},
    "04/2018": {"spend": 14010, "cumulative": 31748},
    "05/2018": {"spend": 43510, "cumulative": 75259},
    "06/2018": {"spend": 41725, "cumulative": 116984},
    "07/2018": {"spend": 41328, "cumulative": 158312},
    "08/2018": {"spend": 47491, "cumulative": 205803},
    "09/2018": {"spend": 36028, "cumulative": 241831},
}

MONTHLY_SPEND_BELUGA = {
    "NP02": {
        "Integ": {"08/2018": 284, "09/2018": 1210},
        "PreProd": {"08/2018": 812, "09/2018": 1389},
        "Prod": {"08/2018": 3742, "09/2018": 4716},
    },
    "FM": {"Integ": {"08/2018": 1498}, "Prod": {"09/2018": 5686}},
}

CUMULATIVE_BUDGET_BELUGA = {
    "08/2018": {"spend": 4838, "cumulative": 4838},
    "09/2018": {"spend": 14500, "cumulative": 19338},
}

REPORT_FIXTURE_MAP = {
    "Aardvark": {
        "cumulative": CUMULATIVE_BUDGET_AARDVARK,
        "monthly": MONTHLY_SPEND_AARDVARK,
        "budget": 500_000,
    },
    "Beluga": {
        "cumulative": CUMULATIVE_BUDGET_BELUGA,
        "monthly": MONTHLY_SPEND_BELUGA,
        "budget": 70_000,
    },
}


def _sum_monthly_spend(data):
    return sum(
        [
            spend
            for project in data.values()
            for env in project.values()
            for spend in env.values()
        ]
    )


def _derive_project_totals(data):
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

    return project_totals


def _derive_workspace_totals(project_totals):
    monthly_spend = [
        (month, spend)
        for project in project_totals.values()
        for month, spend in project.items()
    ]
    workspace_totals = {}
    for month, spends in groupby(sorted(monthly_spend), lambda m: m[0]):
        workspace_totals[month] = sum([spend[1] for spend in spends])

    return workspace_totals


class Reports:
    @classmethod
    def workspace_totals(cls, workspace):
        if workspace.name in REPORT_FIXTURE_MAP:
            budget = REPORT_FIXTURE_MAP[workspace.name]["budget"]
            spent = _sum_monthly_spend(REPORT_FIXTURE_MAP[workspace.name]["monthly"])
        elif workspace.request and workspace.request.task_order:
            ws_to = workspace.request.task_order
            budget = ws_to.budget
            # spent will be derived from CSP data
            spent = 0
        else:
            budget = 0
            spent = 0

        return {"budget": budget, "spent": spent}

    @classmethod
    def monthly_totals(cls, workspace):
        if workspace.name in REPORT_FIXTURE_MAP:
            environments = REPORT_FIXTURE_MAP[workspace.name]["monthly"]
        else:
            environments = {
                project.name: {env.name: {} for env in project.environments}
                for project in workspace.projects
            }

        project_totals = _derive_project_totals(environments)
        workspace_totals = _derive_workspace_totals(project_totals)

        return {
            "environments": environments,
            "projects": project_totals,
            "workspace": workspace_totals,
        }

    @classmethod
    def cumulative_budget(cls, workspace):
        if workspace.name in REPORT_FIXTURE_MAP:
            months = REPORT_FIXTURE_MAP[workspace.name]["cumulative"]
        else:
            this_month = datetime.today().strftime("%m/%Y")
            months = {this_month: {"spend": 0, "cumulative": 0}}

        return {"months": months}
