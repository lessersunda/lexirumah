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
        <ol>
        %for value in obj:
            <li> ${recursive_html(value) | n} </li>
        %endfor
        </ol>
    % else:
        ${obj}
    % endif
</%def>

<div class="well" style="float:right; max-width: 40%; clear:both;">
<h4>Metadata</h4>
 ${recursive_html({key: value for key, value in ctx.jsondata.items() if key not in ['language_pks']})}
</div>

<h2>${_('Contribution')} ${ctx.name}</h2>
<p>
 ${ctx.description | n}
</p>

<small>cite as</small>
<blockquote>
<ul>
% for source in ctx.all_sources:
    <li>${source}</li>
% endfor
</ul>
</blockquote>
% if ctx.url:
    <p>Available online at ${h.external_link(ctx.url)}</p>
% endif

<table class="table table-nonfluid" style="clear:none;">
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

<h3 style="clear:both;">Languages</h3>

${map.render()}

${request.get_datatable('languages', h.models.Language, contribution=ctx) .render()}