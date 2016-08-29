from pyramid.response import Response
import transaction
from lexibank.models import LexibankLanguage, Cognateset, Counterpart
from clld.db.models.common import Contributor, Contribution, ContributionContributor
from sqlalchemy.orm.exc import NoResultFound, FlushError
from sqlalchemy.exc import IntegrityError, InvalidRequestError, CompileError
from clld.db.meta import DBSession, Base
import json
from sqlalchemy.orm.collections import InstrumentedList

models = {"Language": LexibankLanguage,
          "ContributionContributor": ContributionContributor,
          "Contributor": Contributor,
          "Counterpart": Counterpart,
          "Cognateset": Cognateset,
          "Contribution": Contribution}
             
def form(message = ""):
    reply = """
<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js"></script> 

<script>
// Post to the provided URL with the specified parameters.
function post(path, parameters) {
    var form = $('<form></form>');

    form.attr('method', 'post');
    form.attr('action', path);

    $.each(parameters, function(key, value) {
        var field = $('<input></input>');

        field.attr('type', 'hidden');
        field.attr('name', key);
        field.attr('value', value);

        form.append(field);
    });

    // The form needs to be a part of the document in
    // order for us to be able to submit it.
    $(document.body).append(form);
    form.submit();
}
    
function getCookie(cname) {
    var name = cname + '=';
    var ca = document.cookie.split(';');
    for(var i = 0; i <ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length,c.length);
        }
    }
    return '';
} 

function getCookiesWith(match) {
    var matches = {};
    var ca = document.cookie.split(';');
    for(var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') {
            c = c.substring(1);
        }
        equalsign = c.indexOf('=');
        matchposition = c.indexOf(match);
        if (0 <= matchposition && matchposition < equalsign) {
            matches[c.substring(0, equalsign)] =\
                c.substring(equalsign+1,c.length).replace(/&quot/g, '&quot;');
        }
    }
    return matches;
} 


$(document).ready(function(){
    var key = document.cookie;
    $('#author').attr('value', getCookie('author')); 
    var changes = getCookiesWith('__');
    for(var key in changes) {
        var value = changes[key];
        if (key.indexOf('ADD') > 0) {
            $('#submit').prepend('\
                <label id="label_'+key.replace('.','x')+'" for="'+key+'">'+key+':</label>\
                <input id="'+key.replace('.','x')+'" name="'+key+'" value="'+value+'" />\
                <input id="remove_'+key.replace('.','x')+'" type="submit" value="remove" onclick="remove(\\''+key+'\\')"/>\
                <br id="br_'+key.replace('.','x')+'"/>')
        } else {
            $('#submit').prepend('\
                <label id="label_'+key.replace('.','x')+'" for="'+key+'">'+key+':</label>\
                <input id="'+key.replace('.','x')+'" name="'+key+'" value="'+value+'" />\
                <input id="remove_'+key.replace('.','x')+'" type="submit" value="remove" onclick="remove(\\''+key+'\\')"/>\
                <br id="br_'+key.replace('.','x')+'"/>')
        }
    }
})

function set_magic(){
    $('#magic').attr('name', $('#label_magic').val())
}

function set_more_magic(){
    $('#magic__ADD').attr('name', $('#label_magic__ADD').val()+"__ADD");
}

function remove(name){
    $('#'+name.replace('.','x')).remove();
    $('#remove_'+name.replace('.','x')).remove();
    $('#label_'+name.replace('.','x')).remove();
    $('#br_'+name.replace('.','x')).remove();
}

function delete_cookies(){
    set_magic();
    set_more_magic();
    var ca = document.cookie.split(';');
    for(var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') {
            c = c.substring(1);
        }
        c = c.substring(0, c.indexOf('='))
        if (c != 'author') {
            document.cookie = c+'=; expires=Thu, 01 Jan 1970 00:00:00 UTC';
        }
    }
}

</script> """ + ("<h1>Results</h1>"+message
           if message
           else "") + """
<h1>Changes to be submitted to the database</h1>
<form id="submit" style="text-align:right" action="/submit_edit" method="post">
    Add <input id="label_magic__ADD" value="magic" onchange="set_more_magic()">:
    <input id="magic__ADD" name="magic__ADD" />
    <input id="remove_magic__ADD" type="submit" value="remove" onclick="remove('magic__ADD')"/>
    <br id="br_magic__ADD"/>
    <input id="label_magic" value="magic__magic.magic" onchange="set_magic()"/>: 
    <input id="magic" name="magic_content" value="MAGIC"/>
    <input id="remove_magic" type="submit" value="remove" onclick="remove('magic')"/>
    <br id="br_magic"/>
    <textarea id="reason" name="reason" style="width:100%"/>
    Reason and Sources
    </textarea>
    <br />
    <label for="author">Author of changes:</label>
    <input id="author" name="author" value="NAME"/>
    <br />
    <input type="submit" onmousedown="delete_cookies()" value="Submit changes" />
</form>
"""  
    return Response(reply)

