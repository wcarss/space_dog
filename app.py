import json
import requests
import config
from flask import Flask, render_template, jsonify
import datetime

app = Flask(__name__)
count = 0

def datetime_encoder(o):
    if isinstance(o, datetime.datetime):
        return o.isoformat()
    elif isinstance(o, datetime.date):
        return o.isoformat()
    else:
        raise TypeError(repr(o) + " is not JSON serializable")

@app.route('/js')
def json_orgs():
    return jsonify({
        'organizations': build_page_data(config.organization_names),
        'fetched_at': datetime.datetime.now().isoformat()
    })

@app.route('/')
def fake_index():
    with open("fake_orgs.js") as fake_org_file:
        fake_orgs = json.load(fake_org_file)
    return render_template(
        'index.html',
        organizations=fake_orgs['organizations'],
        fetched_at=fake_orgs['fetched_at']
    )

def index():
    return render_template(
        'index.html',
        orgs=build_page_data(config.organization_names)
    )

def build_page_data(organization_names):
    orgs = []
    for name in organization_names:
        organization = get_organization(config.api_url + '/orgs/' + name)
        orgs.append(organization)
    return orgs

def get_organization(org_url):
    full_organization = api_get(org_url)
    return {
        'name': full_organization['login'],
        'description': full_organization['name'],
        'api_url': full_organization['url'],
        'html_url': full_organization['html_url'],
        'repos': get_repos(full_organization['url'] + '/repos?per_page=100')
    }

def api_get(resource):
    global count
    count += 1
    print "Made %s calls." % count
    response = requests.get(resource)
    #print "Requested: %s" % resource
    #print "Response headers: %s" % response.headers
    return response.json()
    #return json.loads(requests.get(resource).text)

def get_repos(repos_url):
    repos = []
    full_repos = api_get(repos_url)
    for full_repo in full_repos:
        repo = make_minimal_repo(full_repo)
        repos.append(repo)
    return repos

def make_minimal_repo(full_repo):
    pull_requests = get_pull_requests(full_repo['url'] + '/pulls?state=open?per_page=100')
    return {
        'name': full_repo['name'],
        'description': full_repo['description'],
        'api_url': full_repo['url'],
        'html_url': full_repo['html_url'],
        'pull_requests': pull_requests,
        'pull_request_count': len(pull_requests),
    }

def get_pull_requests(pull_url):
    pulls = []
    full_pulls = api_get(pull_url)
    for full_pull in full_pulls:
        pull = make_minimal_pull(full_pull)
        pulls.append(pull)

    pulls.reverse()
    return pulls

def make_minimal_pull(full_pull):
    #print full_pull
    comments = get_comments(full_pull['_links']['review_comments']['href'])
    avatar_url = full_pull['user']['avatar_url']
    default_avatar_url = "https://secure.gravatar.com/avatar/d41d8cd98f00b204e9800998ecf8427e?d=https://github.2ndsiteinc.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png"
    if avatar_url == default_avatar_url:
        avatar_url = avatar_url.replace(".2ndsiteinc", "")
    return {
        'number': full_pull['number'],
        'name': full_pull['title'],
        'description': full_pull['body'],
        'state': full_pull['state'],
        'created_at': full_pull['created_at'],
        'updated_at': full_pull['updated_at'],
        'user': full_pull['user']['login'],
        'avatar_url': avatar_url,
        'api_url': full_pull['url'],
        'html_url': full_pull['html_url'],
        #'comments': comments,
        'comment_count': len(comments),
    }

def get_comments(comments_url):
    comments = []
    full_comments = api_get(comments_url + '?per_page=100')
    #for full_comment in full_comments:
    #    comments.append(make_minimal_comment(full_comment))
    return full_comments

def make_minimal_comment(full_comment):
    #print "full comment: %s" % full_comment
    return {
        'body': full_comment['body'],
        'id': full_comment['id'],
        'api_url': full_comment['url'],
        'html_url': full_comment['_links']['html']['href'],
        'user': full_comment['user']['login'],
        'created_at': full_comment['created_at'],
        'updated_at': full_comment['updated_at'],
        'position': full_comment['position'],
    }

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0')
