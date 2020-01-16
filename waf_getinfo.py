import sys
import os
import boto3
from json2html import *
import numpy as np
import pdfkit
import matplotlib
import matplotlib.pyplot as plt

session = boto3.Session(profile_name=sys.argv[1])
client = session.client('dynamodb', region_name='us-east-1')

hostname = sys.argv[2]

response = client.scan(
	TableName='fail2ban',
	FilterExpression='f2b_hostname = :host_val and f2b_date BETWEEN :low_date_val and :high_date_val',
	ExpressionAttributeValues={
		":host_val": {"S": hostname},
		":low_date_val": {"S": sys.argv[3]}, 
		":high_date_val": {"S": sys.argv[4]}
	},
	ProjectionExpression='f2b_ip, f2b_date, f2b_geoip'
)
new_response = response['Items']

count = response['Count']

countries = []
dates = []

for i in range(count):
	new_response[i]['Date'] = new_response[i].pop('f2b_date')
	new_response[i]['IP'] = new_response[i].pop('f2b_ip')
	new_response[i]['Country'] = new_response[i].pop('f2b_geoip')
	new_response[i]['SECID'] = i + 1
	new_response[i] = dict(sorted(new_response[i].items(), key=lambda x: x[0], reverse=True))
	countries.append(new_response[i]['Country']['S'])
	dates.append(new_response[i]['Date']['S'])

#print(new_response)
table = json2html.convert(json = new_response).replace('<td><table border="1"><tr><th>S</th>', '').replace('</tr></table></td>', '').replace('<table border="1">', '<table id="info-table" style="width:100%">')

# count ips by data

date_ip = dict(map(lambda x : (x, list(dates).count(x)), dates))
date = []
count_ip_by_date = []
for k in date_ip:
	date.append(k)
	count_ip_by_date.append(date_ip[k])

fig, ax = plt.subplots(figsize=(15, 11))
ax.set_ylabel('Number of IPs')
ax.set_xlabel('Date')
ax.set_title('Blocked IPs by date')
plt.xticks(rotation=90)
plt.plot(date, count_ip_by_date)
fig.savefig('ip_by_date.png')


# count ips by countries
country_ip = dict(map(lambda x : (x, list(countries).count(x)), countries))
county_name = []
ip_blocked = []
for k in country_ip:
	county_name.append(k)
	ip_blocked.append(country_ip[k])

N = len(county_name)

ind = np.arange(N)
width = 0.5

fig, ax = plt.subplots(figsize=(12,6))

ax.grid(color='k', linewidth=.5, linestyle=':')
ax.set_ylabel('Number of IPs')
ax.set_xlabel('Country')
ax.set_title('Blocked IPs by countries')

p = ax.bar(ind, ip_blocked, width, color="#9BD3DA")
plt.xticks(ind, county_name)

fig.savefig('ip_by_countries.png')

head = '''<html>
<head>
	<style>
		table {
  			border: 1px solid black;
  			border-collapse: collapse;
  			text-align: center;
		}
		th {
			background-color: #dddddd;
		}
		th, td {
  			border: 1px solid black;
  			padding: 5px;
		}
		.main {
			margin-left: 20%;
			margin-right: 20%;
		}
		img {
			width: 100%;
		}
	</style>
</head>
<body>
<div class="main">
<h1> Blocked IP Addresses </h1>
<p>The following IP Addresses are blocked by Web Application Firewall (WAF).<p>
<br>
<p>Total Blocked IPs: ''' + str(count) + '</p>'

#############Write to file############
path = 'report_' + hostname + '_date_' + sys.argv[3] + ' - ' + sys.argv[4] + '.html'
pdf = 'report_' + hostname + '_date_' + sys.argv[3] + ' - ' + sys.argv[4] +'.pdf'
report_file = open(path, 'w')
report_file.write(head + table + '<div><img src="ip_by_countries.png"/></div><div><img src="ip_by_date.png"/></div></div></body></html>')
report_file.close()

if pdfkit.from_file(path, pdf):
	os.remove(path)

##############Upload to S3################
s3 = session.client('s3')

bucket_name = 'report.fail2ban'

s3.upload_file(pdf, bucket_name, pdf)
