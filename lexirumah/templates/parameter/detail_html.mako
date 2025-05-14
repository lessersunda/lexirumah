<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "parameters" %>
<%block name="title">${_('Parameter')} ‘${ctx.name}’/‘${ctx.indonesian}’</%block>

<h2>${_('Parameter')} ‘${ctx.name}’/‘${ctx.indonesian}’ ${u.concepticon_link(request, ctx)}</h2>

<table class="table table-nonfluid">
  <tr>
    <th>Semantic Field:</th>
    <td>${ctx.semanticfield}</td>
  </tr>
  <tr>
    <th>List:</th>
    <td>${ctx.origin}</td>
  </tr>
</table>
    % if ctx.elicitationnotes or ctx.description:
    <div class="alert">
      % if ctx.description:
      <p>
        ${ctx.description}
      </p>
      % endif
      % if ctx.elicitationnotes:
      <h4>Notes for Elicitation</h4>
      <p>
        ${ctx.elicitationnotes}
      </p>
      % endif
    </div>
    % endif
    % if ctx.comment:
    ${ctx.comment}
    % endif

% if map_ or request.map:
${(map_ or request.map).render()}
% endif

${request.get_datatable('values', h.models.Value, parameter=ctx).render()}
