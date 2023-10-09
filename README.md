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
  --resource String                 [default: service]
  --resource-type String
  --console String                  [default: net]
  --folder String
  --separate-files / --no-separate-files
                                  [default: no-separate-files]
  --install-completion [bash|zsh|fish|powershell|pwsh]
                                  Install completion for the specified shell.
  --show-completion [bash|zsh|fish|powershell|pwsh]
                                  Show completion for the specified shell, to
                                  copy it or customize the installation.
  --help                          Show this message and exit.
  ```
The tool will initialize Terraform and generate the necessary configuration files based on the imported resources.
You can then use Terraform to apply or manage the infrastructure as needed.

# Examples
Here are some example commands to use the Banyan Terraform Import Tool:

```bash
# Import services with separate configuration files
python main.py --api-key <banyan_api_key> --resource service --resource-type web --console net --separate-files

# Import policies with a single configuration file
python main.py --api-key <banyan_api_key> --resource policy --resource-type infra --console release
```


# Support
If you encounter any issues or have questions, please open an issue on the GitHub repository.

