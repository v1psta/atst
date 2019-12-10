from collections import defaultdict
import json
from decimal import Decimal


def load_fixture_data():
    with open("fixtures/fixture_spend_data.json") as json_file:
        return json.load(json_file)


class MockReportingProvider:
    FIXTURE_SPEND_DATA = load_fixture_data()

    @classmethod
    def get_portfolio_monthly_spending(cls, portfolio):
        """
        returns an array of application and environment spending for the 
        portfolio. Applications and their nested environments are sorted in
        alphabetical order by name.
        [
            {
                name
                this_month
                last_month
                total
                environments [
                    {
                        name
                        this_month
                        last_month
                        total
                    }
                ]
            }
        ]
        """
        if portfolio.name in cls.FIXTURE_SPEND_DATA:
            applications = cls.FIXTURE_SPEND_DATA[portfolio.name]["applications"]
            return sorted(
                [
                    cls._get_application_monthly_totals(application)
                    for application in applications
                ],
                key=lambda app: app["name"],
            )
        return []

    @classmethod
    def _get_environment_monthly_totals(cls, environment):
        """
        returns a dictionary that represents spending totals for an environment e.g. 
        {
            name
            this_month
            last_month
            total
        }
        """
        return {
            "name": environment["name"],
            "this_month": sum(environment["spending"]["this_month"].values()),
            "last_month": sum(environment["spending"]["last_month"].values()),
            "total": sum(environment["spending"]["total"].values()),
        }

    @classmethod
    def _get_application_monthly_totals(cls, application):
        """
        returns a dictionary that represents spending totals for an application 
        and its environments e.g. 
            {
                name
                this_month
                last_month
                total
                environments: [
                    {
                        name
                        this_month
                        last_month
                        total
                    }
                ]
            }
        """
        environments = sorted(
            [
                cls._get_environment_monthly_totals(env)
                for env in application["environments"]
            ],
            key=lambda env: env["name"],
        )
        return {
            "name": application["name"],
            "this_month": sum(env["this_month"] for env in environments),
            "last_month": sum(env["last_month"] for env in environments),
            "total": sum(env["total"] for env in environments),
            "environments": environments,
        }

    @classmethod
    def get_spending_by_JEDI_clin(cls, portfolio):
        """
        returns an dictionary of spending per JEDI CLIN for a portfolio
        {
            jedi_clin: {
                invoiced
                estimated
            },
        }
        """
        if portfolio.name in cls.FIXTURE_SPEND_DATA:
            CLIN_spend_dict = defaultdict(lambda: defaultdict(Decimal))
            for application in cls.FIXTURE_SPEND_DATA[portfolio.name]["applications"]:
                for environment in application["environments"]:
                    for clin, spend in environment["spending"]["this_month"].items():
                        CLIN_spend_dict[clin]["estimated"] += Decimal(spend)
                    for clin, spend in environment["spending"]["total"].items():
                        CLIN_spend_dict[clin]["invoiced"] += Decimal(spend)
            return CLIN_spend_dict
        return {}
