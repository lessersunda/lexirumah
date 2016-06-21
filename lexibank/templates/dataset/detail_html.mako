<%inherit file="../home_comp.mako"/>

<%def name="sidebar()">
##    <div class="well">
 ##       <h3>Sidebar</h3>
##        <p>
##            Content
##        </p>
##    </div>
</%def>

<h2>Welcome to lexiSunDa</h2>

<p class="lead">
    The lexicon of the lesser Sunda Islands languages database.
</p>
    <table class="table table-nonfluid">
        <tbody>
            <tr><th>Wordlists</th><td></td><td class="right">${stats['contribution']}</td></tr>
            <tr><th>Lexical items</th><td></td><td class="right">${stats['value']}</td></tr>
            <tr><th>Concepts</th><td></td><td class="right">${stats['parameter']}</td></tr>
            <tr><th>Languages</th><td></td><td class="right">${stats['language']}</td></tr>
            <tr><th>Families</th><td></td><td class="right">${stats['family']}</td></tr>
            % for fam, count in families:
                <tr><td></td><th>${fam}</th><td class="right">${count}</td></tr>
            % endfor
        </tbody>
    </table>
