from fastapi import FastAPI
from api import file_manager,article_retriever,get_metadata, Image_extractor,table_extractor,combined_extractor,common_word_analysis,pdf_filter,term_extractor

app = FastAPI()
#file manager
app.include_router(file_manager.router,prefix="/downloads",tags=["file"])
#term extreactor
app.include_router(term_extractor.router,prefix="/extract-terms",tags=["Term-Extractor"])
# Article Retrieval Module
app.include_router(article_retriever.router, prefix="/articles", tags=["Article Retriver"])
# get meta data 
app.include_router(get_metadata.router,prefix="/extract-metadata",tags=["Get Details of pdf files "])
#common word analysis module
app.include_router(common_word_analysis.router,prefix="/common-word-analysis",tags=["Common Word Analysis"])
# Recent Searches Module
app.include_router(combined_extractor.router,prefix="/extract-all",tags=["Combined Extractor"])
#table extractor module
app.include_router(table_extractor.router,prefix="/tables",tags=["Table Extractor"])

# Image Extraction Module
app.include_router(Image_extractor.router, prefix="/images", tags=["PDF Image Extractor"])
#csv  file manger Module
# app.include_router(csv_manager.router, prefix="/csv-manager", tags=["CSV Manager"])
#filter pdf 
app.include_router(pdf_filter.router,prefix="/filter-pdf",tags=["PDF Filter"])

@app.get("/")
def root():
    return {"message": "Welcome to VBP FastAPI Backend"}
