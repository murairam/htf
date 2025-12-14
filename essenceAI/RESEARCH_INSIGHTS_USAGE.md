# Research Insights - User Guide

## Overview
The Research Insights feature allows you to query scientific research papers about consumer preferences, market trends, and product acceptance in the plant-based food industry.

## How to Use

### 1. Access the Feature
- Open the app: `streamlit run src/app.py`
- Click on the **"🔬 Research Insights"** tab

### 2. Query Research Papers
The system has access to several scientific papers covering:
- Consumer acceptance of plant-based products
- Fermented plant-based dairy alternatives
- Plant-based meat alternatives
- 3D food printing with plant-based materials
- Food essentialism and consumer perception

### 3. Available Research Papers
Located in the `data/` directory:
- `Cheon_et_al._2025_food_essentialism_perception_plant-based_meat_alternatives.pdf`
- `Flint_et_al._2025_meating_consumer_expectations_plant_based_meat_alternative_products.pdf`
- `Liu_et_al._2025_plant-based_raw_materials_for_3d_food_printing.pdf`
- `Saint-Eve_et_al._2021_preferences_animal_and_plant_protein_sources_compressed.pdf`
- `Ueda_et_al._2025_fermented_plant-based_dairy_alternatives_acceptability.pdf`

### 4. Example Queries
Try asking questions like:
- "What are the key factors affecting consumer acceptance of plant-based meat?"
- "What do consumers think about fermented plant-based dairy products?"
- "What are the barriers to adoption of plant-based alternatives?"
- "How do different consumer segments perceive plant-based products?"
- "What marketing strategies work best for plant-based products?"

### 5. Understanding Results
Each query returns:
- **Answer**: A synthesized response based on the research papers
- **Citations**: Direct quotes from the papers with source information
- **Context**: Relevant sections from the papers that support the answer

## Features

### Rate Limiting
- The system automatically adds 2-second delays between API calls
- This prevents hitting OpenAI rate limits
- You may notice brief pauses during processing - this is normal

### Caching
- Results are cached to avoid redundant API calls
- Subsequent identical queries return instantly
- Cache is stored in `.cache/` directory

### Persistent Storage
- The research index is saved in `.storage/` directory
- First-time setup takes a few minutes to process PDFs
- Subsequent loads are instant (no API calls needed)

## Troubleshooting

### "Failed to load research database" Error
✅ **FIXED**: This error has been resolved. If you still see it:
1. Delete the `.storage/` directory
2. Restart the app
3. The index will rebuild automatically

### Slow Initial Load
- First-time setup processes all PDF files
- This can take 2-5 minutes depending on the number of papers
- Progress is shown in the terminal
- Subsequent loads are instant

### Rate Limit Errors
If you see rate limit warnings:
- The system automatically retries with exponential backoff
- Wait times are logged in the terminal
- Consider reducing the number of PDFs if issues persist

### No Results Found
If queries return no results:
- Try rephrasing your question
- Use more specific terms related to plant-based foods
- Check that PDF files are in the `data/` directory

## Technical Details

### How It Works
1. **Document Loading**: PDFs are loaded and split into chunks
2. **Embedding**: Text chunks are converted to vector embeddings
3. **Indexing**: Embeddings are stored in a searchable index
4. **Querying**: Your question is embedded and matched against the index
5. **Response**: Relevant chunks are sent to GPT-4 for synthesis

### API Usage
- Uses OpenAI's `text-embedding-3-small` model for embeddings
- Uses `gpt-4o-mini` for response generation
- Rate-limited to prevent quota issues
- Optimized for minimal API calls

### Storage
- `.storage/` - Persistent vector index
- `.cache/` - Query result cache
- `data/` - Source PDF files

## Adding New Research Papers

To add new papers:
1. Place PDF files in the `data/` directory
2. Delete the `.storage/` directory
3. Restart the app
4. The index will rebuild with all papers

Supported formats:
- ✅ PDF files
- ✅ Scientific papers
- ✅ Research reports
- ✅ Academic publications

## Best Practices

### For Best Results
1. **Be Specific**: Ask focused questions about specific topics
2. **Use Context**: Mention product types or consumer segments
3. **Check Citations**: Review the source papers for full context
4. **Iterate**: Refine your questions based on initial results

### Performance Tips
1. **First Run**: Allow time for initial index building
2. **Reuse Queries**: Cached results return instantly
3. **Batch Questions**: Ask multiple related questions in one session
4. **Monitor Logs**: Check terminal for rate limit warnings

## Integration with Other Features

### With Competitor Intelligence
- Use research insights to understand market positioning
- Compare competitor claims against scientific evidence
- Identify gaps in competitor messaging

### With Marketing Strategy
- Ground marketing claims in research
- Target specific consumer segments based on research
- Address barriers identified in studies

### With AI Agent Analysis
- Research agent provides scientific backing
- Marketing agent uses insights for strategy
- Competitor agent validates market claims

## Support

### Common Issues
- **Slow queries**: Normal for first-time processing
- **Rate limits**: System handles automatically
- **Missing papers**: Check `data/` directory
- **Cache issues**: Delete `.cache/` to reset

### Getting Help
- Check logs in terminal for detailed error messages
- Review `RESEARCH_INSIGHTS_FIX.md` for technical details
- Ensure all dependencies are installed: `pip install -r requirements.txt`

---

**Status**: ✅ Fully Operational
**Last Updated**: December 2024
