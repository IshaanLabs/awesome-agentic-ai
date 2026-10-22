## Project Title and Description

**SlideForge: Open-source AI-powered PowerPoint Presentation Generator**

SlideForge is an open-source application that utilizes Generative AI and Large Language Models (LLMs) to automatically generate engaging PowerPoint presentations. It empowers users to create professional-looking presentations with ease, saving time and effort.

## Tech Stack

* Python
* Langchain
* Ctransformers
* Streamlit

## Project Structure

* **main.py:** Main application file where the user interface and presentation generation logic reside.
* **utils.py:** Utility functions for generating slide titles and content.
* **config.py:** Configuration file for environment variables and model paths.

## Installation

1. Clone the repository: `git clone https://github.com/Ginga1402/Generate_PPT_using_llama2.git`
2. Install the required dependencies: `pip install -r requirements.txt`
3. Set the environment variables in `config.py`: `local_llm = r'path to your file\llama-2-7b-chat.Q4_K_M.gguf'`

## Usage

1. Run the application: `python main.py`
2. Enter the topic for your presentation in the text input field.
3. Click the "Generate Presentation" button.
4. The application will generate a presentation based on the topic and display a download link.

## Configuration

The application requires the following environment variables to be set in `config.py`:

* `local_llm`: Path to the local LLM model file.

## Disclaimer

The software is provided "as is" without warranty of any kind. In no event shall the authors or copyright holders be liable for any claim, damages, or other liability arising from or in connection with the software or the use or other dealings in the software.

## License

The software is licensed under the MIT License.