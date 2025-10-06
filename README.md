# About

This is a code repository for **Modified version of the SPOC** (Structure Prediction and Omics informed Classifier), a random forest classifier designed to evaluate AlphaFold-Multimer (AF-M v2.3, custom version running on the Little Beast server) iutputted on the custom version on server little beast of binary human protein pairs to assess their structural plausibility and consistency with experimental omics data.

For more information, please see the associated publication: Predictomes, A classifier-curated database of AlphaFold-modeled protein-protein interactions

This code was developed and tested on a Linux system.

**Link to orginal repo:** https://github.com/walterlab-HMS/SPOC

# Changes in the Modified SPOC
1. Changed method for retrieving complex names
The original classifier extracts the complex name from the file name of the AF-M outpu files. However, the AF-M implementation on Little Beast server does not follow the default naming convention, hence, the modified version of SPOC retrieves the complex name by concatenating the protein IDs in the chain_id_map.json file located in the msas folder of the AF-M output.

2. Changed path to extract AF-M metrics
In the original classifier, the pTM, ipTM, and PAE scores were extracted from JSON files in the AF-M output. However, in the AF-M implementation on Little Beast, only the PAE files were available in JSON file. After minor adjustments (such as updating the PAE score indices) and adding functions to extract pTM and ipTM values from the pickle files of randomly selected models, all required AF-M metrics (pTM, ipTM, and PAE) were successfully retrieved and used for the SPOC score calculation.

3. Other minor changes

 - Modified classifier output file paths so that all SPOC output CSV files are stored in a dedicated folder.

 - Improved the random selection process for choosing 3 out of 5 models. If needed, users can now set a fixed random seed to ensure reproducibility of the SPOC algorithm results.

# Using SPOC on Little_beast
## Step 1: Creating the environment
1. Nagivate to the SPOC directory
```bash
cd /mnt/scratch/SPOC
```
2. Create a personal Conda environment in your home
```bash
conda env create -f environment.yml -n <user_name>_spoc_venv
```
## Step 2: Using SPOC
Navigate to your home directory or directory where you want to output folder (which contains output files) to be saved
1. Activate the spoc environment
```bash
conda activate <username>_spoc_venv
```
2. Run SPOC
```bash
python3 /mnt/scratch/SPOC/run.py /mnt/storage/<user_name>/<path>/<afm_output_folder>
```

--- 

# Using SPOC on Linux
## Cloning the Repository

To clone the SPOC repository, use the following command:

```bash
git clone https://github.com/LaCava-Lab/SPOC
```
or
```bash
git clone git@github.com:LaCava-Lab/SPOC.git
```

Navigate into the cloned directory:

```bash
cd SPOC
```


## Step 1: Install Miniconda (if conda is not already installed)

1. **Download Miniconda:**

   ```bash
   wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
   ```

2. **Install Miniconda:**

   ```bash
   bash Miniconda3-latest-Linux-x86_64.sh
   ```

   Follow the on-screen instructions and accept the default options.

3. **Initialize Conda (if not done automatically):**

   ```bash
   source ~/.bashrc
   ```

4. **Verify the installation:**

   ```bash
   conda --version
   ```

---

## Step 2: Create SPOC Conda Environment to Load Necessary Dependencies

1. **Create the environment (while in SPOC directory):**

   ```bash
   conda env create -f environment.yml
   ```

2. **Activate the SPOC environment:**

   ```bash
   conda activate spoc_venv
   ```

---

## Step 3: Run SPOC to Analyze Predictions

SPOC is trained specifically to analyze complexes containing pairs of human proteins run in at least three AlphaFold-Multimer models. The program will ignore any complexes that do not meet the above criteria. The program will attempt to use all available CPUs in parallel to minimize runtime. The program does not require specific file naming formats (besides the words unrelaxed and the alphafold model number used in the filename), as it extracts sequences from the PDB files directly to determine which proteins are in which files and uses Protein BLAST to match sequences to UniProt IDs.

```
Example folder

my_afm_predictions_folder/
│-- DONS_HUMAN__MCM3_HUMAN__1374aa.a3m.xz
│-- DONS_HUMAN__MCM3_HUMAN__1374aa_scores_rank_001_alphafold2_multimer_v3_model_1_seed_000.json.xz
│-- DONS_HUMAN__MCM3_HUMAN__1374aa_scores_rank_002_alphafold2_multimer_v3_model_2_seed_000.json.xz
│-- DONS_HUMAN__MCM3_HUMAN__1374aa_scores_rank_003_alphafold2_multimer_v3_model_4_seed_000.json.xz
│-- DONS_HUMAN__MCM3_HUMAN__1374aa_unrelaxed_rank_001_alphafold2_multimer_v3_model_1_seed_000.pdb.xz
│-- DONS_HUMAN__MCM3_HUMAN__1374aa_unrelaxed_rank_002_alphafold2_multimer_v3_model_2_seed_000.pdb.xz
│-- DONS_HUMAN__MCM3_HUMAN__1374aa_unrelaxed_rank_003_alphafold2_multimer_v3_model_4_seed_000.pdb.xz

```
### To run single complex saved in one folder:
```bash
python3 run.py my_afm_predictions_folder
```
### To run multiple complexes, each in one folder:
```bash
python3 run.py my_afm_predictions_folder_1 my_afm_predictions_folder_2 my_afm_predictions_folder_3 .....
```
### To run folder/complexes with wildcard or numbered files/folders:
```bash
python3 run.py my_afm_predictions_folder_0?
```
### To run multiple folders/complexes with wildcard and optional filters:
```bash
python3 run.py my_afm_predictions_folder_0? --name_filter MCM --output only_mcm_complexes
```