def submit(factory, req):
    transaction.savepoint()
    reason = None
    author = None
    changes = []
    for key, value in req.POST.items():
        if key.strip().lower() == 'reason':
            reason = value
            if reason.strip().lower() == "reason and sources":
                return form("No reason given")
            continue
        if key.strip().lower() == 'author':
            author = value.strip()
            if not author:
                return form("No author given")
            continue

        try:
            model_string, identifier = key.split("__")
        except ValueError:
            return form("Key malformed: Expected model and identifier to be separated by __, got {:s}".format(key))
        try:
            model = models[model_string]
        except KeyError:
            return form("Model undefined: {:s}".format(model_string))

        if identifier == "ADD":
            # Read properties for a new object from the string
            # First, check that the value string is well-formed.
            try:
                values = json.loads(value)
            except json.decoder.JSONDecodeError:
                return form("Bad json: {:s}".format(value))
            for c in model.__table__.columns:
                column = c.name
                if column.endswith("_pk"):
                    object_column = column[:-3]
                    if object_column in values:
                        object_id = values[object_column]
                        values[column] = getattr(
                            model, object_column).comparator.property.argument.get(object_id).pk
                        del values[object_column]
            insert_stmt = model.__table__.insert(values)
            try:
                print(insert_stmt)
                print(insert_stmt.parameters)
                insert_stmt.execute()
            except (CompileError, IntegrityError) as i:
                return form("Conflict in database: {:}".format(i))
            return Response("Yay!")
        else:
            # Change a property of an object
            try:
                object_id, attribute = identifier.split(".")
            except ValueError:
                return form("Identifier malformed: One dot expected, got {:s}".format(identifier))
            try:
                object = model.get(object_id)
            except NoResultFound:
                return form("No such {:}: {:s}".format(model, object_id))
            try:
                oldvalue = getattr(object, attribute)
                print("Old value of {:}.{:s} was {:}".format(
                    object, attribute, oldvalue))
            except AttributeError:
                return form("No attribute {:s}: {:}".format(
                    attribute, dir(object)))
            if isinstance(oldvalue, dict) and attribute=="cognatesets_with_properties":
                def convert(newvalue):
                    return {Cognateset.get(x):{}
                            for x in newvalue.split(",")}
            elif isinstance(oldvalue, Base):
                convert = type(oldvalue).get
            else:
                convert = type(oldvalue)
            try:
                value = convert(value)
            except (ValueError, NoResultFound) as problem:
                return form("Could not convert {:s} using {:}: {:}".format(
                    value,
                    convert,
                    problem))
            try:
                setattr(object, attribute, value)
            except AttributeError:
                return form("Could not set {:}.{:s} to {:}".format(
                    object,
                    attribute,
                    value))
            changes.append((object, attribute, oldvalue, value))
            # Commit changes, catch errors
    try:
        transaction.commit()
    except (FlushError, IntegrityError, InvalidRequestError):
        DBSession.rollback()
        transaction.abort()
        return form("Transaction failed.")

    return form()

def addtosubmit(factory, req):
    return Response("""
<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js"></script> 
    
<script>
function prompt_new_value_for(field_identifier) {
    set_to = window.prompt('New value for '+field_identifier);
    if (set_to==null) {
        return
    }
    document.cookie = field_identifier+'='+set_to;
}
</script>
<h1 ondblclick="prompt_new_value_for('Contributor__gereon.name')"> Does something! </h1>
<h1 ondblclick="prompt_new_value_for('Contributor__gereon.nothinglikethis')"> No such attribute! </h1>
<h1 ondblclick="prompt_new_value_for('Contributor__gereon.pk')"> Restricted attribute! </h1>
<h1 ondblclick="prompt_new_value_for('Contribution__dummy.contributor_assocs')"> Other class! </h1>
<h1 ondblclick="prompt_new_value_for('author')"> Author!</h1>
<p id="p">
</p>
""")
    
