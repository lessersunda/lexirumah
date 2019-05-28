<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "contributions" %>
<%block name="title">
  ${ctx.valueset.language}:
  [ ${ctx.segments} ]
  ‘${ctx.valueset.parameter}’
</%block>

<%block name="head">
    <script src="${request.static_url('lexirumah:static/alignment.js')}"></script>
    <link rel="stylesheet" href="${request.static_url('lexirumah:static/alignment.css')}" type="text/css"/>
    <script>
        $( document ).ready(function() {
            var alignments = document.getElementsByClassName("alignment");
            for (var i=0,alignment; alignment=alignments[i]; i++) {
                alignment.innerHTML = plotWord(alignment.innerHTML, 'span');
            }
        });
    </script>
</%block>


<%def name="sidebar()">
% if ctx.references:
    <div class="well">
      <h3>References</h3>
      <p>
      % if ctx.references:
            Given in ${h.link(request, ctx.references[0].source)}
            as <q>${ctx.references[0].form_given_as}</q>.
      % endif
      % if len(ctx.references) > 1:
        Also given in
        ${h.link(request, ctx.references[1].source)}<!--
        % for ref in ctx.references[2:]:
-->; ${h.link(request, ref.source)}
        % endfor
      % endif
      </p>
      <p>
        From the dataset ${h.link(request, ctx.valueset.contribution)}
      </p>
    </div>
% endif
</%def>

<h2>
  ${h.link(request, ctx.valueset.language)}
</h2>

<p style="font-size:150%">
   <b>${ctx.orthographic_form}</b>
   [${ctx.name}]
   ‘${h.link(request, ctx.valueset.parameter)}’
</p>

% if ctx.external_url:
    <p>${h.external_link(ctx.external_url)}</p>
% endif

<table class="table table-nonfluid">
    % if ctx.context:
        <tr>
            <th>Context:</th>
            <td>${ctx.context}</td>
        </tr>
    % endif
    % if ctx.description:
        <tr>
            <th>Description:</th>
            <td>${ctx.description}</td>
        </tr>
    % endif
    % if ctx.comment:
        <tr>
            <th>Notes about ${ctx.orthographic_form}:</th>
            <td>${ctx.comment}</td>
        </tr>
    % endif
    % if ctx.cognatesets:
        <tr>
            <th>Cognatesets:</th>
            <td>
                <ul class="unstyled">
                    % for cs in ctx.cognatesets:
                    <li>
                        ${h.link(request, cs.cognateset)}
                    </li>
                    % endfor
                </ul>
            </td>
        </tr>
    % endif
    % if colexifications:
    <tr>
      <th>it also means:</th>
      <td>
          % for cp in colexifications:
            ${h.link(request, cp, label=cp.valueset.parameter)} <br />
          % endfor
      </td>
    </tr>
    % endif
    % if synonyms:
    <tr>
      <th>Synonym${"s" if len(synonyms)>1 else ""}:</th>
    <td>
        % for cp in synonyms:
          ${h.link(request, cp)} <br />
        % endfor
    </td>
    </tr>
    % endif
</table>
