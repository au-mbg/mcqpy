# MCQPy Web Interface

A Streamlit-based web interface for MCQPy functionality, providing an intuitive way to grade PDFs, analyze results, and manage quizzes.

## Features

### Current Features
- **🎯 Quiz Generation**: Generate quizzes from local or remote sources
- **🌐 Remote Loading**: Load quiz configurations from GitHub or zip archives
- **📄 PDF Grading**: Upload student answer PDFs for automatic grading
- **📊 Results Analysis**: View detailed grading results and statistics
- **💾 Export Options**: Download results as CSV or Excel files
- **🔄 Batch Processing**: Grade multiple submissions simultaneously
- **📈 Question Analysis**: Detailed breakdown of question performance

### Coming Soon
- **🎮 Interactive Quizzes**: Host live quiz sessions
- **❓ Question Builder**: Create and edit questions with preview
- **� Private Repos**: Authentication for private GitHub repositories
- **�📱 Mobile-Friendly**: Responsive design for mobile devices
- **🔐 User Authentication**: Secure access controls

## Installation & Setup

The web interface is included with the main MCQPy package. Make sure you have installed MCQPy with all dependencies:

```bash
pip install -e .
```

## Usage

### Starting the Web Interface

You can launch the web interface in several ways:

1. **Using the command line entry point:**
```bash
mcqpy-web
```

2. **Direct Streamlit command:**
```bash
streamlit run src/mcqpy/web/app.py
```

3. **From Python:**
```python
from mcqpy.web.launcher import main
main()
```

### Generating Quizzes

#### From Remote Sources
1. **Navigate to "Generate Quiz" page**
2. **Switch to "Remote Source" tab**
3. **Enter a GitHub directory URL** (e.g., `https://github.com/user/repo/tree/main/test_quiz`)
4. **Click "Load Quiz"** to fetch the configuration and questions
5. **Configure quiz options** (number of questions, randomization, etc.)
6. **Click "Generate Quiz"** to create the quiz files

#### From Local Files
1. **Navigate to "Generate Quiz" page**
2. **Stay on "Local Files" tab**
3. **Upload your config.yaml and question YAML files**
4. **Configure quiz options** and generate

### Grading PDFs

1. **Navigate to "Grade PDF" page**
2. **Upload your quiz manifest** (JSON file generated when creating the quiz)
3. **Upload student answer PDFs** (one or multiple files)
4. **Click "Grade All PDFs"** to process the submissions
5. **View results** with detailed breakdowns and statistics
6. **Download** results as CSV or Excel files

### Understanding Results

The grading interface provides:
- **Summary Statistics**: Overview of class performance
- **Individual Results**: Detailed breakdown per student
- **Question Analysis**: Performance statistics for each question
- **Score Distribution**: Visual representation of grade distribution

## Architecture

The web interface follows a modular architecture:

```
src/mcqpy/web/
├── app.py                 # Main Streamlit entry point
├── config.py              # Configuration management
├── launcher.py            # CLI launcher script
├── components/            # Reusable UI components
│   ├── file_upload.py     # File upload handling
│   └── grading_display.py # Results visualization
├── pages/                 # Individual page modules
│   ├── home.py           # Landing page
│   └── grade_pdf.py      # PDF grading interface
├── utils/                 # Utility functions
│   ├── session_state.py  # Session management
│   └── validators.py     # Input validation
└── static/               # Static assets
    └── style.css         # Custom CSS styles
```

## Extending the Interface

### Adding New Pages

1. Create a new module in `pages/`:
```python
# pages/new_feature.py
import streamlit as st

def show():
    st.title("New Feature")
    st.write("Implementation here...")
```

2. Add to navigation in `app.py`:
```python
pages = {
    "🏠 Home": home,
    "📄 Grade PDF": grade_pdf,
    "🆕 New Feature": new_feature,  # Add here
}
```

### Creating Components

Create reusable components in `components/`:
```python
# components/my_component.py
import streamlit as st

class MyComponent:
    def show(self, data):
        # Component implementation
        pass
```

### Configuration

Web-specific settings are managed in `config.py`:
```python
class WebConfig:
    def __init__(self):
        self.max_file_size_mb = 10
        self.allowed_file_types = ['.pdf']
        # Add new settings here
```

## Integration with MCQPy Core

The web interface seamlessly integrates with MCQPy's core functionality:

- **Grading**: Uses `mcqpy.grade.MCQGrader` for PDF processing
- **Manifests**: Works with `mcqpy.create.manifest.Manifest` objects
- **Analysis**: Leverages `mcqpy.grade.analysis` for statistics
- **Question Bank**: Can access `mcqpy.question.QuestionBank` for question management

## Development Guidelines

### Code Style
- Follow existing patterns in the codebase
- Use type hints where appropriate
- Document functions and classes
- Keep components focused and reusable

### Error Handling
- Validate user inputs thoroughly
- Provide clear error messages
- Handle edge cases gracefully
- Use try/except blocks for external operations

### Session State
- Use `SessionStateManager` for consistent session handling
- Clear session state when appropriate
- Store only necessary data in session

### File Handling
- Always use temporary files for uploads
- Clean up temporary files after processing
- Validate file types and sizes
- Handle file encoding issues

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure MCQPy is properly installed with all dependencies
2. **File Upload Issues**: Check file size limits and formats
3. **Grading Errors**: Ensure manifest file matches the PDF structure
4. **Performance Issues**: Consider file sizes and number of concurrent users

### Debugging

Enable debug mode by setting:
```python
st.set_option('server.enableXsrfProtection', False)
```

Check browser console for JavaScript errors and Streamlit logs for Python exceptions.

## Contributing

When contributing to the web interface:

1. **Test thoroughly** with various file types and sizes
2. **Consider mobile users** when designing layouts
3. **Follow accessibility guidelines**
4. **Update documentation** for new features
5. **Add appropriate error handling**

## Future Enhancements

Planned improvements include:
- Real-time collaborative features
- Advanced analytics and reporting
- Integration with Learning Management Systems
- API endpoints for external integration
- Improved mobile experience
- Multi-language support