import json
import requests
from flask import Flask, render_template
import orgs

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

def get_pr_list_resource(url):
  response = requests.get(url)
  return json.loads(response.text)#, object_hook=datetime_encoder)

def get(projects):
  compiled_prs = {}
  for project in projects:
    prs = get_pr_list_resource(project['link'] + '/pulls')
    for pr in prs:
      # links could be normalized here to better-eliminate duplicates
      bare_pr = {
        'title': pr['title'],
        'link': pr['html_url'],
        'created_at': pr['created_at']
      }
      compiled_prs[bare_pr['created_at']] = bare_pr

  return compiled_prs

@app.route('/')
def hello():
  orgs = {}
  for org in orgs.orgs:
    orgs[org] = {}
    projects = get_projects(org)
    orgs[org]['projects'] = projects
    for project in projects:
      project['pull_requests'] = get_pull_requests(project)
      pull_requests = get_pull_requests(project)

    orgs[org] = get_prs(org)

  return render_template('index.html', projects=default.projects, prs=prs)
  compiled_prs = get(default.projects)
  for date in sorted(compiled_prs.iterkeys()):
    prs.append(compiled_prs[date])


if __name__ == '__main__':
  app.run(debug=True)
