# Project Interview Guide

A practical preparation sheet for explaining the projects in this repository. Use it to revise the problem, workflow, technical decisions, trade-offs, and limitations before a recruiter or technical interview.

> Be honest about what you implemented yourself, what is a library feature, and what you are still learning. Never invent model scores or business impact. Run the project and use the actual output when discussing results.

## Which projects should I present first?

For Python, Data Analyst, and entry-level AI/ML roles, use this order:

1. **RetailIQ** — strongest combined demonstration of Python, SQL, analytics, data modeling, and a dashboard.
2. **Crypto Market Data Pipeline** — clearest example of API ingestion, validation, persistence, and repeatable ETL.
3. **Book Price Intelligence** — practical web scraping, data cleaning, SQL storage, and business analysis.
4. **Customer Churn Prediction** — useful supervised-learning workflow with model comparison and class imbalance.
5. **VidBrain** — useful applied AI/RAG demonstration.
6. **Market Basket Recommendation System** — demonstrates recommendation approaches and their differences.
7. **Car Price Prediction** — straightforward regression and preprocessing pipeline.
8. **AI Teaching Assistant** — local transcription, embeddings, retrieval, and grounded answers.
9. **Customer Churn Intelligence** — exploratory analysis and a Logistic Regression baseline.
10. **Heart Disease Classification** — classification and deployment demonstration; always explain that it is not a medical tool.

Choose two or three projects that match the job description. Do not try to present all ten in every interview.

---

## 1. RetailIQ — Retail Analytics Platform

**Problem:** A retail business needs to understand sales, customers, products, and operational performance from relational data.

**How to explain the workflow:**
1. Create a relational SQLite database with customers, products, employees, orders, and order items.
2. Generate synthetic records so the project can be run and demonstrated without private business data.
3. Use SQL joins, filtering, aggregation, and business queries to answer questions.
4. Display KPIs and trends in Streamlit.
5. Segment customers using Recency, Frequency, and Monetary value, then apply KMeans.
6. For natural-language questions, match against a predefined SQL library first; an optional LLM fallback can generate SQL, which is validated and executed read-only.

**Technical concepts to revise:** primary and foreign keys, joins, GROUP BY, CTEs, aggregation, RFM, feature scaling, KMeans, TF-IDF, cosine similarity, SQL injection, read-only database access.

**Likely interview questions:**
- Why did you use a relational database?
- Explain one SQL query that produces a business insight.
- What are Recency, Frequency, and Monetary value?
- Why do you scale features before KMeans?
- Why use predefined SQL before LLM-generated SQL?
- How do you prevent generated SQL from changing the database?

**Honest limitation:** The dataset is synthetic. The natural-language SQL feature is a demonstration and should be evaluated carefully before use with real company data.

**Demo:** Open the dashboard, show one business KPI, run one saved SQL question, and show the RFM customer segments.

## 2. Crypto Market Data Pipeline

**Problem:** Market data is available through an external API, but it needs to be collected, validated, stored, and summarized consistently.

**Workflow:**
1. Request market data from the CoinGecko endpoint.
2. Handle timeouts, retries, and unsuccessful responses.
3. Validate and transform fields using Pandas.
4. Append timestamped snapshots to SQLite using parameterized SQL.
5. Write a CSV backup safely using a temporary file and atomic replacement.
6. Analyze the latest stored snapshot to report gainers, losers, and average 24-hour movement.

**Technical concepts:** REST API, HTTP status codes, timeout, retry, JSON, DataFrame validation, parameterized queries, SQLite transactions, timestamps, idempotency, atomic file replacement.

**Likely questions:**
- What is ETL? Identify extract, transform, and load in this project.
- Why do you set an HTTP timeout?
- Why store snapshots instead of overwriting the latest values?
- What is the benefit of parameterized SQL?
- What happens if the API is unavailable?
- Why is the market summary not an investment recommendation?

**Honest limitation:** Historical snapshots exist only from the times the pipeline is run. The sentiment summary is a simple descriptive statistic, not a forecasting or trading model.

**Demo:** Run the pipeline, inspect the SQLite snapshot table, then run the analyzer.

## 3. Book Price Intelligence

**Problem:** A product catalog must be collected from web pages, cleaned, stored, and analyzed to understand prices, ratings, and stock availability.

**Workflow:**
1. Fetch catalog pages using HTTP requests.
2. Parse HTML with BeautifulSoup.
3. Convert extracted values into structured records.
4. Validate titles, prices, ratings, and stock status with Pandas.
5. Store valid catalog records in SQLite.
6. Run analysis for price distribution, stock, ratings, and price-rating relationship.

**Technical concepts:** HTTP requests, HTML parsing, CSS selectors, pagination, missing values, type conversion, data validation, duplicate prevention, SQL constraints, correlation.

**Likely questions:**
- What is the difference between scraping and using an API?
- How do you handle a changed page or missing field?
- Why validate data before inserting it?
- How do you avoid duplicate records?
- Does correlation mean price causes a higher rating?

