<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%block name="title">${_('Family')} ${ctx.name}</%block>

<h2>${_('Family')} ${ctx.name}</h2>
