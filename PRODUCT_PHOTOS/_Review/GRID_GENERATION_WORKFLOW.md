# One generation, five website crops

User requested one native image per product containing all five styles, then cropping it into five files. This supersedes the earlier five-call approach.

Use a landscape 3-column, 2-row grid with six equal cells and no gutters, separators or panel labels. Reading order: white background; lavender/cream styled background; lifestyle; standalone tight macro of an actual part; promotional with accurate heading; unused blank cell. Request 1536x1024 so square crops can be512x512; inspect actual returned dimensions. Keep each view wholly inside its cell with margin. Full views preserve the complete original product/assortment count, identity, shapes and colours; macro is only a real visible part.

Save the exact prompt in a text file. Immediately preserve the successful native cache and mechanically crop with:

`python PRODUCT_PHOTOS/_Review/save_generated_grid.py --product ID --cache /workspace/generated_images/exec-....png --prompt-file /workspace/prompt.txt`

The helper retains the full grid in Generation_Grids with prompt/source/SHA and crops only missing New files. It never overwrites an existing output. Review original photographs, whole grid, and resulting actual crops. Mark each crop checked only after its boundaries, correct style, product count/identity/colour and legibility are acceptable. Keep original baselines byte-identical. Keep folders-0 until allfive expected outputs are checked and original+savedhashes match. Source-grid records are not standalone website views; their checkedfalse field is expected.

Preserve valid existing single-view images. For a materially failed crop, allow at most one targeted correction for that failed view if none was already spent; retain rejection. Do not retry minor cosmetic variations, or spent corrections. Stop globally on hard nativequota; drain and save successful in-flight outputs.
