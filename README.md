# Invoice from TMetric

This is my little pet project that helps me make invoices for work.
Maybe it will become a plugin for [TMetric], or maybe it will become a separate service.

I did it for my purposes.

### What you need to do to start the project on your own:
 - in the `/conf` folder there are examples of config files that you need to fill in with your data. Please rename it like `config_EN.ini.example` -> `config_EN.ini`

##### Folder `/conf`
Configuration files are stored here, with the help of which you need to specify the invoice parameters. At startup, the script will ask you to select a config file (if you have one only, it will be selected by default). Alse you need to specify the api key to access [TMetric], it can be generated in your [TMetric profile] (I used documentation [TMetric API]).

```sh

[General]
conf_alias: EN # you can name the config file 
invoice_template: Invoice_template_EN.html # you can choose hmlt-template
salary_amount = 1000 # you salary
quantity_in_invoice = 4 # count of line in the invioce
salary_in_cursive: One thousand US Dollars # you salary in the coursive
use_project_description: yes # use additional names for projects, matching by project ID

[TMetric API]
url: https://app.tmetric.com/api/v3 # API url
api_key: 0000000000000000000000000000000000000000000000000000000000000000 # you API-key from [TMetric profile]
authorization: Bearer ${api_key}
accept: text/json

[GeneralForPrint]
unit: Month

[Contractor]
# you details

[Customer]
# customers details

[ContractorBank]
# your bank details
```

##### Folder `/templates`
This directory stores html templates that can be specified in configuration files.

##### Folder `/invoices`
Invoices in pdf format will be saved to this directory

##### File `projects_description.txt`
If you want to use project descriptions (for example, to have names in 2 languages), you need to fill in the file projects_description.txt.
First, rename `projects_description.txt.example` -> `projects_description.txt`
Second, you need to fill the file with descriptions of your projects.
If the project description is not found while the script is running, then the invoice will contain the project ID and its name from the time tracker.

 [TMetric API]: <https://app.tmetric.com/api-docs>
 [TMetric]: <https://tmetric.com>
 [TMetric profile]: <https://app.tmetric.com/#/profile>