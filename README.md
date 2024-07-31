# Translation app that is better than Goolgle translate.

## Concept of this repo

The app is created with Streamlit and takes [reflection workflow](https://github.com/andrewyng/translation-agent/tree/e0fc605acbb5d78cb7a58a98bc8bd8f0056df49c) into practice, which is proposed by Andrew Ng.

The main idea is that there are three layers of the model.

**Translation, refleciton, and the improvement.**

#### a. Translation

Take in the orginial text and generate the translated content.

#### b. Reflection

Based on the original text and the translated content, generate the comment that can make the model improve its performance. This model will be different from the first and third one and will be viewed as the reviewer.

#### c. Improvement

Accroding to translated pair and the comment, this model make the improvement of its performance.

## To run the code, you must

### 1. Install the modules

```
pip install python-dotenv streamlit
```

### 2. Create a file ".env"

Modify ".env.example file and input you API key.
The model in app.py I use now is **taide-llama2-70b**.
