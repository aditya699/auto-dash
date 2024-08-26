# AUTO-DASH: Your Personal Dashboard Wizard 🚀

AUTO-DASH is an open-source tool that generates interactive dashboards on the fly using your CSV data. It leverages the power of AI to create custom Dash code, allowing you to visualize and analyze your data in seconds instead of days.

## Features

- 📊 Automatic dashboard generation from CSV files
- 🧹 Built-in data cleaning and validation
- 🔮 Optional feature engineering
- 🎨 AI-powered dashboard code creation
- 🔄 Interactive, interconnected charts
- 🔍 Customizable filters with select-all feature
- 🔄 Reset filters functionality

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/AUTO-DASH.git
   cd AUTO-DASH
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up your environment variables:
   - Create a `.env` file in the root directory
   - Add your Anthropic API key: `ANTHROPIC_API_KEY=your_api_key_here`

## Usage

1. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

2. Open your web browser and go to `http://localhost:8501`

3. Upload your CSV file using the file uploader

4. Follow the on-screen instructions to generate your dashboard

5. Download the generated Python script (`gendb.py`)

6. Run the generated dashboard:
   ```
   python gendb.py
   ```

7. Open your web browser and go to `http://127.0.0.1:8050` to view your dashboard

## Project Structure

- `app.py`: Main Streamlit application
- `src/`: Source code directory
  - `data_loader.py`: Functions for loading and cleaning data
  - `feature_eng.py`: Feature engineering module
  - `prompt_builder.py`: AI prompt generation for dashboard creation
- `Generated_Dashboards/`: Directory for storing generated dashboard files
- `Staging_Data/`: Temporary directory for data processing

## Contributing and Customizing for Your Organization

We encourage contributions and customizations to make AUTO-DASH fit your organization's needs. Here are some ways you can contribute and adapt the tool:

### Contributing to the Core Project

1. **Report Issues**: If you encounter any bugs or have feature suggestions, please open an issue on our GitHub repository.

2. **Submit Pull Requests**: Feel free to fork the repository and submit pull requests for bug fixes or new features.

3. **Improve Documentation**: Help us make the documentation more comprehensive and user-friendly.

4. **Enhance AI Prompts**: Contribute to improving the AI prompts used for dashboard generation to create even better visualizations.

### Customizing for Your Organization

1. **Custom Data Loaders**: 
   - Extend the `src/data_loader.py` module to support your organization's specific data formats or sources.
   - Example: Add support for connecting to your company's databases or APIs.

2. **Domain-Specific Feature Engineering**:
   - Modify `src/feature_eng.py` to include feature engineering techniques relevant to your industry or data types.
   - Example: Add time-series specific feature generation for financial data.

3. **Tailored Dashboard Themes**:
   - Customize the dashboard generation process in `src/prompt_builder.py` to incorporate your organization's branding and design guidelines.
   - Example: Include company logos, color schemes, or specific chart types preferred by your organization.

4. **Integration with Internal Tools**:
   - Extend AUTO-DASH to integrate with your organization's existing data pipelines or reporting tools.
   - Example: Add functionality to automatically upload generated dashboards to an internal server or collaborate with other team members.

5. **Custom Metrics and KPIs**:
   - Modify the dashboard generation process to automatically include key metrics and KPIs specific to your organization.
   - Example: Add calculation and display of industry-specific performance indicators.

6. **Security and Compliance**:
   - Implement additional security measures or compliance checks that align with your organization's policies.
   - Example: Add data anonymization features or audit logging for sensitive information.

### Steps for Customization

1. Fork the AUTO-DASH repository to your organization's GitHub account.
2. Clone your forked repository and create a new branch for your customizations.
3. Make the desired changes, focusing on modular additions that don't break core functionality.
4. Test your changes thoroughly to ensure they work with various data types and scenarios.
5. Document your customizations, including any new dependencies or setup steps.
6. If your changes could benefit the broader community, consider submitting a pull request to the main AUTO-DASH repository.

By contributing to and customizing AUTO-DASH, you can create a powerful, tailored dashboard solution that meets your organization's specific needs while benefiting from ongoing community improvements.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Streamlit](https://streamlit.io/) for the interactive web app framework
- [Dash](https://dash.plotly.com/) for the dashboard creation
- [Anthropic](https://www.anthropic.com/) for the AI-powered code generation

## Contact

If you have any questions or suggestions, please open an issue or contact the project maintainers.


## Live Demo
[Live Demo](https://www.linkedin.com/feed/update/urn:li:activity:7232349693526089728/)


Happy dashboarding! 🎉