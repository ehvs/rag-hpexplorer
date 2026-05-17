> Always remember there is no PERFECT solution in Technology. We always want the best precision, but errors are always expected at some point.

# RAG (Retrieval Augmented Generation)

## Why to use it?

Although LLM are great and trained over billion of parameters, they are generic and can suffer of hallucination. When having a specific use case, you want to use specific datasources to have more precise answers. Per example, product documentation for customer support. 

Methods like Fine-tuning and RAG provides better answers but can make the solution a bit more complex.

### Alternative, Fine-tuning?

It is to refine the weights with an extra dataset. This is made to customize the LLM, giving specific/specialized information.
You want to do it whenever Prompt engineering is not enough.

- Problems: 
    - You need to retrain the model (extra work/added complexity/slow task [long hours]). Not everything tho, just a few "weights".
    - There is no guarantee of viability
    - Overfitting risks (learning too much - whenever the model learn the details of the training)
    - It can make the model more specific, losing versatility.

> Curiosity: There are training in OpenAI that takes 90 days to be trained.

#### A brief note about training Weights

### Better alternative: RAG

Using RAG with Generative AI, helps reduces hallucinations and does not need to retrain LLM.

- How it does that?
It combines LLM with an external information retrieval mechanism, allowing the model to access the relevant data (like a vector database)  in the moment of text generation, instead of depending only of the knowledge stored in the parameters.

It works as giving a **live memory system**, which is consulted before answering.

## RAG Pipeline

The question -> question turns into a vector -> vector store is searched and finds similarities (top-k retrieved) -> Build the augmented prompt.

### Why AUGMENTED?
Because RAG augments/increases/make it larger the prompt with external content before sending to the model.
So the model receives an enriched version of the original query.

 
# Naive RAG

Structured/unstructured Data -> Split into Chunks -> Stored in a Vector DB (embedding) -> Retrieved Chunks -> (LLM reads everything) -> Response Generation

- Embeddings = Numerical Representation

# CAG
# KAG
# Adaptative RAG
# Corrective RAG (CRAG)

