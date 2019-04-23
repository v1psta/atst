from flask import render_template, request as http_request, g, url_for, redirect


from . import applications_bp
from atst.domain.environments import Environments
from atst.domain.applications import Applications
from atst.domain.authz.decorator import user_can_access_decorator as user_can
from atst.domain.permission_sets import PermissionSets
from atst.forms.application_member import NewForm as NewMemberForm
from atst.models.permissions import Permissions
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
