import json
import requests
from flask import Flask, render_template, jsonify
import config

app = Flask(__name__)

def datetime_encoder(o):
    from datetime import date
    from datetime import datetime
    if isinstance(o, datetime):
        return o.isoformat()
    elif isinstance(o, date):
        return o.isoformat()
    else:
        raise TypeError(repr(o) + " is not JSON serializable")

@app.route('/')
def pull_requests():
    return jsonify(build_page_data(config.organization_names))
#    return render_template(
#        'index.html',
#        orgs=build_page_data(config.organization_names)
#    )

def build_page_data(organization_names):
    orgs = []
    org_urls = get_org_urls(organization_names)
    for org_url in org_urls:
        organization = get_organization(org_url)
        orgs.append(organization)
    return orgs

def get_org_urls(names):
    urls = []
    for name in names:
        urls.append(config.api_url + '/orgs/' + name)
    return urls

def get_organization(org_url):
    full_organization = api_get(org_url)
    return {
        'name': full_organization['name'],
        'api_url': full_organization['url'],
        'html_url': full_organization['html_url'],
        'repos': get_repos(full_organization['url'] + '/repos')
    }

def api_get(resource):
    return json.loads(requests.get(resource).text)

def get_repos(repos_url):
    repos = []
    full_repos = api_get(repos_url)
    for full_repo in full_repos:
        repo = make_minimal_repo(full_repo)
        repos.append(repo)
    return repos

def make_minimal_repo(full_repo):
    pull_requests = get_pull_requests(full_repo['url'] + '/pulls/open')
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

    return pulls

def make_minimal_pull(full_pull):
    comments = get_comments(full_pull['_links']['comments']['href'])
    return {
        'number': full_pull['number'],
        'name': full_pull['title'],
        'description': full_pull['body'],
        'state': full_pull['open'],
        'created_at': full_pull['created_at'],
        'updated_at': full_pull['updated_at'],
        'api_url': full_pull['api_url'],
        'html_url': full_pull['html_url'],
        'comments': comments,
        'comment_count': len(comments),
    }

def get_comments(comments_url):
    full_comments = api_get(comments_url)
    return {
        'body': full_comments['body'],
        'id': full_comments['id'],
        'api_url': full_comments['url'],
        'html_url': full_comments['_links']['html']['href'],
        'user': full_comments['user'],
        'created_at': full_comments['created_at'],
        'updated_at': full_comments['updated_at'],
        'position': full_comments['position'],
    }

if __name__ == '__main__':
  app.run(debug=True)
