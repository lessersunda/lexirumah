<%inherit file="../home_comp.mako"/>
<%namespace name="util" file="../util.mako"/>

<%def name="sidebar()">
    <img src="${request.static_url('lexibank:static/glottobank_all.jpg')}"/>

    <%util:well title="LexiRumah">
        <a href="${req.resource_url(req.dataset)}" style="font-family: monospace">lessersunda.ullet.nl/lexirumah</a>
        serves the latest
        ${h.external_link('https://github.com/Anaphory/lexirumah-data/releases', label='released version')}
        of data curated at
        ${h.external_link('https://github.com/Anaphory/lexirumah-data', label='github:Anaphory/lexirumah-data')}.
    </%util:well>
</%def>

<h2>Welcome to LexiRumah</h2>

<p class="lead"> LexiRumah (from <i>Lexicon</i> and Ind. <i>Rumah</i>
    = house) is an online database containing lexical data about
    languages of the Lesser Sunda islands. The database contains
    mostly IPA-transcribed wordlist data taken from referenced sources
    or collected by the NWO Vici projet <a
    href="http://www.vici.marianklamer.org/">“Reconstructing the past
    through languages of the present: the Lesser Sunda Islands”</a> at
    Leiden University.</p>

    <table class="table table-nonfluid">
        <tbody>
            <tr>
                <th><a href="${request.route_url('contributions')}">Datasets</a></th>
                <td class="right">${'{:,}'.format(stats['contribution'])}</td>
                <td></td>
            </tr>
            <tr>
                <th>Lexical items</th>
                <td class="right">${'{:,}'.format(stats['value'])}</td>
                <td></td>
            </tr>
            <tr>
                <th><a href="${request.route_url('parameters')}">Concepts</a></th>
                <td class="right">${'{:,}'.format(stats['parameter'])}</td>
                <td></td>
            </tr>
            <tr>
                <th><a href="${request.route_url('cognatesets')}">Cognate sets</a></th>
                <td class="right">${'{:,}'.format(stats['cognateset'])}</td>
                <td></td>
            </tr>
            <tr>
                <th><a href="${request.route_url('languages')}">Languages</a></th>
                <td class="right">${'{:,}'.format(stats['language'])}</td>
                <td>from ${stats['family']} families</td>
            </tr>
            % for fid, fname, count in families:
                <tr>
                    <td></td>
                    <td class="right">${count}</td>
                    <th><a href="${request.route_url('family', id=fid)}">${fname}</a></th>
                </tr>
            % endfor
        </tbody>
    </table>
