# Microservices Security Scanner

This project is an advanced analysis tool designed to assess the security posture of microservice-based applications. It uses a multi-stage approach combining AI-driven code analysis, human-in-the-loop validation, and statistical modeling to provide security predictions.

The core workflow is as follows:
1.  **AI Analysis**: The tool scans a target microservice project (identified by its `docker-compose.yml`), using a local Large Language Model (LLM) via Ollama to analyze the source code and identify component types, security annotations, and inter-service connections.
2.  **Human Validation**: After the automated scan, a graphical editor opens, allowing the user to review, correct, and augment the AI's findings. This ensures the data is accurate before the final stage.
3.  **Statistical Prediction**: The validated data is used to calculate security metrics. These metrics are then fed into pre-trained logistic regression models (written in R) to predict security scores for various tactics, such as traffic control, authorization, and sensitive data handling.

## Setup and Installation

Follow these steps to set up and run the scanner on your local machine.

### Prerequisites
- Python 3.8+
- R programming language (version 4.0 or higher)
- [Ollama](https://ollama.com/) installed and running.

### Step 1: Clone the Repository
```bash
git clone https://github.com/younes-nb/microservices-security-scanner.git
cd microservices-security-scanner
````

### Step 2: Set up Python Environment

It is highly recommended to use a virtual environment.

```bash
# Create a virtual environment
python -m venv venv

# Activate it
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install the required Python packages
pip install -r requirements.txt
```

### Step 3: Set up Ollama and AI Model

This project requires a local LLM to perform the code analysis.

1.  **Install Ollama**: Follow the instructions on the [official Ollama website](https://ollama.com/).

2.  **Pull the Required Model**: Once Ollama is running, pull the specific model used for this project by running the following command in your terminal:

    ```bash
    ollama run llama3-groq-tool-use
    ```

    This will download the model and make it available for the application.

### Step 4: Set up R Environment

The final prediction stage relies on R and specific statistical packages.

1.  **Install R**: Download and install R from the [official R Project website](https://www.r-project.org/).

2.  **Install R Packages**: Open your R console (either the R GUI or by typing `R` in your terminal) and run the following command to install the necessary libraries:

    ```r
    install.packages(c("rms", "jsonlite"))
    ```

### Step 5: Configure Environment Variables

The application needs to know where to find your R installation.

1.  **Create a `.env` file**: In the root directory of the project, create a new file named `.env`.

2.  **Set the R Path**: Copy the contents from the `.env.template` file into your new `.env` file and update the `RSCRIPT_PATH` to point to the `Rscript.exe` executable on your system.

    ```dotenv
    # Example for Windows:
    RSCRIPT_PATH="C:\Program Files\R\R-4.5.1\bin\Rscript.exe"

    # Example for macOS/Linux (usually in /usr/local/bin/ or similar):
    # RSCRIPT_PATH="/usr/local/bin/Rscript"
    ```

## How to Run

Once all the setup steps are complete, you can run the application from the root directory of the project.

```bash
python main.py
```

This will launch the GUI. From there, you can browse to your target microservice project folder and start the scan.

## Acknowledgements

The statistical models and ground truth data used in the final prediction stage of this project are based on the research and dataset provided in the following academic paper:

  - **Title**: Detection Strategies for Microservice Security Tactics
  - **Authors**: Uwe Zdun, Pierre-Jean Queval, Georg Simhandl, Riccardo Scandariato, Somik Chakravarty, Marjan Jelić, and Aleksandar Jovanović
  - **Publication**: IEEE Transactions on Dependable and Secure Computing, Vol. 21, No. 3, May/June 2024

The methodologies for calculating metrics and the baseline for the R models are derived from this work.

Additionally, this project utilizes the **CodeableModels** library, also developed by the paper's authors, for specifying meta-models and generating model visualizations. The library can be found on GitHub: [https://github.com/uzdun/CodeableModels](https://github.com/uzdun/CodeableModels).