**Honest limitation:** Books to Scrape is a practice website. A real production scraper must respect the site's terms, robots policy, request limits, and changes to page structure.

**Demo:** Run scraper, cleaner, and analysis in order; show raw versus cleaned records and one generated insight.

## 4. Customer Churn Prediction

**Problem:** A subscription business wants to identify customers who may leave so that it can investigate retention opportunities.

**Workflow:**
1. Inspect training and separate test datasets.
2. Explore missing values, target distribution, and churn patterns.
3. Separate identifiers from model features.
4. Split the training data with stratification.
5. Build preprocessing pipelines for numeric and categorical columns.
6. Compare Logistic Regression, Decision Tree, and Random Forest.
7. Use class weights to address imbalance without artificially changing the holdout distribution.
8. Compare precision, recall, and F1; save the best holdout-F1 pipeline.

**Technical concepts:** binary classification, train/test split, stratification, data leakage, imputation, scaling, one-hot encoding, class imbalance, precision, recall, F1, confusion matrix, Random Forest.

**Likely questions:**
- Why is accuracy not enough for imbalanced churn data?
- What is data leakage?
- Why put preprocessing inside a Pipeline?
- What does stratification preserve?
- Why might recall matter to a retention team?
- Why keep the separate test CSV out of model selection?

**Honest limitation:** Predictions indicate patterns in the provided dataset. They do not prove why a customer leaves. Check the actual holdout and separate-test metrics before quoting performance.

**Demo:** Show target imbalance, explain the pipeline, then show the classification report and confusion matrix.

## 5. VidBrain — YouTube Transcript Assistant

**Problem:** A learner wants to ask questions about a video without manually searching its transcript.

**Workflow:**
1. Extract the YouTube video transcript.
2. Split it into smaller text chunks.
3. Generate vector embeddings using a Hugging Face embedding model.
4. Store and search vectors with FAISS.
5. Retrieve relevant transcript chunks for the user's question.
6. Pass the retrieved context to the Groq language model and ask it to answer using that evidence.

**Technical concepts:** RAG, chunking, embeddings, vector similarity, FAISS, retrieval, prompt grounding, context window, hallucination, API keys.

**Likely questions:**
- What is RAG and why use it?
- What is an embedding?
- Why split text into chunks?
- What does FAISS do?
- What happens if the answer is not in the transcript?
- How would you improve retrieval quality?

**Honest limitation:** The quality depends on transcript availability, chunking, retrieval, and the language model. Retrieved context can still be incomplete, and answers should be checked against the source video.

**Demo:** Load a video, ask a question answered in the transcript, then ask one outside the video content.

## 6. Market Basket & Product Recommendation System

**Problem:** Retailers want to understand which products are bought together and suggest relevant products to customers.

**Workflow:**
1. Load customer transaction baskets from CSV.
2. Calculate product co-occurrence and association-rule measures.
3. Use support, confidence, and lift to evaluate product associations.
4. Build a user-item matrix and calculate user similarity for collaborative filtering.
5. Use purchase transitions to suggest likely next items.
6. Show recommendations and summaries in a Flask dashboard.

**Technical concepts:** market basket analysis, support, confidence, lift, association rules, user-item matrix, cosine similarity, collaborative filtering, cold start, Markov transition.

**Likely questions:**
- Explain support, confidence, and lift.
- Why is lift above 1 useful?
- What is collaborative filtering?
- How do you handle a new user with no purchase history?
- How is a next-item transition different from a trained LSTM?
- What happens when transaction data is sparse?

**Honest limitation:** The default next-item model is a simple sequence/transition approach. The optional LSTM is experimental. Recommendations depend heavily on transaction quality and volume.

**Demo:** Upload or use the sample CSV, show a product association and a customer recommendation.

## 7. Ford Car Price Prediction

**Problem:** Estimate used Ford car prices from vehicle specifications.

**Workflow:**
1. Inspect the dataset and validate target and feature columns.
2. Split into training and holdout data.
3. Impute and scale numeric features.
4. Impute and one-hot encode categorical features.
5. Fit Linear Regression in a Scikit-learn Pipeline.
6. Evaluate MAE, RMSE, R², and adjusted R².
7. Save the fitted preprocessing and model pipeline.

**Technical concepts:** regression, categorical encoding, imputation, scaling, pipeline, MAE, RMSE, R², adjusted R², overfitting.

**Likely questions:**
- Why use regression rather than classification?
- What does MAE mean in price units?
- Why can RMSE be larger than MAE?
- Why use one-hot encoding?
- Why fit preprocessing only on training data?
- What other features could improve valuation?

**Honest limitation:** This is a baseline Linear Regression model for Ford listings. Condition, accident history, service history, location, and market timing are not fully represented.

**Demo:** Run `python train.py`, explain the pipeline, and interpret the metrics actually printed.

## 8. AI Teaching Assistant

