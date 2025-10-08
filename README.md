# 🌿 Future Agent

Cannabis Industry Knowledge Agent powered by Future4200 forum data and RAG technology.

## 🚀 Features

- **F8 vs Community Comparison**: Side-by-side analysis of F8 LangChain responses vs Future4200 forum discussions
- **Question Extraction**: 16,337+ questions extracted from 7,061 forum threads
- **Interactive Interface**: Filter by category, confidence, and search functionality
- **Data Versioning**: All data files managed with DVC (Data Version Control)

## 📊 Data Overview

- **Total Questions**: 16,337 extracted from Future4200 forum
- **Total Threads**: 7,061 scraped from Future4200.com
- **Data Size**: 430MB+ of forum data stored in S3
- **Categories**: Extraction, Cultivation, Business, Equipment, Genetics
- **Sources**: Future4200.com community discussions
- **Processing**: F8 LangChain integration with confidence scoring
- **Storage**: AWS S3 via DVC for efficient data versioning

## 🛠️ Setup

### Prerequisites
- Python 3.8+
- DVC (Data Version Control)
- Git
- AWS CLI configured (for S3 access)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/dcmcshan/future-agent.git
   cd future-agent
   ```

2. **Install DVC:**
   ```bash
   pip install dvc
   ```

3. **Configure DVC remote (if not already set):**
   ```bash
   dvc remote add -d s3 s3://future-agent-dvc-data
   ```

4. **Pull data files from S3:**
   ```bash
   dvc pull
   ```

5. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Demo

1. **Generate F8 responses:**
   ```bash
   python demo_f8_processing.py
   ```

2. **Process all questions (if you have F8 API access):**
   ```bash
   python ask_f8_all_questions.py
   ```

## 🌐 GitHub Pages

The site is automatically deployed to GitHub Pages:

- **Live Site**: `https://dcmcshan.github.io/future-agent/`
- **F8 Comparison**: `https://dcmcshan.github.io/future-agent/f8-comparison.html`

## 📁 Data Management

This repository uses DVC for data version control:

- **Data files** are tracked by DVC, not Git
- **DVC files** (`.dvc` files) are tracked by Git
- **Large datasets** are stored in DVC remote storage

### DVC Commands

```bash
# Pull data files
dvc pull

# Push data changes
dvc push

# Add new data files
dvc add data/new_file.json

# Check data status
dvc status
```

## 🔧 Development

### Project Structure

```
future-agent/
├── docs/                    # GitHub Pages site
│   ├── f8-comparison.html   # Main comparison interface
│   ├── index.html          # Landing page
│   └── data/               # Web-accessible data files
├── data/                   # DVC-tracked data files (stored in S3)
│   ├── comprehensive_scraping_results.json  # 425MB - all forum threads
│   ├── extracted_questions.json            # 5MB - 16,337 questions
│   ├── f8_responses_demo.json
│   ├── f8_processing_stats.json
│   └── sample_questions_for_f8.json
├── demo_f8_processing.py   # Demo F8 processing script
├── ask_f8_all_questions.py # Full F8 processing script
└── .github/workflows/      # GitHub Actions for deployment
```

### Adding New Data

1. **Add to DVC:**
   ```bash
   dvc add data/new_file.json
   ```

2. **Commit changes:**
   ```bash
   git add data/new_file.json.dvc
   git commit -m "Add new data file"
   ```

3. **Push to remote:**
   ```bash
   dvc push
   git push origin main
   ```

## 📈 Statistics

- **Questions by Category:**
  - General: 12,525
  - Extraction: 1,456
  - Business: 663
  - Equipment: 600
  - Cultivation: 581
  - Genetics: 330
  - Processing: 182

- **F8 Response Quality:**
  - Average Confidence: 0.817
  - Processing Time: ~2.3s per question
  - Success Rate: 100% (demo data)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add/update data with DVC
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Links

- **Repository**: https://github.com/dcmcshan/future-agent
- **Live Site**: https://dcmcshan.github.io/future-agent/
- **Future4200 Forum**: https://future4200.com/