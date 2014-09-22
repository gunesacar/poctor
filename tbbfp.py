"""
Based on EFF's Panopticlick, Flaskr
https://panopticlick.eff.org
https://github.com/mitsuhiko/flask/blob/master/examples/flaskr/
"""
from __future__ import division
import json
import sqlite3
from os.path import join as joinp
from flask import Flask, render_template, request, redirect, url_for, Markup, g
from fp_common import TBFingerprint, DB_CONN_TIMEOUT, hash_text
from math import log
app = Flask(__name__)

DEBUGMODE=False  # False in production
DBFILENAME='tbbfp.db'
# Load default config and override config from an environment variable
if DEBUGMODE:
    app.config.update(dict(
        DATABASE=joinp(app.root_path, DBFILENAME),
        DEBUG=DEBUGMODE,
        SECRET_KEY='AJSDHFLAQWT346795URESHJ9FLA79SKHJDFALIUA78CNIA587U54B234AKS24243DF'
    ))
else:
    app.config.from_envvar('FLASKR_SETTINGS', silent=False)  # in production 

        
@app.route('/', methods=['GET', 'POST'])
def index():
    # we lose the http params on ajax post !!! 
    action = get_req_arg('action', None)
    record_fp, tbb_v = get_visit_params()
    if action is None:  # just landed
        return render_template('front.html', record_fp=record_fp, tbb_v=tbb_v)
    elif action == "test":  # linked from Test me button on the landing page
        js_enabled = get_req_arg('js', "no")
        if js_enabled == "yes":  # will POST client-side FP 
            return render_template('resultjs.html', result_table='')
        else:  # JS disabled, record server side FP only
            fp = TBFingerprint()
            fp.tbb_v = tbb_v
            fp = detect_server_side_fp(fp)
            # if record_fp == 'yes':
            record_fingerprint(fp)
            result_table = entropy_table(fp);
            return render_template('result.html', result_table=result_table)
    elif action == "ajax_post_client_vars":  # post from AJAX, combine with server-side and record
        # we sometimes get multuple (2) POSTs since it times out and retries until we respond
        fp = TBFingerprint()
        fp.tbb_v = tbb_v
        detect_server_side_fp(fp)
        detect_client_side_fp(fp)
        #if record_fp == 'yes':  # handle cases where rec-no and unique visit causes div by zero errors 
        record_fingerprint(fp)
        return entropy_table(fp)  # echoed by the AJAX-POST endpoint, will be inserted to div#result.
    else:
        return "Dunno what to do here!"

# TODO: check if we need use lock/acquire here
def connect_db():
    """Connect to database."""
    rv = sqlite3.connect(app.config['DATABASE'], timeout=DB_CONN_TIMEOUT)
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def count_similar(var, val, tbb_v):
    """Count similar entries."""
    try:
        return get_db().execute("""SELECT total FROM totals WHERE 
            variable=? AND value=? AND tbb_v=?""", [var, val, tbb_v]).fetchone()[0]
    except:
        return 0

def get_info_metrics(var, val, tbb_v, tbb_v_total):
    """Return surpisal and "one_in_x" value for a (var, val, tbb_v) tuple."""
    similar_count = count_similar(var, val, tbb_v)
    return get_entropy(similar_count, tbb_v_total), round(tbb_v_total / similar_count, 2)

def get_entropy(count_similar, count_total):
    """Return the surprisal value."""
    return 0 + round(-log(count_similar / count_total, 2) , 2)  # add 0 to prevent -0.0

def get_overall_metrics(fp, tbb_v_total):
    """Return info metrics for combined fingerprint."""
    return get_info_metrics('signature', fp.signature, fp.tbb_v, tbb_v_total)  # TODO !!!

def get_res_dict_for_var(var, value, tbb_v, tbb_v_total):
    """Return info metrics for a variable as dict."""
    surpisal, one_in_x = get_info_metrics(var, value, tbb_v, tbb_v_total)
    return {"var": var, "bits": surpisal, "one_in_x": one_in_x, "value": value}

def entropy_table(fp):
    """Return the result table in HTML."""
    tbb_v_total = count_similar('count', '', fp.tbb_v)  # total entries with this tbb_v
    surpisal, one_in_x = get_overall_metrics(fp, tbb_v_total)
    res_rows = [get_res_dict_for_var(var, val, fp.tbb_v, tbb_v_total) for var, val in fp]
    res_dict = {"res_rows": res_rows, "tot_surpisal": surpisal,
                "tbb_v_total": tbb_v_total, "tot_one_in_x":one_in_x,
                 "tbb_v": fp.tbb_v}
    return render_template('entropy_table.html', res_dict=res_dict)


def upsert_totals(var, val, tbb_v):
    """Insert into or update totals table."""
    db = get_db()
    try:
        db.execute('insert into totals values (?, ?, ?, ?, ?)',
               [None, var, val, tbb_v, 1])
    except sqlite3.IntegrityError, err:  # throws when (variable, value, tbb_v) is already present
        db.execute('UPDATE TOTALS SET total=total+1 WHERE variable=? AND value=? AND tbb_v=?',
                   [var, val, tbb_v])
    db.commit()

# TODO: decide which values should be stored as hash
# EFF's Panopticlick keeps the hash of the following in the totals table:
# plugins, fonts, user_agent, http_accept, supercookies
# But the raw values are stored in a separate (fingerprint_) table, which we possibly won't have (?)
def value_or_hash(var, val):
    """Return either the hash of the value."""
    return val  # TODO: revise

def record_fingerprint(fp):
    fp.signature = hash_text(' '.join(v for _, v in fp))
    upsert_totals('count', '', fp.tbb_v)
    for var, val in fp:
        upsert_totals(var, value_or_hash(var, val), fp.tbb_v)

# TODO: Add support for POST if we settle on that
def get_visit_params():
    """Return the TBB version and record bool from GET params."""
    return get_req_arg('rec', 'no'), get_req_arg('tbb_v', 'unknown')

def get_http_header(header, default=''):
    """Return the value of an HTTP header."""
    try:
        return request.headers.get(header, default)
    except:  # no headers at all, this should not be possible, log? !!!
        return default

def get_req_arg(param_name, default=''):
    """Return HTTP parameter value."""
    return request.args.get(param_name) or default
    
def get_req_form_data(key, default=''):
    """Return submitted POST data."""
    return request.form[key] or default

def get_accept_headers():
    """Return HTTP accept headers in concatenated form.""" 
    return " ".join((get_http_header('Accept'),
                     get_http_header('Accept-Charset'),
                     get_http_header('Accept-Encoding'),
                     get_http_header('Accept-Language')
                     ))

# TODO: TCP timestamps
# TODO: handle pixel requests  initiated by CSS media queries, use session cookie to combine
# What if both JS and cookies are disabled ? !!!
def detect_server_side_fp(fp):
    """Collect and add server side fingerprint to given object.""" 
    fp.cookie_enabled = 'Yes' if len(request.cookies) else 'No'
    fp.user_agent =  get_http_header('User-Agent')
    fp.http_accept = get_accept_headers()
    return fp

def detect_client_side_fp(fp):
    """TODO process, form data."""
    fp.js_enabled = '1'
    fp.video = get_req_form_data('video')
    fp.js_user_agent = get_req_form_data('js_user_agent')
    fp.plugins = get_req_form_data('plugins')
    fp.timezone = get_req_form_data('timezone')
    fp.fonts = get_req_form_data('fonts')
    fp.cookie_enabled = get_req_form_data('cookie_enabled')
    fp.supercookies = get_req_form_data('supercookies')
    return fp

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
