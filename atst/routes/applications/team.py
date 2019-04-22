from flask import render_template


from . import applications_bp
from atst.domain.environments import Environments
from atst.domain.applications import Applications
from atst.domain.authz.decorator import user_can_access_decorator as user_can
from atst.models.permissions import Permissions
from atst.domain.permission_sets import PermissionSets
from atst.utils.localization import translate


def permission_str(member, edit_perm_set):
    if member.has_permission_set(edit_perm_set):
        return translate("portfolios.members.permissions.edit_access")
    else:
        return translate("portfolios.members.permissions.view_only")


@applications_bp.route("/applications/<application_id>/team")
@user_can(Permissions.VIEW_APPLICATION, message="view portfolio applications")
def team(application_id):
    application = Applications.get(resource_id=application_id)

    environment_users = {}
    for member in application.members:
        user_id = member.user.id
        environment_users[user_id] = {
            "permissions": {
                "delete_access": permission_str(
                    member, PermissionSets.DELETE_APPLICATION_ENVIRONMENTS
                ),
                "environment_management": permission_str(
                    member, PermissionSets.EDIT_APPLICATION_ENVIRONMENTS
                ),
                "team_management": permission_str(
                    member, PermissionSets.EDIT_APPLICATION_TEAM
                ),
            },
            "environments": Environments.for_user(
                user=member.user, application=application
            ),
        }

    return render_template(
        "portfolios/applications/team.html",
        application=application,
        environment_users=environment_users,
    )
