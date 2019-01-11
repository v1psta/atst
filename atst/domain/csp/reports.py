from itertools import groupby
from collections import OrderedDict
import pendulum


class ReportingInterface:
    def monthly_totals_for_environment(environment):
        """Return the monthly totals for the specified environment.

        Data should be in the format of a dictionary with the month as the key
        and the spend in that month as the value. For example:

            { "01/2018": 79.85, "02/2018": 86.54 }

        """
        raise NotImplementedError()


class MockEnvironment:
    def __init__(self, id_, env_name):
        self.id = id_
        self.name = env_name


class MockApplication:
    def __init__(self, application_name, envs):
        def make_env(name):
            return MockEnvironment("{}_{}".format(application_name, name), name)

        self.name = application_name
        self.environments = [make_env(env_name) for env_name in envs]


class MockReportingProvider(ReportingInterface):
    MONTHLY_SPEND_BY_ENVIRONMENT = {
        "LC04_Integ": {
            "02/2018": 284,
            "03/2018": 1210,
            "04/2018": 1430,
            "05/2018": 1366,
            "06/2018": 1169,
            "07/2018": 991,
            "08/2018": 978,
            "09/2018": 737,
        },
        "LC04_PreProd": {
            "02/2018": 812,
            "03/2018": 1389,
            "04/2018": 1425,
            "05/2018": 1306,
            "06/2018": 1112,
            "07/2018": 936,
            "08/2018": 921,
            "09/2018": 694,
        },
        "LC04_Prod": {
            "02/2018": 1742,
            "03/2018": 1716,
            "04/2018": 1866,
            "05/2018": 1809,
            "06/2018": 1839,
            "07/2018": 1633,
            "08/2018": 1654,
            "09/2018": 1103,
        },
        "SF18_Integ": {
            "04/2018": 1498,
            "05/2018": 1400,
            "06/2018": 1394,
            "07/2018": 1171,
            "08/2018": 1200,
            "09/2018": 963,
        },
        "SF18_PreProd": {
            "04/2018": 1780,
            "05/2018": 1667,
            "06/2018": 1703,
            "07/2018": 1474,
            "08/2018": 1441,
            "09/2018": 933,
        },
        "SF18_Prod": {
            "04/2018": 1686,
            "05/2018": 1779,
            "06/2018": 1792,
            "07/2018": 1570,
            "08/2018": 1539,
            "09/2018": 986,
        },
        "Canton_Prod": {
            "05/2018": 28699,
            "06/2018": 26766,
            "07/2018": 22619,
            "08/2018": 24090,
            "09/2018": 16719,
        },
        "BD04_Integ": {},
        "BD04_PreProd": {
            "02/2018": 7019,
            "03/2018": 3004,
            "04/2018": 2691,
            "05/2018": 2901,
            "06/2018": 3463,
            "07/2018": 3314,
            "08/2018": 3432,
            "09/2018": 723,
        },
        "SCV18_Dev": {"05/2019": 9797},
        "Crown_CR Portal Dev": {
            "03/2018": 208,
            "04/2018": 457,
            "05/2018": 671,
            "06/2018": 136,
            "07/2018": 1524,
            "08/2018": 2077,
            "09/2018": 1858,
        },
        "Crown_CR Staging": {
            "03/2018": 208,
            "04/2018": 457,
            "05/2018": 671,
            "06/2018": 136,
            "07/2018": 1524,
            "08/2018": 2077,
            "09/2018": 1858,
        },
        "Crown_CR Portal Test 1": {"07/2018": 806, "08/2018": 1966, "09/2018": 2597},
        "Crown_Jewels Prod": {"07/2018": 806, "08/2018": 1966, "09/2018": 2597},
        "Crown_Jewels Dev": {
            "03/2018": 145,
            "04/2018": 719,
            "05/2018": 1243,
            "06/2018": 2214,
            "07/2018": 2959,
            "08/2018": 4151,
            "09/2018": 4260,
        },
        "NP02_Integ": {"08/2018": 284, "09/2018": 1210},
        "NP02_PreProd": {"08/2018": 812, "09/2018": 1389},
        "NP02_Prod": {"08/2018": 3742, "09/2018": 4716},
        "FM_Integ": {"08/2018": 1498},
        "FM_Prod": {"09/2018": 5686},
    }

    CUMULATIVE_BUDGET_AARDVARK = {
        "02/2018": {"spend": 9857, "cumulative": 9857},
        "03/2018": {"spend": 7881, "cumulative": 17738},
        "04/2018": {"spend": 14010, "cumulative": 31748},
        "05/2018": {"spend": 43510, "cumulative": 75259},
        "06/2018": {"spend": 41725, "cumulative": 116_984},
        "07/2018": {"spend": 41328, "cumulative": 158_312},
        "08/2018": {"spend": 47491, "cumulative": 205_803},
        "09/2018": {"spend": 36028, "cumulative": 241_831},
    }

    CUMULATIVE_BUDGET_BELUGA = {
        "08/2018": {"spend": 4838, "cumulative": 4838},
        "09/2018": {"spend": 14500, "cumulative": 19338},
    }

    REPORT_FIXTURE_MAP = {
        "Aardvark": {
            "cumulative": CUMULATIVE_BUDGET_AARDVARK,
            "applications": [
                MockApplication("LC04", ["Integ", "PreProd", "Prod"]),
                MockApplication("SF18", ["Integ", "PreProd", "Prod"]),
                MockApplication("Canton", ["Prod"]),
                MockApplication("BD04", ["Integ", "PreProd"]),
                MockApplication("SCV18", ["Dev"]),
                MockApplication(
                    "Crown",
                    [
                        "CR Portal Dev",
                        "CR Staging",
                        "CR Portal Test 1",
                        "Jewels Prod",
                        "Jewels Dev",
                    ],
                ),
            ],
            "budget": 500_000,
        },
        "Beluga": {
            "cumulative": CUMULATIVE_BUDGET_BELUGA,
            "applications": [
                MockApplication("NP02", ["Integ", "PreProd", "NP02_Prod"]),
                MockApplication("FM", ["Integ", "Prod"]),
            ],
            "budget": 70000,
        },
    }

    def _sum_monthly_spend(self, data):
        return sum(
            [
                spend
                for application in data
                for env in application.environments
                for spend in self.MONTHLY_SPEND_BY_ENVIRONMENT[env.id].values()
            ]
        )

    def get_budget(self, portfolio):
        if portfolio.name in self.REPORT_FIXTURE_MAP:
            return self.REPORT_FIXTURE_MAP[portfolio.name]["budget"]
        elif portfolio.request and portfolio.legacy_task_order:
            return portfolio.legacy_task_order.budget
        return 0

    def get_total_spending(self, portfolio):
        if portfolio.name in self.REPORT_FIXTURE_MAP:
            return self._sum_monthly_spend(
                self.REPORT_FIXTURE_MAP[portfolio.name]["applications"]
            )
        return 0

    def _rollup_application_totals(self, data):
        application_totals = {}
        for application, environments in data.items():
            application_spend = [
                (month, spend)
                for env in environments.values()
                if env
                for month, spend in env.items()
            ]
            application_totals[application] = {
                month: sum([spend[1] for spend in spends])
                for month, spends in groupby(sorted(application_spend), lambda x: x[0])
            }

        return application_totals

    def _rollup_portfolio_totals(self, application_totals):
        monthly_spend = [
            (month, spend)
            for application in application_totals.values()
            for month, spend in application.items()
        ]
        portfolio_totals = {}
        for month, spends in groupby(sorted(monthly_spend), lambda m: m[0]):
            portfolio_totals[month] = sum([spend[1] for spend in spends])

        return portfolio_totals

    def monthly_totals_for_environment(self, environment_id):
        """Return the monthly totals for the specified environment.

        Data should be in the format of a dictionary with the month as the key
        and the spend in that month as the value. For example:

            { "01/2018": 79.85, "02/2018": 86.54 }

        """
        return self.MONTHLY_SPEND_BY_ENVIRONMENT.get(environment_id, {})

    def monthly_totals(self, portfolio):
        """Return month totals rolled up by environment, application, and portfolio.

        Data should returned with three top level keys, "portfolio", "applications",
        and "environments".
        The "applications" key will have budget data per month for each application,
        The "environments" key will have budget data for each environment.
        The "portfolio" key will be total monthly spending for the portfolio.
        For example:

            {
                "environments": { "X-Wing": { "Prod": { "01/2018": 75.42 } } },
                "applications": { "X-Wing": { "01/2018": 75.42 } },
                "portfolio": { "01/2018": 75.42 },
            }

        """
        applications = portfolio.applications
        if portfolio.name in self.REPORT_FIXTURE_MAP:
            applications = self.REPORT_FIXTURE_MAP[portfolio.name]["applications"]
        environments = {
            application.name: {
                env.name: self.monthly_totals_for_environment(env.id)
                for env in application.environments
            }
            for application in applications
        }

        application_totals = self._rollup_application_totals(environments)
        portfolio_totals = self._rollup_portfolio_totals(application_totals)

        return {
            "environments": environments,
            "applications": application_totals,
            "portfolio": portfolio_totals,
        }

    def cumulative_budget(self, portfolio):
        if portfolio.name in self.REPORT_FIXTURE_MAP:
            budget_months = self.REPORT_FIXTURE_MAP[portfolio.name]["cumulative"]
        else:
            budget_months = {}

        this_year = pendulum.now().year
        all_months = OrderedDict()
        for m in range(1, 13):
            month_str = "{month:02d}/{year}".format(month=m, year=this_year)
            all_months[month_str] = budget_months.get(month_str, None)

        return {"months": all_months}
