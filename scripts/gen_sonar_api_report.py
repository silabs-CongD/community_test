import requests
import sys
import os

REPO_NAME   = sys.argv[1]
REPO_BRANCH = sys.argv[2]
SONAR_TOKEN = sys.argv[3]

############ Debug input params
print(50*"*")
print("REPO_NAME:", REPO_NAME)
print("REPO_BRANCH:", REPO_BRANCH)

# Set up the headers with the Bearer token
headers = {
  "Authorization": f"Bearer {SONAR_TOKEN}"
}

# Fetch measures from SonarQube API
api_url_issues = "https://sonarqube.silabs.net/api/issues/search?componentKeys=" + REPO_NAME + "&branch=" + REPO_BRANCH + "&resolved=false&inNewCodePeriod=true"
response_issues = requests.get(api_url_issues, headers=headers)
data_issues = response_issues.json()
issues = data_issues['issues']

#####################
# Security hotpot
api_url_security_hotpot = "https://sonarqube.silabs.net/api/hotspots/search?project=" + REPO_NAME + "&branch=" + REPO_BRANCH
response_hotpot = requests.get(api_url_security_hotpot, headers=headers)
data_security_hotpot = response_hotpot.json()
security_hotpots = data_security_hotpot['hotspots']

# Generate HTML report
html_report = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>SonarQube Detailed Report</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 40px; }
    h1, h2, h3 { color: #333; }
    table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
    th { background-color: #f2f2f2; }
    .issue { margin-bottom: 10px; }
  </style>
</head>
<body>
  <h1>SonarQube Detailed Report</h1>
  <h2>Issues</h2>
  <table>
    <tr>
      <th>Type</th>
      <th>Severity</th>
      <th>Message</th>
      <th>File</th>
      <th>Line</th>
    </tr>
 """

# Append issues to HTML report
for issue in issues:
  severity = issue.get('severity', 'N/A')
  if severity == "MINOR":
    continue

  html_report += """
    <tr>
      <td>{type}</td>
      <td>{severity}</td>
      <td>{message}</td>
      <td>{file}</td>
      <td>{line}</td>
    </tr>
  """.format(
    type=issue.get('type', 'N/A'),
    severity=issue.get('severity', 'N/A'),
    message=issue.get('message', 'N/A'),
    file=issue.get('component', 'N/A').split(':')[-1],
    line=issue.get('line', 'N/A') if 'line' in issue else 'N/A'
  )

for issue in security_hotpots:
  severity = issue.get('severity', 'N/A')
  if severity == "MINOR":
    continue

  html_report += """
    <tr>
      <td>{type}</td>
      <td>{severity}</td>
      <td>{message}</td>
      <td>{file}</td>
      <td>{line}</td>
    </tr>
  """.format(
    type=issue.get('securityCategory', 'N/A'),
    severity=issue.get('vulnerabilityProbability', 'N/A'),
    message=issue.get('message', 'N/A'),
    file=issue.get('component', 'N/A').split(':')[-1],
    line=issue.get('line', 'N/A') if 'line' in issue else 'N/A'
  )

html_report += """
  </table>
</body>
</html>
"""

# Save HTML report to a file
report_file_path = os.path.join(os.environ.get("GITHUB_WORKSPACE"), "sonar_api_report.html")
with open(report_file_path, 'w') as file:
  file.write(html_report)