See all available options by running:

```bash
python3 run.py --help
```

---

## Step 4: Understanding SPOC Outputs

After running SPOC, the output files will be generated in the location where you initiated the run script.

1. **{your_analyzed_folder}_SPOC_analysis.csv**

   This file provides a summary of analyzed predictions, including key metrics such as SPOC and other measurements of predicted structural accuracy and omic data linking the proteins in analyzed pairs.

   **Columns explanation:**
   - `complex_name`: Name of the analyzed protein complex.
   - `spoc_score`: Overall SPOC confidence score. 1 is best and 0 is worst. The higher the better.
   - `avg_n_models`: Average number of models for all inter-residue conacts found in the analysis. Normalized by number of models run (Always 3 for SPOC). 1 is best and 0 is worst.
   - `max_n_models`: Maximum number of models for all inter-residue conacts found in the analysis. Normalized by number of models run (Always 3 for SPOC). 1 is best and 0 is worst.
   - `num_contacts_with_max_n_models`: Number of contacts observed in the most models across all those analyzed.
   - `num_unique_contacts`: Total unique residue contacts found across all analyzed models.
   - `mean_contacts_across_predictions`: Mean number of contacts found across all analyzed models.
   - `min_contacts_across_predictions`: Minimum number of contacts observed across all analyzed models.
   - `iptm_mean`: Mean interface predicted template modeling score across all analyzed models.
   - `iptm_min`: Minimum interface predicted template modeling score across all analyzed models.
   - `iptm_max`: Maximum interface predicted template modeling score across all analyzed models.
   - `models_checked`: IDs of models that were processed. If more than 3 models are available, the program will randomlly choose 3.
   - `uniprot_ids`: UniProt IDs that were matched to the protein sequyences found in the file for the given complex.
   - `sequence`: Protein sequences extracted from the PDB file associated with the given complex.
   - `best_num_residue_contacts`: Number of contacts (residue pairs) found at the protein-protein interface in the single "best" model.
   - `best_if_residues`: Best number of interacting residues found in the protein-protein interface in the single "best" model.
   - `best_plddt_max`: Maximum predicted Local Distance Difference Test (pLDDT) score for any residue found in the protein-protein interface in the single "best" model.
   - `best_pae_min`: Minimum Predicted Aligned Error (PAE) score across all residue pairs in the protein-protein interface of the single "best" model.
   - `best_contact_score_max`: Maximum score for predicted contacts in the single "best" model.
   - `best_num_significant_afm_scores`: Best number of significant AlphaMissense scores (> 80) for residues at the protein-protein interface in the single "best" model.
   - `crispr_jaccard`: Jaccard similarity score for CRISPR data.
   - `crispr_shared_hit_count`: Count of shared CRISPR hits for both proteins in the analyzed pair.
   - `co_expression_score`: Score indicating co-expression pattern (from CoExpressDB) for both proteins in the analyzed pair.
   - `t5_embedding_cosine_dist`: Cosine distance between T5 embeddings for both proteins in the analyzed pair.
   - `t5_embedding_euclidian_dist`: Euclidean distance between T5 embeddings for both proteins in the analyzed pair.
   - `depmap_cosine_dist`: Cosine distance in DepMap data for both proteins in the analyzed pair.
   - `depmap_euclidian_dist`: Euclidean distance in DepMap data for both proteins in the analyzed pair.
   - `depmap_abs_diff`: Absolute difference in DepMap values for both proteins in the analyzed pair.
   - `colocalization_match_score`: Score indicating how well the predicted DeepLoc 2.0 localization vectors match for both proteins in the analyzed pair.
   - `biogrid_detect_count`: Number of times an interaction between the analyzed proteins in the pair was detected in BioGRID.

   Any complexes that could not be analyzed in the specified folder will be listed in a new document: **{your_analyzed_folder}_errored_complexes.csv**

---

## Additional Notes

- Ensure that the input AlphaFold multimer models are in the correct format (.pdb files) and that they have corresponding JSON PAE files.
- If you encounter any errors, check the console output to help debug any issues.

---









