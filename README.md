[!Warning]
Warning: Please contact your Banyan Customer Success representative, before running this script in your environment. The script may cause changes to your environment and we advise you to reach out to us to guide you through it. You may still decide to use it but that might change the configuration and cause unintended consequences.

# Banyan Terraform Import Tool

The Banyan Terraform Import Tool is a command-line utility that allows you to import resources from the Banyan API and generate Terraform configuration files for managing those resources. This tool simplifies the process of managing Banyan resources through Terraform, making it easier to automate your infrastructure setup.

## Prerequisites

Before using this tool, make sure you have the following prerequisites installed on your system:

- Python 3.x
- Terraform (>=v1.5.x) - [Terraform Installation Guide](https://www.terraform.io/downloads.html)
- Banyan Terraform Provider (>=v1.2.5)

## Installation

1. Clone this repository to your local machine:

    git clone https://github.com/banyansecurity/terraform-resource-importer.git

2. Navigate to the project directory:

    cd terraform-resource-importer

3. Install the required Python packages using `pip`:

    pip install -r requirements.txt


## Usage

To use the Banyan Terraform Import Tool, follow these steps:

1. Open a terminal window and navigate to the project directory.

2. Run the tool using the following command:

```bash
USAGE:
 python main.py --help
Usage: main.py [OPTIONS] API_KEY

Arguments:
  API_KEY  [required]

Options:
  --resource [service|policy|role|all]
                                  resource to be imported  [required]
  --resource-type [all|web|db|k8s|rdp|ssh|tcp|infra|tunnel]
                                  Type of selected resource to be imported,
                                  for --resource service options are [all,
                                  web, db, k8s, rdp, ssh, tcp] for --resource
                                  policy options are [all, web, infra, tunnel]
                                  for --resource role need not set this option
                                  or can provide value [all]   [required]
  --console [net|preview|release]
                                  [default: net]
  --folder TEXT
  --module / --no-module          [default: no-module]
  --install-completion [bash|zsh|fish|powershell|pwsh]
                                  Install completion for the specified shell.
  --show-completion [bash|zsh|fish|powershell|pwsh]
                                  Show completion for the specified shell, to
                                  copy it or customize the installation.
  --help                          Show this message and exit.
  ```
The tool will initialize Terraform and generate the necessary configuration files based on the imported resources.
You can then use Terraform to apply or manage the infrastructure as needed.

Please Note:
Once you import your Banyan resources into Terraform, you may now use the import.tf file, in addition to the generated.tf or separated Terraform code files, in your Terraform code. 
Please ensure your code utilizes the Banyan Terraform provider 1.2.5 or above versions.

```bash
terraform init

##The command ‘terraform plan’ should display the number of resources being imported, and NOT the number of added or updated or removed.

terraform plan 
terraform apply
```

# Examples
Here are some example commands to use the Banyan Terraform Import Tool:

```bash

# Import all policies 
python main.py <banyan_api_key> --resource policy --resource-type all --folder mypolicies
# Import all resources
python main.py <banyan_api_key> --resource all --folder allresources 
# Import certain services
python main.py <banyan_api_key> --resource service --resource-type web --folder mywebservices 

```


# Support
If you encounter any issues or have questions, please open an issue on the GitHub repository.

