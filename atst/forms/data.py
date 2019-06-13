from atst.models import CSPRole
from atst.utils.localization import translate


SERVICE_BRANCHES = [
    ("", "- Select -"),
    ("Air Force, Department of the", "Air Force, Department of the"),
    ("Army and Air Force Exchange Service", "Army and Air Force Exchange Service"),
    ("Army, Department of the", "Army, Department of the"),
    (
        "Defense Advanced Research Applications Agency",
        "Defense Advanced Research Applications Agency",
    ),
    ("Defense Commissary Agency", "Defense Commissary Agency"),
    ("Defense Contract Audit Agency", "Defense Contract Audit Agency"),
    ("Defense Contract Management Agency", "Defense Contract Management Agency"),
    ("Defense Finance & Accounting Service", "Defense Finance & Accounting Service"),
    ("Defense Health Agency", "Defense Health Agency"),
    ("Defense Information System Agency", "Defense Information System Agency"),
    ("Defense Intelligence Agency", "Defense Intelligence Agency"),
    ("Defense Legal Services Agency", "Defense Legal Services Agency"),
    ("Defense Logistics Agency", "Defense Logistics Agency"),
    ("Defense Media Activity", "Defense Media Activity"),
    ("Defense Micro Electronics Activity", "Defense Micro Electronics Activity"),
    ("Defense POW-MIA Accounting Agency", "Defense POW-MIA Accounting Agency"),
    ("Defense Security Cooperation Agency", "Defense Security Cooperation Agency"),
    ("Defense Security Service", "Defense Security Service"),
    ("Defense Technical Information Center", "Defense Technical Information Center"),
    (
        "Defense Technology Security Administration",
        "Defense Technology Security Administration",
    ),
    ("Defense Threat Reduction Agency", "Defense Threat Reduction Agency"),
    ("DoD Education Activity", "DoD Education Activity"),
    ("DoD Human Recourses Activity", "DoD Human Recourses Activity"),
    ("DoD Inspector General", "DoD Inspector General"),
    ("DoD Test Resource Management Center", "DoD Test Resource Management Center"),
    (
        "Headquarters Defense Human Resource Activity ",
        "Headquarters Defense Human Resource Activity ",
    ),
    ("Joint Staff", "Joint Staff"),
    ("Missile Defense Agency", "Missile Defense Agency"),
    ("National Defense University", "National Defense University"),
    (
        "National Geospatial Intelligence Agency (NGA)",
        "National Geospatial Intelligence Agency (NGA)",
    ),
    (
        "National Oceanic and Atmospheric Administration (NOAA)",
        "National Oceanic and Atmospheric Administration (NOAA)",
    ),
    ("National Reconnaissance Office", "National Reconnaissance Office"),
    ("National Reconnaissance Office (NRO)", "National Reconnaissance Office (NRO)"),
    ("National Security Agency (NSA)", "National Security Agency (NSA)"),
    (
        "National Security Agency-Central Security Service",
        "National Security Agency-Central Security Service",
    ),
    ("Navy, Department of the", "Navy, Department of the"),
    ("Office of Economic Adjustment", "Office of Economic Adjustment"),
    ("Office of the Secretary of Defense", "Office of the Secretary of Defense"),
    ("Pentagon Force Protection Agency", "Pentagon Force Protection Agency"),
    (
        "Uniform Services University of the Health Sciences",
        "Uniform Services University of the Health Sciences",
    ),
    ("US Cyber Command (USCYBERCOM)", "US Cyber Command (USCYBERCOM)"),
    (
        "US Special Operations Command (USSOCOM)",
        "US Special Operations Command (USSOCOM)",
    ),
    ("US Strategic Command (USSTRATCOM)", "US Strategic Command (USSTRATCOM)"),
    (
        "US Transportation Command (USTRANSCOM)",
        "US Transportation Command (USTRANSCOM)",
    ),
    ("Washington Headquarters Services", "Washington Headquarters Services"),
]

APP_MIGRATION = [
    ("on_premise", translate("forms.task_order.app_migration.on_premise")),
    ("cloud", translate("forms.task_order.app_migration.cloud")),
    ("both", translate("forms.task_order.app_migration.both")),
    ("none", translate("forms.task_order.app_migration.none")),
    ("not_sure", translate("forms.task_order.app_migration.not_sure")),
]

APPLICATION_COMPLEXITY = [
    ("storage", translate("forms.task_order.complexity.storage")),
    ("data_analytics", translate("forms.task_order.complexity.data_analytics")),
    ("conus", translate("forms.task_order.complexity.conus")),
    ("oconus", translate("forms.task_order.complexity.oconus")),
    ("tactical_edge", translate("forms.task_order.complexity.tactical_edge")),
    ("not_sure", translate("forms.task_order.complexity.not_sure")),
    ("other", translate("forms.task_order.complexity.other")),
]

DEV_TEAM = [
    ("civilians", translate("forms.task_order.dev_team.civilians")),
    ("military", translate("forms.task_order.dev_team.military")),
    ("contractor", translate("forms.task_order.dev_team.contractor")),
    ("other", translate("forms.task_order.dev_team.other")),
]

TEAM_EXPERIENCE = [
    ("none", translate("forms.task_order.team_experience.none")),
    ("planned", translate("forms.task_order.team_experience.planned")),
    ("built_1", translate("forms.task_order.team_experience.built_1")),
    ("built_3", translate("forms.task_order.team_experience.built_3")),
    ("built_many", translate("forms.task_order.team_experience.built_many")),
]

ENV_ROLE_NO_ACCESS = "No Access"
ENV_ROLES = [(role.value, role.value) for role in CSPRole] + [
    (ENV_ROLE_NO_ACCESS, "No access")
]

JEDI_CLIN_TYPES = [
    ("JEDI_CLIN_1", translate("forms.task_order.clin_01_label")),
    ("JEDI_CLIN_2", translate("forms.task_order.clin_02_label")),
    ("JEDI_CLIN_3", translate("forms.task_order.clin_03_label")),
    ("JEDI_CLIN_4", translate("forms.task_order.clin_04_label")),
]
