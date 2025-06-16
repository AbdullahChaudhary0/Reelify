Project Title
Reelify: Social Media Trend Analysis and Video Content Generation

Overview
Reelify is an innovative system designed for trend analysis and automated content generation. The project leverages AI to create user-friendly, bilingual videos from social media trends with an emphasis on scalability and user-centric functionality.

Current Status
Module 1: Social Media Trend Analysis ✅
Extracted real-time social media trends from platforms such as X (formerly Twitter) and Instagram.

Integrated Gemini API to generate concise one-liner descriptions for each trend.

Completed scraping and evaluation of trends.

Module 2: Bilingual Content Generation 

Translation system implemented using the facebook model for English to Urdu conversion.

Transformer-based architecture being utilized for translation.

General Updates
Integrated modules are modular and follow API connectivity principles for easy scalability.

Preliminary tests of trend scraping and API integration have been successful.

Dependencies
Transformers Library: Used for NLLB-based translation.

Gemini API: Trend summarization and description.

TensorFlow/PyTorch: For underlying AI model functionality.

How to Run
Install dependencies:


pip install -r requirements.txt
Run the social media trend extraction module:


python app.py
Translate text with the bilingual content generator:

