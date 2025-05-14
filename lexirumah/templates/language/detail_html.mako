<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "languages" %>
<%block name="title">${_('Language')} ${ctx.name}</%block>

<h2>${_('Language')} ${ctx.name}</h2>
<p>
  ${ctx.description or "No description."}
</p>
<p>
  Language family: ${ctx.family}
</p>
% if ctx.comment:
<p class="alert">
  ${ctx.comment}
</p>
% endif


${request.get_datatable('values', h.models.Value, language=ctx).render()}

<%def name="sidebar()">
    <div style="clear: right;"> </div>
    <div class="well">
    ${util.codes()}

        % if ctx.latitude is not None:
            ${request.map.render()}
            ${h.format_coordinates(ctx)}
        % endif
    </div>
</%def>
