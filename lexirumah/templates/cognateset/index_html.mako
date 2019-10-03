<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "cognatesets" %>


<h2>${_('Cognate sets')}</h2>
<p style="font-size:80%">
  The forms listed in the “Name” column are a random representative
  from all forms in the cognate class, not necessarily a reconstructed
  proto-form or a particularly frequent or representative form. They
  only serve as a rough illustration of the forms to be found in the
  set.
</p>
<div>
    ${ctx.render()}
</div>
