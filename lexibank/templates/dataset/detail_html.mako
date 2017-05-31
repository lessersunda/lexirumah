<%! from datetime import date %>
<%inherit file="../home_comp.mako"/>
<%namespace name="util" file="../util.mako"/>

<%def name="sidebar()">
    <img src="${request.static_url('lexibank:static/logo.png')}"/>

    <%util:well title="LexiRumah">
        <a href="${req.resource_url(req.dataset)}">${req.resource_url(req.dataset)}</a>
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
    transcribed wordlist data and was set up and is maintained by the
    NWO Vici
    project <a href="http://www.vici.marianklamer.org/">“Reconstructing
    the past through languages of the present: the Lesser Sunda
    Islands”</a> at Leiden University.
</p>

<h3>Data Provenance</h3>
The data represented in LexiRumah is taken from published sources attributed explicitly or from survey work
executed in the following projects:
<ul>
  <li>NWO-VICI project <a
    href="http://www.vici.marianklamer.org/">“Reconstructing the past
    through languages of the present: the Lesser Sunda Islands”</a>, Leiden University 2014–2019
  </li>
  <li>The European Science Foundation EuroBABEL Project “Alor-Pantar languages: Origins and theoretical impact”,
  Leiden University, University of Fairbanks, Alaska, US and University of Surrey, United Kingdom, 2009–2013</li>
  <li>NWO-VIDI project “Linguistic Variation in Eastern Indonesia”, Leiden University 2002–2007</li>
</ul>

<h3> How to cite LexiRumah</h3>
<p>
  LexiRumah is a separate publication by ${request.dataset.formatted_editors()}. We recommend you cite it as
  <blockquote><%block name="cite_us">${" & ".join([editor.contributor.last_first() for editor in request.dataset.editors if editor.primary])} (eds.)
    <i>LexiRumah</i>.  Leiden: Leiden University Centre for
    Linguistics, 2017. Available online
    at <a href="">${req.resource_url(req.dataset)}</a>. Accessed on
    ${date.today()}.  </%block>
  </blockquote>
</p>
<p>
  It is important to cite the specific reference (printed source, data
  collector) that you are taking information from. Every item in the
  database is linked to its reference, please cite them accordingly
  as, for example
  <blockquote><a href="${request.route_url('contribution', id=example_reference.id)}">${list(example_reference.all_sources)[0]}</a> In: ${cite_us()}</blockquote>
</p>
                            

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
