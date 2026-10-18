from pathlib import Path
b=Path(r'E:\CEAESSON WHOLESALE ITEMS\PRODUCT_PHOTOS\_Review')
s=(b/'batch-01'/'complete_batch.py').read_text(encoding='utf-8')
s=s.replace('batch-01','batch-02').replace('Batch 01','Batch 02')
a=s.index("corrections={'0002'")
z=s.index('for row in inventory:',a)
s=s[:a]+s[z:]
(b/'batch-02'/'complete_batch.py').write_text(s,encoding='utf-8')
m=(b/'batch-01'/'mark_reviewed.py').read_text(encoding='utf-8').replace('batch-01','batch-02')
(b/'batch-02'/'mark_reviewed.py').write_text(m,encoding='utf-8')
