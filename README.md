## About

```text
Author:   Diana Chajkovska
Release:  16th Jan, 2020
```
This script make monthly pdf report for website and put it on s3. 
PDF report shows information about blocked IP`s and gives some analytics using graps: 'Blocked IPs by countries', 'Blocked IPs by date'. IP Addresses are blocked by Web Application Firewall (WAF).
All information was taken from DynamoDB table.

## Usage
To run the script:

	python3 waf_getinfo.py creds_name hostname from_date to_date
example:
	
	python3 waf_getinfo.py swarming tiemart.com 2019-02-13 2019-03-13

required libs:

	- boto3
		install: pip install boto3
	- json2html
		install: pip install json2html
	- numpy
		install:  pip install numpy
	- pdfkit
		install: pip install pdfkit
			 sudo apt-get install wkhtmltopdf
	- matplotlib
		install: pip install matplotlib

## Examples
Graphs in report:
![ip_by_countries](https://user-images.githubusercontent.com/50831927/72558147-cccffd00-38aa-11ea-8851-74ef6b004cbf.png)

![ip_by_date](https://user-images.githubusercontent.com/50831927/72558263-01dc4f80-38ab-11ea-9bd6-f69a449783c5.png)
