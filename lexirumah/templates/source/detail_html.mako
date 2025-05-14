<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "sources" %>

<h2>${ctx.name}</h2>
${ctx.coins(request)|n}

<div class="tabbable">
    <ul class="nav nav-tabs">
        <li class="active"><a href="#tab1" data-toggle="tab">Text</a></li>
        <li><a href="#tab2" data-toggle="tab">BibTeX</a></li>
        <!--
            Conversion to RIS needs the external xml2ris tool, conversion to MODS is not supported at all
        <li><a href="#tab3" data-toggle="tab">RIS</a></li>
        <li><a href="#tab4" data-toggle="tab">MODS</a></li>
        -->
    </ul>
    <div class="tab-content">
        <% bibrec = ctx.bibtex() %>
        <div id="tab1" class="tab-pane active">
            <p id="${h.format_gbs_identifier(ctx)}">${bibrec.text()|n}</p>
            % if ctx.datadict().get('Additional_information'):
            <p>
                ${ctx.datadict().get('Additional_information')}
            </p>
            % endif
            <!-- We store fieldnotes as `misc` with non-standard fields. -->
            % if str(bibrec.genre) == 'misc' and (bibrec.get('collector') or bibrec.get('date') or (bibrec.get('latitude') and bibrec.get('longitude')) or bibrec.get('speaker') or bibrec.get('location')):
            <p style="font-size:90%">
              Field Notes collected
              % if bibrec.get('collector') or bibrec.get('assistant') or bibrec.get('date') or bibrec.get('location') or bibrec.get('latitude') and bibrec.get('longitude'):
              % if bibrec.get('collector'):
              by ${bibrec['collector']}
              % endif
              % if bibrec.get('assistant'):
              with ${bibrec['assistant'].split('–')[0]}
              % endif
              % if bibrec.get('date'):
              on ${bibrec['date']}
              % endif
              % if bibrec.get('location') or (bibrec.get('latitude') and bibrec.get('longitude')):
              for the language spoken at
              % if bibrec.get('location'):
              ${bibrec['location']}
              % endif
              % if bibrec.get('latitude') and bibrec.get('longitude'):
              (${bibrec['latitude']}, ${bibrec['longitude']})
              % endif
              % endif
              .
              % endif
              % if bibrec.get('date_of_transcription') or bibrec.get('transcribed_by'):
              Transcribed
              % if bibrec.get('date_of_transcription'):
              ${bibrec['date_of_transcription']}
              % endif
              % if bibrec.get('transcribed_by'):
              by ${bibrec['transcribed_by']}
              % endif
              .
              % endif
              % if bibrec.get('speaker'):
              % if len(bibrec['speaker'].split('&')) == 1:
              Speaker: ${bibrec['speaker'].split('–')[0]}
              % else:
              Speakers:
              % for speaker in bibrec['speaker'].split('&')[:-1]:
              ${speaker.split('–')[0]} and
              % endfor
              ${bibrec['speaker'].split('&')[-1]}
              % endif
              % endif
            </p>
            % endif
            % if bibrec.get('url'):
                <p>${h.external_link(bibrec['url'])}</p>
            % endif
            ${util.gbs_links(filter(None, [ctx.gbs_identifier]))}
            % if ctx.jsondata.get('internetarchive_id'):
                <hr />
                <iframe src='https://archive.org/stream/${ctx.jsondata.get('internetarchive_id')}?ui=embed#mode/1up' width='680px' height='750px' frameborder='1' ></iframe>
            % endif
        </div>
        <div id="tab2" class="tab-pane"><pre>${bibrec}</pre></div>
        <div id="tab3" class="tab-pane"><pre>${bibrec.format('ris')}</pre></div>
        <div id="tab4" class="tab-pane"><pre>${bibrec.format('mods')}</pre></div>
    </div>
</div>

<%def name="sidebar()">
    <% referents, one_open = context.get('referents', {}), False %>
    <div class="accordion" id="sidebar-accordion">
    % if referents.get('language'):
        <%util:accordion_group eid="acc-l" parent="sidebar-accordion" title="${_('Languages')}" open="${not one_open}">
            ${util.stacked_links(referents['language'])}
        </%util:accordion_group>
        <% one_open = True %>
    % endif
    % if referents.get('contribution'):
        <%util:accordion_group eid="acc-c" parent="sidebar-accordion" title="${_('Contributions')}" open="${not one_open}">
            ${util.stacked_links(referents['contribution'])}
        </%util:accordion_group>
        <% one_open = True %>
    % endif
    % if referents.get('valueset'):
        <%util:accordion_group eid="acc-v" parent="sidebar-accordion" title="${_('ValueSets')}" open="${not one_open}">
            ${util.stacked_links(referents['valueset'])}
        </%util:accordion_group>
        <% one_open = True %>
    % endif
    % if referents.get('sentence'):
        <%util:accordion_group eid="acc-s" parent="sidebar-accordion" title="${_('Sentences')}" open="${not one_open}">
            ${util.stacked_links(referents['sentence'])}
        </%util:accordion_group>
        <% one_open = True %>
    % endif
    </div>
</%def>

${request.get_datatable('values', h.models.Value, source=ctx).render()}
