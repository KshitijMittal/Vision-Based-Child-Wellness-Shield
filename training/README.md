# training/

Python training scripts and dataset preparation for the on-device models.

**Phase 1 status:** placeholder — nothing to run yet.

Per the Implementation Plan (§6.1, parallel track), training starts in Phase 2:

- `train_jaundice.py` — first model (Kaggle ~600+ validated images)
- `train_pallor.py`, `train_skin.py`, `train_goitre.py`, `train_malnutrition.py`
- `train_bmi.py` — height/weight estimator (depends on MediaPipe pose landmarks)
- `datasets/` — seeded + field-collected data (TRD §7.3)

**Training runs on free cloud GPUs** (Google Colab T4 / Kaggle), not this
machine — see TRD §7. This repo only holds scripts and dataset prep.
