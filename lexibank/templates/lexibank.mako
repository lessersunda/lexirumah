<%inherit file="app.mako"/>

##
## define app-level blocks:
## #263681
<%block name="brand">
    <a class="brand" href="${request.route_url('dataset')}"
       style="padding-top: 3px; padding-bottom: 1px;">
        <img width="55" src="${request.static_url('lexibank:static/logo.png')}"/>
    </a>
</%block>

${next.body()}
