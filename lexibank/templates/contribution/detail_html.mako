<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "contributions" %>

<%def name="recursive_html(obj)">
    % if isinstance(obj, dict):
    <ul>
        % for key, value in obj.items():
        <li>${key}:
        ${recursive_html(value) | n}
        </li>
        % endfor
    </ul>
    % elif isinstance(obj, str):
    ${obj}
    % elif hasattr(obj, '__iter__'):
        <ul>
        %for value in obj:
            <li> ${recursive_html(value) | n} </li>
        %endfor
        </ul>
    % else:
        ${obj}
    % endif
</%def>

<h2>${_('Contribution')} ${ctx.name}</h2>

<p>
${ctx.description | n}
</p>

 ${recursive_html({key: value for key, value in ctx.jsondata.items() if key not in ['language_pks']})}

<small>cite as</small>
% for source in ctx.all_sources:
<blockquote>
    ${source}
</blockquote>
% endfor
% if ctx.url:
    <p>Available online at ${h.external_link(ctx.url)}</p>
% endif

<table class="table table-nonfluid">
    <tr>
        <td>Concepts</td>
        <td class="right">${ctx.parameter_count}</td>
    </tr>
    <tr>
        <td>Lexemes</td>
        <td class="right">${'{0:,}'.format(ctx.lexeme_count)}</td>
    </tr>
    <tr>
        <td>
            <span class="hint--bottom" data-hint="${ctx.__class__.__table__._columns['synonym_index'].doc}">Synonymy index</span>
        </td>
        <td class="right">${'{0:.2f}'.format(ctx.synonym_index)}</td>
    </tr>
</table>

<h3>Languages</h3>

${map.render()}

${request.get_datatable('languages', h.models.Language, contribution=ctx) .render()}
