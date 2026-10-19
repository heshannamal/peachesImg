# Continue the product-photo run

Latest scope: generate five images for each of the remaining25 products listed in `REMAINING25.json`. The earlier twelve partials are complete and uploaded. Do not process outside the original100 queue.

The original run targets **100 products**, IDs **0053–0152**, five new images per product. Existing originals must remain untouched. The user prefers clear website-ready photos and accepts minor cosmetic or tiny typography imperfections; do not spend extra generations polishing those.

Read `products.json` and `RUN_100_PROGRESS.json`, then inspect the actual product folders. `RUN_100.json` is the starting queue, so its embedded product statuses are historical. Folder names can misidentify the photographed item: inspect the originals before writing prompts.

- `Originals/`: source photos, never overwrite or edit.
- `New/`: immediately saved generated photos. Resume missing images; do not regenerate existing successful images.
- Five views: `01_White-Background.png`, `02_Styled-Background.png`, `03_Lifestyle.png`, `04_Detail.png`, `05_Promotional.png`.
- Treat each whole assortment as one product. Preserve visible product count, shape, colour and identity; remove shop/hand/old price overlays.
- Record each output, prompt, SHA256 and honest visual review in `GENERATION_NOTES.json` as soon as saved.
- `-0` stays pending or partial. Rename to `-1` only after five new images are saved and visually checked and originals are verified unchanged.

`save_generated.py` preserves a result immediately with `--product`, `--variant` (without extension), `--cache` and `--prompt`. Its new record starts unchecked; review the actual image before setting `checked: true`.

After processing, run `python PRODUCT_PHOTOS/_Review/reconcile_run_100.py` from the repository root to update the main inventory and progress checkpoint. Run `backup_run_100.py` from the same directory to archive each next ten completed products.

Downloadable backup ZIPs are in `/workspace/product-photo-backups`. Generation-cache originals are in `/workspace/generated_images`; keep them until their product copies are confirmed. Some cache files are rejected attempts, so inspect unmatched files before using them.

The stopped checkpoint (354 generated images) and CSV batches04–07 were pushed to GitHub main and all315 CSV links verified. Resumed outputs must be committed and pushed after completion.

If a usage limit occurs, save every successful in-flight output, retain partial folders, and record the blocker. Do not claim the batch is complete or keep retrying a confirmed hard quota.
