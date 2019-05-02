from flask import render_template, request as http_request, g, url_for, redirect


from . import applications_bp
from atst.domain.applications import Applications
from atst.domain.environments import Environments
from atst.domain.environment_roles import EnvironmentRoles
from atst.domain.authz.decorator import user_can_access_decorator as user_can
from atst.domain.permission_sets import PermissionSets
from atst.domain.exceptions import AlreadyExistsError
from atst.forms.application_member import NewForm as NewMemberForm
from atst.forms.team import TeamForm
from atst.models import Permissions
from atst.services.invitation import Invitation as InvitationService
from atst.utils.flash import formatted_flash as flash
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
    team_data = []
    for member in application.members:
        user_id = member.user.id
        # TODO: if no members, we get a server error
        user_name = member.user.full_name
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
        permission_sets = {
            "perms_env_mgmt": PermissionSets.EDIT_APPLICATION_ENVIRONMENTS
            if member.has_permission_set(PermissionSets.EDIT_APPLICATION_ENVIRONMENTS)
            else "",
            "perms_team_mgmt": PermissionSets.EDIT_APPLICATION_TEAM
            if member.has_permission_set(PermissionSets.EDIT_APPLICATION_TEAM)
            else "",
            "perms_del_env": PermissionSets.DELETE_APPLICATION_ENVIRONMENTS
            if member.has_permission_set(PermissionSets.DELETE_APPLICATION_ENVIRONMENTS)
            else "",
        }
        roles = EnvironmentRoles.get_for_application_and_user(
            member.user.id, application.id
        )
        environment_roles = [
            {
                "environment_id": str(role.environment.id),
                "environment_name": role.environment.name,
                "role": role.role,
            }
            for role in roles
        ]
        team_data.append(
            {
                "user_id": str(user_id),
                "user_name": user_name,
                "permission_sets": permission_sets,
                "environment_roles": environment_roles,
            }
        )

        team_form = TeamForm(data={"members": team_data})

    env_roles = [
        {"environment_id": e.id, "environment_name": e.name}
        for e in application.environments
    ]
    new_member_form = NewMemberForm(data={"environment_roles": env_roles})

    return render_template(
        "portfolios/applications/team.html",
        application=application,
        environment_users=environment_users,
        team_form=team_form,
        new_member_form=new_member_form,
    )


@applications_bp.route("/application/<application_id>/members/new", methods=["POST"])
@user_can(
    Permissions.CREATE_APPLICATION_MEMBER, message="create new application member"
)
def create_member(application_id):
    application = Applications.get(application_id)
    form = NewMemberForm(http_request.form)

    if form.validate():
        try:
            member = Applications.create_member(
                application,
                form.user_data.data,
                permission_sets=form.permission_sets.data,
                environment_roles_data=form.environment_roles.data,
            )

            invite_service = InvitationService(
                g.current_user, member, form.user_data.data.get("email")
            )
            invite_service.invite()

            flash("new_portfolio_member", new_member=member)

        except AlreadyExistsError:
            return render_template(
                "error.html", message="There was an error processing your request."
            )
    else:
        pass
        # TODO: flash error message

    return redirect(
        url_for(
            "applications.team",
            application_id=application_id,
            fragment="application-members",
            _anchor="application-members",
        )
    )
