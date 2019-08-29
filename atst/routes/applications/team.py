from flask import render_template, request as http_request, g, url_for, redirect


from . import applications_bp
from atst.domain.applications import Applications
from atst.domain.application_roles import ApplicationRoles
from atst.domain.authz.decorator import user_can_access_decorator as user_can
from atst.domain.environment_roles import EnvironmentRoles
from atst.domain.environments import Environments
from atst.domain.exceptions import AlreadyExistsError
from atst.domain.permission_sets import PermissionSets
from atst.forms.application_member import NewForm as NewMemberForm
from atst.forms.team import TeamForm
from atst.models import Permissions
from atst.utils.flash import formatted_flash as flash
from atst.utils.localization import translate
from atst.jobs import send_mail


def get_form_permission_value(member, edit_perm_set):
    if member.has_permission_set(edit_perm_set):
        return edit_perm_set
    else:
        return PermissionSets.VIEW_APPLICATION


def get_team_form(application):
    team_data = []
    for member in application.members:
        permission_sets = {
            "perms_team_mgmt": get_form_permission_value(
                member, PermissionSets.EDIT_APPLICATION_TEAM
            ),
            "perms_env_mgmt": get_form_permission_value(
                member, PermissionSets.EDIT_APPLICATION_ENVIRONMENTS
            ),
            "perms_del_env": get_form_permission_value(
                member, PermissionSets.DELETE_APPLICATION_ENVIRONMENTS
            ),
        }
        roles = EnvironmentRoles.get_for_application_member(member.id)
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
                "role_id": member.id,
                "user_name": member.user_name,
                "permission_sets": permission_sets,
                "environment_roles": environment_roles,
            }
        )

    return TeamForm(data={"members": team_data})


def get_new_member_form(application):
    env_roles = [
        {"environment_id": e.id, "environment_name": e.name}
        for e in application.environments
    ]

    return NewMemberForm(data={"environment_roles": env_roles})


def render_team_page(application):
    team_form = get_team_form(application)
    new_member_form = get_new_member_form(application)

    return render_template(
        "portfolios/applications/team.html",
        application=application,
        team_form=team_form,
        new_member_form=new_member_form,
    )


@applications_bp.route("/applications/<application_id>/team")
@user_can(Permissions.VIEW_APPLICATION, message="view portfolio applications")
def team(application_id):
    application = Applications.get(resource_id=application_id)
    return render_team_page(application)


@applications_bp.route("/application/<application_id>/team", methods=["POST"])
@user_can(Permissions.EDIT_APPLICATION_MEMBER, message="update application member")
def update_team(application_id):
    application = Applications.get(application_id)
    form = TeamForm(http_request.form)

    if form.validate():
        for member_form in form.members:
            app_role = ApplicationRoles.get_by_id(member_form.role_id.data)
            new_perms = [
                perm
                for perm in member_form.data["permission_sets"]
                if perm != PermissionSets.VIEW_APPLICATION
            ]
            ApplicationRoles.update_permission_sets(app_role, new_perms)

            for environment_role_form in member_form.environment_roles:
                environment = Environments.get(
                    environment_role_form.environment_id.data
                )
                Environments.update_env_role(
                    environment, app_role, environment_role_form.data.get("role")
                )

        flash("updated_application_team_settings", application_name=application.name)

        return redirect(
            url_for(
                "applications.team",
                application_id=application_id,
                fragment="application-members",
                _anchor="application-members",
            )
        )
    else:
        return (render_team_page(application), 400)


def send_application_invitation(invitee_email, inviter_name, token):
    body = render_template(
        "emails/application/invitation.txt", owner=inviter_name, token=token
    )
    send_mail.delay(
        [invitee_email],
        translate("email.application_invite", {"inviter_name": inviter_name}),
        body,
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
            invite = Applications.invite(
                application=application,
                inviter=g.current_user,
                user_data=form.user_data.data,
                permission_sets_names=form.permission_sets.data,
                environment_roles_data=form.environment_roles.data,
            )

            send_application_invitation(
                invitee_email=invite.email,
                inviter_name=g.current_user.full_name,
                token=invite.token,
            )

            flash("new_application_member", user_name=invite.user_name)

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


@applications_bp.route(
    "/applications/<application_id>/members/<application_role_id>/delete",
    methods=["POST"],
)
@user_can(Permissions.DELETE_APPLICATION_MEMBER, message="remove application member")
def remove_member(application_id, application_role_id):
    application_role = ApplicationRoles.get_by_id(application_role_id)
    Applications.remove_member(application_role)

    flash(
        "application_member_removed",
        user_name=application_role.user_name,
        application_name=g.application.name,
    )

    return redirect(
        url_for(
            "applications.team",
            _anchor="application-members",
            application_id=g.application.id,
            fragment="application-members",
        )
    )
