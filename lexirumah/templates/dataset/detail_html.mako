<%! from datetime import date %>
<%inherit file="../home_comp.mako"/>
<%namespace name="util" file="../util.mako"/>

<%def name="sidebar()">
    <img src="${request.static_url('lexirumah:static/logo.png')}"/>

    <%util:well title="LexiRumah">
        <a href="${req.resource_url(req.dataset)}">${req.resource_url(req.dataset)}</a>
        serves the latest
        ${h.external_link('https://github.com/lessersunda/lexirumah-data/releases', label='released version')}
        of data curated at
        ${h.external_link('https://github.com/lessersunda/lexirumah-data', label='github:lessersunda/lexirumah-data')}.
    </%util:well>
</%def>

<h2>Welcome to LexiRumah</h2>

<p class="lead"> LexiRumah (from <i>Lexicon</i> and Indonesian <i>Rumah</i>
    = house) is an online database containing lexical data 
    for languages of Eastern Indonesian and Timor-Leste.  
    The database was set up and is maintained by the
    NWO Vici
    project <a href="http://www.vici.marianklamer.org/">“Reconstructing
    the past through languages of the present: the Lesser Sunda
    Islands”</a> at Leiden University.
</p>

<h3>Presentation of Data</h3>
<p>
    Each word in LexiRumah belongs to a particular language and a particular concept.
    In the case of data drawn from survey word-lists,
    the concept to which a word matches was the prompt which elicited the word.
    (In nearly all cases this prompt was given in Indonesian/Malay).
    For data from published sources the concept to which a word matches is that
    judged most similar to the gloss or definition given in the source.
</p>

<p>
    Each word is associated with three different transcriptions.
    Firstly, there is a standardised transcription (Form IPA) using the symbols of the
    International Phonetic Alphabet which follows the conventions of
    CLTS (Cross-Linguistic Transcription System).
    Depending on the nature of the source,
    and the level of knowledge of the language,
    this transcription is either phonemic or phonetic,
    bearing in mind the conventions of CLTS. In addition,
    in nearly all cases a phonemic sequence of two identical vowels
    is transcribed as a single long vowel (/VV/ → &lt;Vː&gt;)
    in order to ease cross-linguistic comparison.
</p>

<p>
    Secondly, each word has an orthographic transcription (Orthography).
    For languages which have an established orthography which is
    used to some extent by speakers and/or linguists, this transcription
    follows the conventions of the established orthography.
    For languages which do not yet have any orthography
    this transcription mostly follows the conventions of Indonesian.
</p>

<p>
    Finally, the representation of the word in the original source
    from which the word is derived is also given.
</p>

<p>
    To take one simple example, the Ili'uun (eray1237) word which matches
    the concept ‘hide’ was given in the original source as &lt;ladjōk&gt;.
    This has been standardised to IPA /lad͡ʒoːk/ and is transcribed
    orthographically <i>lajook</i> in rough accordance
    with Indonesian orthography.
</p>

<h3>Data Provenance</h3>
    The data represented in LexiRumah comes from published sources,
    as well as from survey work. All data is attributed and linked
    to the source from which it comes.
    In addition to wordlists provided by individual linguists (as attributed),
    survey work executed in the following projects is also present in LexiRumah.
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
  LexiRumah is a separate publication by Gereon A. Kaiping, Owen Edwards, and Marian Klamer. We recommend you cite it as
  <blockquote><%block name="cite_us">Kaiping, Gereon A., Owen Edwards, and Marian Klamer (eds.). 2019.
    %if request.dataset.description:
    <i>${request.dataset.name} – ${request.dataset.description}</i>.
    %else:
    <i>${request.dataset.name}</i>.
    %endif
    Leiden: Leiden University Centre for
    Linguistics. Available online
    at <a href="">${req.resource_url(req.dataset)}</a>. Accessed on
    ${date.today()}.  </%block>
  </blockquote>
</p>

<p>
    It is important to cite the specific reference (printed source, or data collector)
    that the data you cite comes from.
    Every item in the database is linked to its reference
    and should be cited accordingly.
    Thus, for instance if you wish to cite the Hewa (sika1262-hewa)
    word <i>taʔa</i> ‘betel vive’. You would do so as following:
    “The Hewa word for ‘betel vine’ is <i>taʔa</i> (Fricke 2014)”.
    With the following entry in your list of references:

  <blockquote>
    Fricke, Hanna. 2014.
    <i>Topics in the grammar of Hewa: A variety of Sika in Eastern Flores, Indonesia.</i>
    München: Lincom Europa
  </blockquote>
</p>

<p>
    If you do not have access to the original source,
    as is often the case for survey word-list data,
    it is still insufficient to cite only LexiRumah.
    Instead, cite the original source and LexiRumah in the following way:
    “The Iha word for ‘thorn’ [ˈᵑg͡bɛm] contains a voiced pre-nasalised
    co-articulated bilabial velar plosive (Donohue 2010 in Kaiping, Edwards and Klamer 2019)”
</p>

<p>
    Then in your reference list you will have one reference
    for LexiRumah and one for Donohue (2010).
    You may wish (or your publisher may require) you to treat this original
    source as being “in” LexiRumah, in which case you can
    treat it like a chapter in a book and cite it as follows:
</p>

  <blockquote>
    Donohue, Mark. 2010.
    Bomberai survey word lists.
    in
    Kaiping, Gereon A., Owen Edwards, and Marian Klamer (eds.). 2019.
    %if request.dataset.description:
    <i>${request.dataset.name} – ${request.dataset.description}</i>.
    %else:
    <i>${request.dataset.name}</i>.
    %endif
    Leiden: Leiden University Centre for
    Linguistics. Available online
    at <a href="">${req.resource_url(req.dataset)}</a>. Accessed on
    ${date.today()}.
  </blockquote>
</p>

<h3>Cognate sets</h3>
<p>
    The Cognate sets section contains sets of words which are formally and semantically similar,
    and thus possibly cognate (inherited from a single ancestral etymon).
    These cognate sets are automatically detected with LexStat
    and are not a result of the application of the traditional comparative method through
    identification of regular correspondences.
    The alignment column within a single cognate set shows which segments of
    each word correspond to one another,
    again on the basis of automatic detection.
</p>

<p>
    Each cognate set is named after a randomly selected term from all
    forms in the cognate class. This term is not necessarily a
    reconstructed proto-form or a particularly
    frequent or representative form. 
</p>

    <table class="table table-nonfluid">
        <tbody>
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
                <th><a href="${request.route_url('sources')}">Sources</a></th>
                <td class="right">${'{:,}'.format(stats['source'])}</td>
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
