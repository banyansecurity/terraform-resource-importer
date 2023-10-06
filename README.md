# Banyan Terraform Import Tool

The Banyan Terraform Import Tool is a command-line utility that allows you to import resources from the Banyan API and generate Terraform configuration files for managing those resources. This tool simplifies the process of managing Banyan resources through Terraform, making it easier to automate your infrastructure setup.

## Prerequisites

Before using this tool, make sure you have the following prerequisites installed on your system:

- Python 3.x
- Terraform (v1.2.5) - [Terraform Installation Guide](https://www.terraform.io/downloads.html)

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
python main.py --api-key <your_api_key> --resource <resource_type> --resource-type <resource_type> --console <console_type> --folder <output_folder> --separate-files <True/False>

--api-key: Your Banyan API key.

--resource: The type of resource you want to import (e.g., "service", "policy", "role").

--resource-type: The specific subtype of the resource you want to import.

--console: The Banyan console to connect to (e.g., "net", "release", "preview").

--folder: (Optional) The output folder where Terraform configuration files will be generated.

--separate-files: (Optional) Specify True if you want to generate separate Terraform files for each resource.
```
The tool will initialize Terraform and generate the necessary configuration files based on the imported resources.
You can then use Terraform to apply or manage the infrastructure as needed.

# Examples
Here are some example commands to use the Banyan Terraform Import Tool:

```bash
# Import services with separate configuration files
python banyan_import_tool.py main --api-key <your_api_key> --resource service --resource-type web --console net --separate-files True

# Import policies with a single configuration file
python banyan_import_tool.py main --api-key <your_api_key> --resource policy --resource-type infra --console release
```


# Support
If you encounter any issues or have questions, please open an issue on the GitHub repository.

