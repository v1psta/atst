from atst.domain.roles import WORKSPACE_ROLES as WORKSPACE_ROLE_DEFINITIONS

SERVICE_BRANCHES = [
    ("", "Select an option"),
    ("Air Force, Department of the", "Air Force, Department of the"),
    ("Army and Air Force Exchange Service", "Army and Air Force Exchange Service"),
    ("Army, Department of the", "Army, Department of the"),
    (
        "Defense Advanced Research Projects Agency",
        "Defense Advanced Research Projects Agency",
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

ASSISTANCE_ORG_TYPES = [
    ("In-house staff", "In-house staff"),
    ("Contractor", "Contractor"),
    ("Other DoD Organization", "Other DoD Organization"),
    ("None", "None"),
]

DATA_TRANSFER_AMOUNTS = [
    ("", "Select an option"),
    ("Less than 100GB", "Less than 100GB"),
    ("100GB-500GB", "100GB-500GB"),
    ("500GB-1TB", "500GB-1TB"),
    ("1TB-50TB", "1TB-50TB"),
    ("50TB-100TB", "50TB-100TB"),
    ("100TB-500TB", "100TB-500TB"),
    ("500TB-1PB", "500TB-1PB"),
    ("1PB-5PB", "1PB-5PB"),
    ("5PB-10PB", "5PB-10PB"),
    ("Above 10PB", "Above 10PB"),
]

COMPLETION_DATE_RANGES = [
    ("", "Select an option"),
    ("Less than 1 month", "Less than 1 month"),
    ("1-3 months", "1-3 months"),
    ("3-6 months", "3-6 months"),
    ("Above 12 months", "Above 12 months"),
]

WORKSPACE_ROLES = [
    (role["name"], {"name": role["display_name"], "description": role["description"]})
    for role in WORKSPACE_ROLE_DEFINITIONS
    if role["name"] is not "officer"
]

ENVIRONMENT_ROLES = [
    (
        "developer",
        {
            "name": "Developer",
            "description": "Configures cloud-based IaaS and PaaS computing, networking, and storage services.",
        },
    ),
    (
        "database_administrator",
        {
            "name": "Database Administrator",
            "description": "Configures cloud-based database services.",
        },
    ),
    (
        "devops",
        {
            "name": "DevOps",
            "description": "Provisions, deprovisions, and deploys cloud-based IaaS and PaaS computing, networking, and storage services, including pre-configured machine images.",
        },
    ),
    (
        "billing_administrator",
        {
            "name": "Billing Administrator",
            "description": "Views cloud resource usage, budget reports, and invoices; Tracks budgets, including spend reports, cost planning and projections, and sets limits based on cloud service usage.",
        },
    ),
    (
        "security_administrator",
        {
            "name": "Security Administrator",
            "description": "Accesses information security and control tools of cloud resources which include viewing cloud resource usage logging, user roles and permissioning history.",
        },
    ),
    (
        "financial_auditor",
        {
            "name": "Financial Auditor",
            "description": "Views cloud resource usage and budget reports.",
        },
    ),
    (
        "",
        {"name": "No Access", "description": "User has no access to this environment."},
    ),
]

ENV_ROLE_MODAL_DESCRIPTION = {
    "header": "Assign Environment Role",
    "body": "An environment role determines the permissions a member of the workspace assumes when using the JEDI Cloud.<br/><br/>A member may have different environment roles across different projects. A member can only have one assigned environment role in a given environment.",
}

FUNDING_TYPES = [
    ("", "- Select -"),
    ("RDTE", "Research, Development, Testing & Evaluation (RDT&E)"),
    ("OM", "Operations & Maintenance (O&M)"),
    ("PROC", "Procurement (PROC)"),
    ("OTHER", "Other"),
]

TASK_ORDER_SOURCES = [("MANUAL", "Manual"), ("EDA", "EDA")]

APP_MIGRATION = [
    ("on_premise", "Yes, migrating from an <strong>on-premise data center</strong>"),
    ("cloud", "Yes, migrating from <strong>another cloud provider</strong>"),
    (
        "both",
        "Yes, migrating from an <strong>on-premise data center</strong> and <strong>another cloud provider</strong>",
    ),
    ("none", "Not planning to migrate any applications"),
    ("not_sure", "Not Sure"),
]

PROJECT_COMPLEXITY = [
    ("storage", "Storage "),
    ("data_analytics", "Data Analytics "),
    ("conus", "CONUS Only Access "),
    ("oconus", "OCONUS Access "),
    ("tactical_edge", "Tactical Edge Access "),
    ("not_sure", "Not Sure "),
    ("other", "Other"),
]

DEV_TEAM = [
    ("government_civilians", "Government Civilians"),
    ("military", "Military "),
    ("contractor", "Contractor "),
    ("other", "Other (E.g. University or other partner)"),
]

TEAM_EXPERIENCE = [
    ("none", "No previous experience"),
    ("planned", "Researched or planned a cloud build or migration"),
    ("built_1", "Built or Migrated 1-2 applications"),
    ("built_3", "Built or Migrated 3-5 applications"),
    (
        "built_many",
        "Built or migrated many applications, or consulted on several such projects",
    ),
]

PERIOD_OF_PERFORMANCE_LENGTH = [
    ("1", "1 Month"),
    ("2", "2 Months"),
    ("3", "3 Months"),
    ("4", "4 Months"),
    ("5", "5 Months"),
    ("6", "6 Months"),
    ("7", "7 Months"),
    ("8", "8 Months"),
    ("9", "9 Months"),
    ("10", "10 Months"),
    ("11", "11 Months"),
    ("12", "1 Year"),
    ("13", "1 Year, 1 Month"),
    ("14", "1 Year, 2 Months"),
    ("15", "1 Year, 3 Months"),
    ("16", "1 Year, 4 Months"),
    ("17", "1 Year, 5 Months"),
    ("18", "1 Year, 6 Months"),
    ("19", "1 Year, 7 Months"),
    ("20", "1 Year, 8 Months"),
    ("21", "1 Year, 9 Months"),
    ("22", "1 Year, 10 Months"),
    ("23", "1 Year, 11 Months"),
    ("24", "2 Years"),
]