**Problem:** Students need to search course videos and receive answers with source timestamps.

**Workflow:**
1. Convert course videos to audio using FFmpeg.
2. Transcribe audio into timestamped chunks using Whisper.
3. Generate embeddings for transcript chunks with Ollama's bge-m3 model.
4. Embed the student query and retrieve similar chunks.
5. Give retrieved transcript context to the local llama3.2 model.
6. Return an answer with video and timestamp references.

**Technical concepts:** speech-to-text, Whisper, embeddings, semantic search, vector retrieval, cosine similarity, local LLM, grounding, hallucination.

**Likely questions:**
- Why do you need transcription before RAG?
- What is the difference between keyword search and semantic search?
- Why must the query and documents use the same embedding model?
- Why run Ollama locally?
- How do timestamps help a student verify an answer?
- What happens when the transcript index is missing?

**Honest limitation:** Whisper transcription quality depends on audio clarity and language. Local model speed depends on available hardware. The index must be rebuilt when transcript content or embedding model changes.

**Demo:** Run the pipeline on one short course video and ask a question whose answer has a clear timestamp.

## 9. Customer Churn Intelligence

**Problem:** Understand which telecom customer attributes are associated with churn and build an interpretable baseline classifier.

**Workflow:**
1. Inspect customer, billing, service, and target fields.
2. Convert TotalCharges to numeric and handle blanks.
3. Explore churn by contract, tenure, and monthly charges.
4. Remove customerID from model features.
5. Use a stratified split and a preprocessing pipeline.
6. Train Logistic Regression and evaluate accuracy, precision, recall, F1, and confusion matrix.

**Technical concepts:** EDA, data cleaning, target encoding, stratification, one-hot encoding, imputation, Logistic Regression, classification metrics.

**Likely questions:**
- What patterns did you explore in EDA?
- Why is customerID excluded?
- Why use Logistic Regression as a baseline?
- What does the confusion matrix tell you?
- Why should you not claim correlation is causation?

**Honest limitation:** This is a notebook-based baseline, not a deployed churn service. Findings are associations in the provided dataset.

**Demo:** Show the churn distribution, one EDA comparison, and the model evaluation.

## 10. Heart Disease Classification

**Problem:** Demonstrate a machine-learning classification workflow on a public tabular dataset.

**Workflow:**
1. Validate the required columns and binary target.
2. Treat specified zero measurements as missing where appropriate.
3. Split data using stratification.
4. Impute, scale, and encode inside a Scikit-learn pipeline.
5. Train a class-weighted Logistic Regression baseline.
6. Evaluate with accuracy, F1, ROC-AUC, and a classification report.
7. Use the saved pipeline in a Streamlit demonstration.

**Technical concepts:** binary classification, missing-value handling, stratification, class weights, one-hot encoding, ROC-AUC, F1, model serialization.

**Likely questions:**
- Why treat some zero measurements as missing?
- What does ROC-AUC measure?
- Why use class weights?
- Why save the entire pipeline instead of only the estimator?
- What additional validation is required before clinical use?

**Critical limitation:** This is not clinically validated and must not be used for diagnosis, screening, treatment, or personal health decisions.

**Demo:** Explain the training pipeline and show the Streamlit interface only as an educational demonstration.

---

## A simple 60-second project explanation

Use this structure. Replace the brackets with details from the project you are actually demonstrating.

> "I built **[project name]** to solve **[specific problem]**. The input is **[dataset/API/user input]**. I used **[main tools]** to clean or process the data, then **[analysis/model/retrieval method]** to produce **[output or insight]**. One important technical decision was **[decision]**, because **[reason]**. I tested **[important behavior]** and documented the setup. The current limitation is **[honest limitation]**, and my next improvement would be **[realistic next step]**."

## Before an interview: practical checklist

- [ ] Run the project from a fresh terminal using the README commands.
- [ ] Know where the input data comes from and whether it is synthetic or public.
- [ ] Explain the flow from input to output without reading code.
- [ ] Understand every library and model named on your resume.
- [ ] Be ready to explain one bug you fixed and how you verified the fix.
- [ ] Know the actual test command and latest CI result.
- [ ] Quote metrics only after running the project yourself.
- [ ] Explain one limitation and one sensible next improvement.
- [ ] Never claim production readiness, real business impact, or clinical accuracy without evidence.

## Core revision topics

For these projects, prioritize:
- **Python:** functions, modules, exceptions, file handling, virtual environments, logging, testing.
- **SQL:** joins, GROUP BY, HAVING, subqueries, CTEs, window functions, keys, indexes, transactions.
- **Pandas:** missing values, type conversion, filtering, groupby, merge, duplicates, datetime handling.
- **ML:** train/test split, leakage, preprocessing, class imbalance, classification/regression metrics, pipelines.
- **APIs and ETL:** HTTP methods, status codes, JSON, timeouts, retries, validation, persistence.
- **RAG:** chunking, embeddings, vector search, retrieval quality, grounding, hallucinations.

